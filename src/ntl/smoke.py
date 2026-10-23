"""G1a vertical slice and optional G1b profile. Local success is not Kaggle proof."""
from __future__ import annotations

import sys
import time
from pathlib import Path

import joblib
import pandas as pd

from .common import digest, environment, identity, source_revision, write_json
from .data import load_development, read_csv
from .inference import build_submission, independent_contract, load_model, write_submission
from .models import fit_model
from .runtime import is_kaggle, offline, peak_memory


def cpu_smoke(root: Path, test: Path, output: Path, *, available_memory: int,
              limit_seconds: float = 32400, cold_restart: bool = False) -> dict:
    revision = source_revision()
    if output.exists():
        raise ValueError("Preserve previous smoke attempts")
    output.mkdir(parents=True)
    start = time.perf_counter()
    with offline():
        frame = load_development(root)
        model = fit_model(frame.text.tolist(), frame.model.tolist(), {"architecture": "S", "C": 2})
        joblib.dump(model, output / "smoke.joblib")
        restored = load_model(output / "smoke.joblib", digest(output / "smoke.joblib"))
        contract = independent_contract(restored, ["", " ", "NA", "数学 — code ```x=1```", "long " * 1000])
        runtime_test = read_csv(test, ["id", "text"])
        write_submission(output / "submission.parquet", build_submission(runtime_test, restored))
        timings = {}
        for n in (0, 1, 3, 4000, 8000):
            synthetic = pd.DataFrame({"id": [f"synthetic-{i}" for i in range(n)],
                                      "text": ["Runtime workload text. " * 274 for _ in range(n)]}, dtype="string")
            before = time.perf_counter()
            write_submission(output / f"scale-{n}.parquet", build_submission(synthetic, restored))
            timings[str(n)] = time.perf_counter() - before
        if "torch" in sys.modules or "transformers" in sys.modules:
            raise ValueError("CPU submission path imported optional neural packages")
    wall, memory = time.perf_counter() - start, peak_memory()
    target = is_kaggle() and cold_restart
    passed = target and memory < .8 * available_memory and wall < .7 * limit_seconds
    evidence = {"gate": "G1a", "status": "passed" if passed else "blocked", "kaggle": is_kaggle(),
                "internet_disabled": True, "cold_restart": cold_restart, "independent_contract": True,
                "parquet_roundtrip": True, "development_manifest_hash": digest(root / "manifest.json"),
                "environment": environment(), "source_revision": revision, "wall_seconds": wall,
                "peak_memory_bytes": memory, "available_memory_bytes": available_memory,
                "limit_seconds": limit_seconds, "inference_seconds": timings["4000"], "scale_seconds": timings,
                "contract": contract, "files": {p.name: digest(p) for p in output.iterdir() if p.is_file()},
                "reason": None if passed else "Requires cold Kaggle replay and measured resource reserves"}
    write_json(output / "G1a.json", evidence, exclusive=True)
    if passed:
        relative = output.resolve().relative_to(root.resolve())
        accepted = {**evidence, "files": {(relative / name).as_posix(): value for name, value in evidence["files"].items()}}
        write_json(root / "G1a.json", accepted, exclusive=True)
    return evidence


def neural_smoke(root: Path, encoder, output: Path, *, available_memory: int, limit_seconds: float,
                 cold_restart: bool = False) -> dict:
    from .gates import require_gate
    from .protocol import registered
    require_gate(root / "G1a.json", "G1a", digest(root / "manifest.json"))
    protocol = registered(root)
    if protocol["encoder"]["revision"] != encoder.manifest["revision"]:
        raise ValueError("Register the exact checkpoint before extracting embeddings")
    revision = source_revision()
    if output.exists():
        raise ValueError("Preserve previous encoder attempts")
    output.mkdir(parents=True)
    start = time.perf_counter()
    with offline():
        frame = load_development(root)
        vectors = encoder.cache(frame, output / "cache", view="raw", allowed_ids=set(frame.id))
        import numpy as np
        np.save(output / "development_embeddings.npy", vectors, allow_pickle=False)
        sample = frame.text.iloc[:5].tolist() + ["", "long " * 1000]
        reference = encoder.encode(sample)
        for i, text in enumerate(sample):
            np.testing.assert_allclose(encoder.encode([text])[0], reference[i], atol=1e-5, rtol=1e-4)
        model = fit_model(frame.text.tolist(), frame.model.tolist(), {"architecture": "F", "C": 2}, encoder=encoder)
        independent_contract(model, sample)
        test = pd.DataFrame({"id": [str(i) for i in range(len(sample))], "text": sample}, dtype="string")
        before = time.perf_counter()
        write_submission(output / "submission.parquet", build_submission(test, model))
        inference = (time.perf_counter() - before) * 4000 / len(sample)
    wall, memory = time.perf_counter()-start, peak_memory()
    gpu = None
    if encoder.device != "cpu":
        import importlib
        torch = importlib.import_module("torch")
        gpu = {"peak_bytes": torch.cuda.max_memory_allocated(), "total_bytes": torch.cuda.get_device_properties(encoder.device).total_memory}
    safe = memory < .8 * available_memory and inference < .7 * limit_seconds
    if gpu:
        safe = safe and gpu["peak_bytes"] < .8 * gpu["total_bytes"]
    evidence = {"gate": "G1b", "status": "passed" if is_kaggle() and cold_restart and safe else "blocked",
                "kaggle": is_kaggle(), "cold_restart": cold_restart, "internet_disabled": True,
                "independent_contract": True, "parquet_roundtrip": True, "encoder_hash": identity(encoder.manifest),
                "development_manifest_hash": digest(root / "manifest.json"), "source_revision": revision,
                "environment": environment(), "wall_seconds": wall, "peak_memory_bytes": memory,
                "available_memory_bytes": available_memory, "limit_seconds": limit_seconds,
                "inference_seconds": inference, "gpu": gpu,
                "files": {p.relative_to(output).as_posix(): digest(p) for p in output.rglob("*") if p.is_file()}}
    write_json(output / "G1b.json", evidence, exclusive=True)
    return evidence
