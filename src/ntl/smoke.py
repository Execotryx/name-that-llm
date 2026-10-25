"""G1 vertical slices with measured development-only capacity, never scores."""
from __future__ import annotations

import sys
import contextlib
import time
from pathlib import Path

import joblib
import numpy as np

from .capacity import profile_capacity, verify_capacity
from .common import digest, environment, identity, read_json, source_revision, write_json, record
from .data import load_development, read_csv
from .inference import build_submission, independent_contract, load_model, write_submission
from .models import fit_model
from .runtime import is_kaggle, offline, peak_memory, gpu_memory
from .resources import VERSION, validate_budgets, target_reasons
from .schema import load_contract
from .provenance import execution


@contextlib.contextmanager
def _attempt(output: Path, gate: str):
    if output.exists():
        raise ValueError("Preserve previous smoke attempts")
    output.mkdir(parents=True)
    try:
        yield
    except Exception as error:
        # Failed/OOM attempts retain partial files and cannot become eligibility.
        with contextlib.suppress(Exception):
            record(output / "incidents.jsonl", gate=gate, status="blocked", reason=str(error))
            if not (output / f"{gate}.json").exists():
                write_json(output / f"{gate}.json", {"gate": gate, "status": "blocked",
                    "reason": str(error), "scope": "incomplete smoke; revalidation in a fresh attempt required"}, exclusive=True)
        raise


def _evidence(root, output, capacity, *, start, available_memory, limit_seconds,
              cold_restart, revision, phases, encoder=None) -> dict:
    evidence = {"resource_version": VERSION, "execution": execution(encoder),
                "gate": "G1b" if encoder is not None else "G1a",
                "kaggle": is_kaggle(), "internet_disabled": True, "cold_restart": cold_restart,
                "independent_contract": True, "parquet_roundtrip": True,
                "development_manifest_hash": digest(root / "manifest.json"),
                "environment": environment(), "source_revision": revision,
                "phase_seconds": phases,
                "peak_memory_bytes": peak_memory(), "available_memory_bytes": available_memory,
                "limit_seconds": limit_seconds, "inference_seconds": capacity["scale_seconds"]["4000"],
                "scale_seconds": capacity["scale_seconds"], "capacity": capacity,
                "gpu": gpu_memory(encoder.device) if encoder is not None else None,
                "files": {p.relative_to(output).as_posix(): digest(p) for p in output.rglob("*") if p.is_file()}}
    # Include profiling, dependency/asset verification and evidence-file hashing.
    evidence["wall_seconds"] = time.perf_counter() - start
    verify_capacity(evidence)
    reasons = target_reasons(evidence)
    return {**evidence, "status": "blocked" if reasons else "passed", "reasons": reasons}


def cpu_smoke(root: Path, test: Path, output: Path, *, available_memory: int,
              limit_seconds: float = 32400, cold_restart: bool = False) -> dict:
    validate_budgets(available_memory, limit_seconds)
    revision = source_revision()
    # Accepted G1a paths are relative to the protocol root. Check before fitting.
    relative = output.resolve().relative_to(root.resolve())
    if (root / "G1a.json").exists():
        raise ValueError("Preserve the existing accepted G1a; explicitly revalidate in a new protocol root")
    with _attempt(output, "G1a"):
        contract_schema = load_contract(root)
        start = time.perf_counter()
        with offline():
            frame = load_development(root)
            before = time.perf_counter()
            model = fit_model(frame.text.tolist(), frame.model.tolist(), {"architecture": "S", "C": 2})
            phases = {"fit": time.perf_counter() - before}
            joblib.dump(model, output / "smoke.joblib")
            before = time.perf_counter()
            restored = load_model(output / "smoke.joblib", digest(output / "smoke.joblib"))
            phases["restore"] = time.perf_counter() - before
            contract = independent_contract(restored, ["", " ", "NA", "数学 — code ```x=1```", "long " * 1000])
            runtime_test = read_csv(test, ["id", "text"])
            write_submission(output / "submission.parquet", build_submission(runtime_test, restored), contract_schema)
            capacity = profile_capacity(frame, restored, output, contract_schema,
                                        allowed_ids=set(read_json(root / "manifest.json")["development_ids"]),
                                        manifest_hash=digest(root / "manifest.json"))
            if "torch" in sys.modules or "transformers" in sys.modules:
                raise ValueError("CPU submission path imported optional neural packages")
        evidence = _evidence(root, output, capacity, start=start, available_memory=available_memory,
                             limit_seconds=limit_seconds, cold_restart=cold_restart, revision=revision, phases=phases)
        evidence["contract"] = contract
        write_json(output / "G1a.json", evidence, exclusive=True)
        if evidence["status"] == "passed":
            accepted = {**evidence,
                        "files": {(relative / n).as_posix(): h for n, h in evidence["files"].items()},
                        "capacity": {**capacity, "files": {(relative / n).as_posix(): h for n, h in capacity["files"].items()}}}
            write_json(root / "G1a.json", accepted, exclusive=True)
        return evidence


def neural_smoke(root: Path, encoder, output: Path, *, available_memory: int, limit_seconds: float,
                 cold_restart: bool = False) -> dict:
    from .gates import require_gate
    from .protocol import registered
    validate_budgets(available_memory, limit_seconds)
    require_gate(root / "G1a.json", "G1a", digest(root / "manifest.json"))
    protocol = registered(root)
    contract_schema = load_contract(root)
    if protocol["encoder"]["revision"] != encoder.manifest["revision"]:
        raise ValueError("Register the exact checkpoint before extracting embeddings")
    revision = source_revision()
    with _attempt(output, "G1b"):
        start = time.perf_counter()
        with offline():
            encoder.preflight()
            gpu_memory(encoder.device, reset=True)
            before = time.perf_counter()
            encoder.load()
            phases = {"cold_load": time.perf_counter() - before}
            frame = load_development(root)
            before = time.perf_counter()
            vectors = encoder.cache(frame, output / "cache", view="raw", allowed_ids=set(frame.id))
            phases["development_extraction"] = time.perf_counter() - before
            np.save(output / "development_embeddings.npy", vectors, allow_pickle=False)
            sample = frame.text.iloc[:5].tolist() + ["", "long " * 1000]
            before = time.perf_counter()
            model = fit_model(frame.text.tolist(), frame.model.tolist(), {"architecture": "F", "C": 2},
                              encoder=encoder, embeddings=vectors)
            phases["probe_fit"] = time.perf_counter() - before
            independent_contract(model, sample)
            capacity = profile_capacity(frame, model, output, contract_schema,
                                        allowed_ids=set(read_json(root / "manifest.json")["development_ids"]),
                                        manifest_hash=digest(root / "manifest.json"))
        evidence = _evidence(root, output, capacity, start=start, available_memory=available_memory,
                             limit_seconds=limit_seconds, cold_restart=cold_restart, revision=revision,
                             phases=phases, encoder=encoder)
        evidence.update(upstream={"G1a": digest(root / "G1a.json")}, encoder_hash=identity(encoder.manifest))
        write_json(output / "G1b.json", evidence, exclusive=True)
        return evidence
