"""Exact post-confirmation refit, local bundle and cold offline replay."""
from __future__ import annotations

import shutil
import time
import uuid
import contextlib
from pathlib import Path

import joblib

from .common import digest, environment, read_json, source_revision, verify_files, write_json, code_files, record
from .data import TRAIN_COLUMNS, check_source, read_csv
from .inference import build_submission, independent_contract, load_model, write_submission, model_encoder
from .locked_eval import verify_decision
from .models import fit_model
from .runtime import is_kaggle, offline, peak_memory, gpu_memory
from .resources import VERSION, validate_budgets, target_reasons
from .capacity import profile_capacity, verify_capacity
from .provenance import execution, assert_execution, artifact_execution, verify_roles
from .schema import load_contract


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
        encoder.preflight()
        shutil.copytree(encoder.assets, output / "encoder")
        encoder.rebind(output / "encoder")
        encoder.preflight()
    start = time.perf_counter()
    if task_artifacts_permitted:
        model = fit_model(frame.text.tolist(), frame.model.tolist(), decision["config"], encoder=encoder)
        assert_execution(decision["artifact_execution"]["selected"], artifact_execution(model))
        if encoder is not None:
            encoder.assets = Path("encoder")
        joblib.dump(model, output / "model.joblib")
    else:
        # The full source is eligible here only because G5 has closed. The
        # submission notebook executes this one fixed recipe, never selection.
        shutil.copy2(source, output / "train.csv")
    shutil.copytree(Path(__file__).parent, output / "source" / "ntl", ignore=shutil.ignore_patterns("__pycache__"))
    source_root = Path(__file__).resolve().parents[2]
    for name in code_files():
        if name.startswith("src/ntl/"):
            continue
        target = output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_root / name, target)
    write_json(output / "submission_schema.json", load_contract(root))
    frame[["id", "text"]].to_csv(output / "profile_inputs.csv", index=False)
    shutil.copy2(decision_dir / "decision.json", output / "decision.json")
    shutil.copy2(sealed / "confirmation.json", output / "confirmation.json")
    write_json(output / "refit_manifest.json", {**verify_roles(decision), "development_manifest_hash": digest(root / "manifest.json"), "source_revision": source_revision(), "environment": environment(),
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
    validate_budgets(available_memory, limit_seconds)
    # Never delete or overwrite another attempt's submission/evidence.
    if any((output / name).exists() for name in ("submission.parquet", "release_manifest.json", "attempt.json")):
        raise ValueError("Existing release output/evidence requires explicit reconciliation; use a fresh directory")
    output.mkdir(parents=True, exist_ok=True)
    attempt = uuid.uuid4().hex
    write_json(output / "attempt.json", {"id": attempt, "state": "reserved"}, exclusive=True)
    candidate = output / f"candidate-{attempt}.parquet"
    final = output / "submission.parquet"
    published = False
    output_hash = None
    try:
        manifest = read_json(bundle / "refit_manifest.json")
        roles = verify_roles(manifest)
        verify_files(bundle, manifest["files"])
        contract = load_contract(bundle)
        with offline():
            encoder = None
            if manifest["config"]["architecture"] != "S":
                from .encoder import FrozenEncoder
                encoder = FrozenEncoder(bundle / "encoder", **manifest["encoder_runtime"])
            current = execution(encoder)
            assert_execution(manifest.get("execution", {}), current)
            gpu_memory(encoder.device if encoder is not None else "cpu", reset=True)
            frozen = read_json(bundle / "decision.json")
            if digest(bundle / "decision.json") != manifest["decision_sha256"] or digest(bundle / "confirmation.json") != manifest["G5_sha256"]:
                raise ValueError("Release decision/confirmation identity drift")
            if verify_roles(frozen) != roles:
                raise ValueError("Release role envelope differs from decision")
            if frozen["submission_schema"] != contract:
                raise ValueError("Release submission schema differs from decision")
            if frozen["config"] != manifest["config"] or frozen["execution"] != current:
                raise ValueError("Release recipe or provenance differs from decision")
            if manifest["mode"] == "attached-model":
                model = load_model(bundle / "model.joblib", manifest["files"]["model.joblib"])
                restored_encoder = model_encoder(model)
                if restored_encoder is not None:
                    restored_encoder.rebind(bundle / "encoder")
                    if encoder is None or restored_encoder.manifest != encoder.manifest:
                        raise ValueError("Attached encoder identity drift")
            elif manifest["mode"] == "fixed-refit":
                training = read_csv(bundle / "train.csv", TRAIN_COLUMNS)
                if training.id.tolist() != manifest["training_ids"] or digest(bundle / "train.csv") != manifest["source_hash"]:
                    raise ValueError("Notebook training membership drift")
                model = fit_model(training.text.tolist(), training.model.tolist(), manifest["config"], encoder=encoder)
            else:
                raise ValueError("Unregistered release mode")
            if model.config != manifest["config"]:
                raise ValueError("Refit recipe drift")
            assert_execution(roles["artifact_execution"]["selected"], artifact_execution(model))
            independent_contract(model, ["", " ", "NA", "Unicode — 数学", "code ```x=1```", "worst-case " * 1000])
            frame = read_csv(test, ["id", "text"])
            write_submission(candidate, build_submission(frame, model), contract)
            output_hash = digest(candidate)
            profile_inputs = read_csv(bundle / "profile_inputs.csv", ["id", "text"])
            if profile_inputs.id.tolist() != manifest["training_ids"]:
                raise ValueError("Release capacity source membership drift")
            capacity = profile_capacity(profile_inputs, model, output, contract,
                allowed_ids=set(manifest["training_ids"]), manifest_hash=manifest["development_manifest_hash"],
                role="post-confirmation-full-data")
        evidence = {"resource_version": VERSION, "gate": "G6", "attempt_id": attempt,
            "execution": current, "development_manifest_hash": manifest["development_manifest_hash"],
            "kaggle": is_kaggle(), "internet_disabled": True, "cold_restart": cold_restart,
            "independent_contract": True, "parquet_roundtrip": True,
            "peak_memory_bytes": peak_memory(), "available_memory_bytes": available_memory,
            "limit_seconds": limit_seconds, "scale_seconds": capacity["scale_seconds"], "capacity": capacity,
            "inference_seconds": capacity["scale_seconds"]["4000"],
            "gpu": gpu_memory(encoder.device if encoder is not None else "cpu"), "environment": environment(),
            "source_revision": manifest["source_revision"], "refit_manifest_sha256": digest(bundle / "refit_manifest.json"),
            "decision_sha256": manifest["decision_sha256"], "G5_sha256": manifest["G5_sha256"],
            "test_hash": digest(test), "rows": len(frame), "files": {**capacity["files"], candidate.name: output_hash}}
        evidence["wall_seconds"] = time.perf_counter()-start
        verify_capacity(evidence)
        reasons = target_reasons(evidence)
        evidence.update(status="blocked" if reasons else "passed", reasons=reasons)
        if not reasons:
            # Atomic rename is on the same filesystem. The attempt reservation excludes
            # concurrent cooperating writers; refuse unexpected output rather than replace it.
            if final.exists():
                raise ValueError("Unexpected final output appeared during replay")
            candidate.rename(final)
            published = True
            evidence["files"] = {**capacity["files"], final.name: output_hash}
        write_json(output / "release_manifest.json", evidence, exclusive=True)
        return evidence
    except Exception as error:
        cleanup_error = None
        if published:
            try:
                if final.exists() and digest(final) == output_hash:
                    final.rename(candidate)
            except Exception as cleanup:
                cleanup_error = str(cleanup)
        incident = {"gate": "G6", "status": "failed", "attempt_id": attempt, "reason": str(error), "cleanup_error": cleanup_error}
        with contextlib.suppress(Exception):
            record(output / "incidents.jsonl", **incident)
            if not (output / "release_manifest.json").exists():
                write_json(output / "release_manifest.json", incident, exclusive=True)
        raise


def require_release(report: dict) -> None:
    if report.get("status") != "passed":
        raise RuntimeError(f"Release blocked: {report.get('reasons', report.get('reason', 'G6 incomplete'))}")
