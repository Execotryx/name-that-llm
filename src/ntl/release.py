"""Exact post-confirmation refit, local bundle and cold offline replay."""
from __future__ import annotations

import shutil
import time
from pathlib import Path

import joblib

from .common import digest, environment, read_json, source_revision, verify_files, write_json
from .data import TRAIN_COLUMNS, check_source, read_csv
from .inference import build_submission, independent_contract, load_model, write_submission
from .locked_eval import verify_decision
from .models import fit_model
from .runtime import is_kaggle, offline, peak_memory


def refit(root: Path, sealed: Path, decision_dir: Path, receipt: Path, source: Path, output: Path,
          *, task_artifacts_permitted: bool) -> None:
    decision = verify_decision(root, decision_dir, receipt)
    ledger = read_json(sealed / "consumption_ledger.json")
    if (ledger["state"] != "closed" or ledger["decision_sha256"] != digest(decision_dir / "decision.json")
            or ledger["confirmation_sha256"] != digest(sealed / "confirmation.json")):
        raise ValueError("G5 must be closed for this exact decision")
    if output.exists():
        raise ValueError("Preserve existing release bundle")
    check_source(source, decision["source_hash"], output.parent / "refit-source-discrepancy.json")
    frame = read_csv(source, TRAIN_COLUMNS)
    manifest = read_json(root / "manifest.json")
    if len(frame) != 2699 or set(frame.id) != set(manifest["development_ids"] + manifest["locked_ids"]):
        raise ValueError("Final refit must retain every original row")
    encoder = None
    if decision["architecture"] != "S":
        selected = load_model(decision_dir / "selected.joblib", decision["artifacts"]["selected"]["sha256"])
        encoder = selected.frozen.encoder if decision["architecture"] == "H" else selected.encoder
    output.mkdir(parents=True)
    if encoder is not None:
        shutil.copytree(encoder.assets, output / "encoder")
        encoder.assets = (output / "encoder").resolve()
    start = time.perf_counter()
    if task_artifacts_permitted:
        model = fit_model(frame.text.tolist(), frame.model.tolist(), decision["config"], encoder=encoder)
        if encoder is not None:
            encoder.assets = Path("encoder")
        joblib.dump(model, output / "model.joblib")
    else:
        # The full source is eligible here only because G5 has closed. The
        # submission notebook executes this one fixed recipe, never selection.
        shutil.copy2(source, output / "train.csv")
    shutil.copytree(Path(__file__).parent, output / "source" / "ntl", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copy2(decision_dir / "decision.json", output / "decision.json")
    shutil.copy2(sealed / "confirmation.json", output / "confirmation.json")
    write_json(output / "refit_manifest.json", {"source_revision": source_revision(), "environment": environment(),
               "config": decision["config"], "classes": decision["classes"], "training_ids": frame.id.tolist(),
               "mode": "attached-model" if task_artifacts_permitted else "fixed-refit",
               "encoder_runtime": {"batch_size": encoder.batch_size, "device": encoder.device} if encoder else None,
               "rows": len(frame), "source_hash": digest(source), "refit_seconds": time.perf_counter()-start,
               "decision_sha256": digest(decision_dir / "decision.json"), "G5_sha256": digest(sealed / "confirmation.json"),
               "files": {p.relative_to(output).as_posix(): digest(p) for p in output.rglob("*") if p.is_file()},
               "claim": "Full-data refit inherits the evaluated recipe; no new independent score"}, exclusive=True)


def replay(bundle: Path, test: Path, output: Path, *, available_memory: int,
           limit_seconds: float = 32400, cold_restart: bool = False) -> dict:
    start = time.perf_counter()
    if available_memory <= 0 or limit_seconds <= 0:
        raise ValueError("Positive measured runtime budgets are required")
    if (output / "release_manifest.json").exists():
        raise ValueError("Preserve previous replay evidence")
    manifest = read_json(bundle / "refit_manifest.json")
    verify_files(bundle, manifest["files"])
    if environment()["packages"] != manifest["environment"]["packages"] or environment()["python"] != manifest["environment"]["python"]:
        raise ValueError("Release environment differs from tested lock")
    output.mkdir(parents=True, exist_ok=True)
    with offline():
        if manifest["mode"] == "attached-model":
            model = load_model(bundle / "model.joblib", manifest["files"]["model.joblib"])
        elif manifest["mode"] == "fixed-refit":
            training = read_csv(bundle / "train.csv", TRAIN_COLUMNS)
            if training.id.tolist() != manifest["training_ids"] or digest(bundle / "train.csv") != manifest["source_hash"]:
                raise ValueError("Notebook training membership drift")
            encoder = None
            if manifest["config"]["architecture"] != "S":
                from .encoder import FrozenEncoder
                encoder = FrozenEncoder(bundle / "encoder", **manifest["encoder_runtime"])
            model = fit_model(training.text.tolist(), training.model.tolist(), manifest["config"], encoder=encoder)
        else:
            raise ValueError("Unregistered release mode")
        if model.config != manifest["config"]:
            raise ValueError("Refit recipe drift")
        # Resolve portable local encoder paths after moving the bundle.
        encoder = model.frozen.encoder if model.config["architecture"] == "H" else model.encoder
        if encoder is not None:
            encoder.assets = (bundle / "encoder").resolve()
        independent_contract(model, ["", " ", "NA", "Unicode — 数学", "code ```x=1```", "worst-case " * 1000])
        frame = read_csv(test, ["id", "text"])
        write_submission(output / "submission.parquet", build_submission(frame, model))
        timing = {}
        import pandas as pd
        for n in (0, 1, 3, 4000, 8000):
            fixture = pd.DataFrame({"id": [str(i) for i in range(n)], "text": ["long workload " * 274] * n}, dtype="string")
            before = time.perf_counter()
            build_submission(fixture, model)
            timing[str(n)] = time.perf_counter()-before
    wall, memory = time.perf_counter()-start, peak_memory()
    passed = is_kaggle() and cold_restart and wall < .7*limit_seconds and memory < .8*available_memory
    evidence = {"gate": "G6", "status": "passed" if passed else "blocked", "kaggle": is_kaggle(),
                "internet_disabled": True, "cold_restart": cold_restart, "independent_contract": True, "parquet_roundtrip": True,
                "wall_seconds": wall, "peak_memory_bytes": memory, "available_memory_bytes": available_memory,
                "limit_seconds": limit_seconds, "scale_seconds": timing, "environment": environment(),
                "source_revision": manifest["source_revision"], "refit_manifest_sha256": digest(bundle / "refit_manifest.json"),
                "test_hash": digest(test), "rows": len(frame), "files": {"submission.parquet": digest(output / "submission.parquet")}}
    write_json(output / "release_manifest.json", evidence, exclusive=True)
    return evidence
