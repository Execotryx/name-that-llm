"""Deterministic, uncached capacity workloads and comparable component costs."""
from __future__ import annotations

import hashlib
import time
from pathlib import Path

import pandas as pd

from .common import digest, identity
from .data import validate
from .inference import build_submission, write_submission, model_encoder
from .resources import number
from .runtime import synchronize

VERSION = 1
SCALES = (0, 1, 3, 4000, 8000)
ADAPTER_BATCH = 64
POLICY = {"version": VERSION, "scales": list(SCALES), "primary_rows": 4000,
          "order": "id-ascending-cycle", "adapter_batch_size": ADAPTER_BATCH,
          "timing": "adapter-plus-parquet-wall-seconds-v1", "cache": "direct-prediction-no-result-cache",
          "stress_rule": "longest-development-text-plus-512-capacity-stress-token-triplets-v1"}


def workload(frame: pd.DataFrame, allowed_ids: set[str], manifest_hash: str, *, role="development") -> dict:
    validate(frame)
    if frame.empty or not set(frame.id) <= allowed_ids:
        raise ValueError("Capacity inputs must be nonempty and allowlisted")
    ordered = frame.sort_values("id")
    return {**POLICY, "source_manifest_hash": manifest_hash, "source_role": role,
            "sources": [{"id": i, "text_sha256": hashlib.sha256(t.encode()).hexdigest()}
                        for i, t in zip(ordered.id, ordered.text)]}


def profile_capacity(frame: pd.DataFrame, model, output: Path, contract: dict, *,
                     allowed_ids: set[str], manifest_hash: str, role="development") -> dict:
    plan = workload(frame, allowed_ids, manifest_hash, role=role)
    texts = frame.sort_values("id").text.tolist()
    encoder = model_encoder(model)
    device = encoder.device if encoder is not None else "cpu"
    batch = encoder.batch_size if encoder is not None else None
    timings, rows, files = {}, {}, {}

    def measure(name: str, values: list[str], batch_size: int = ADAPTER_BATCH) -> float:
        fixture = pd.DataFrame({"id": [f"capacity-{name}-{i}" for i in range(len(values))],
                                "text": values}, dtype="string")
        path = output / f"capacity-{name}.parquet"
        if path.exists():
            raise ValueError("Preserve prior capacity output")
        synchronize(device)
        start = time.perf_counter()
        # TextClassifier calls encode directly; no ExperimentLog or embedding cache.
        write_submission(path, build_submission(fixture, model, batch_size=batch_size), contract)
        synchronize(device)
        elapsed = time.perf_counter() - start
        files[path.name] = digest(path)
        return elapsed

    for n in SCALES:
        timings[str(n)] = measure(str(n), [texts[i % len(texts)] for i in range(n)])
        rows[str(n)] = n
    longest = max(texts, key=len)
    stress_text = longest + "\n" + "capacity stress token " * 512
    stress_rows = max(ADAPTER_BATCH, batch or 1)
    stress = {"rows": stress_rows, "adapter_batch_size": stress_rows,
              "seconds": measure("stress", [stress_text] * stress_rows, stress_rows)}
    token_profile = None
    if encoder is not None:
        token_profile = encoder.token_profile(texts)
        stress["tokens"] = encoder.token_profile([stress_text] * stress_rows)
        if stress["tokens"]["min"] < 512:
            raise ValueError("Stress workload did not fill the encoder token window")
    return {"version": VERSION, "workload": plan, "workload_hash": identity(plan),
            "scale_seconds": timings, "scale_rows": rows, "stress": stress,
            "encoder_batch_size": batch, "tokens": token_profile, "files": files}


def verify_capacity(evidence: dict) -> dict:
    profile = evidence.get("capacity", {})
    plan = profile.get("workload", {})
    if profile.get("version") != VERSION or any(plan.get(k) != v for k, v in POLICY.items()):
        raise ValueError("Legacy capacity evidence; explicit workload revalidation required")
    if (profile.get("workload_hash") != identity(plan)
            or plan.get("source_manifest_hash") != evidence.get("development_manifest_hash")
            or plan.get("source_role") != ("post-confirmation-full-data" if evidence["gate"] == "G6" else "development")):
        raise ValueError("Capacity workload identity mismatch")
    sources = plan.get("sources", [])
    if (not sources or len({r["id"] for r in sources}) != len(sources)
            or sources != sorted(sources, key=lambda r: r["id"])
            or any(not isinstance(r.get("text_sha256"), str) or len(r["text_sha256"]) != 64 for r in sources)):
        raise ValueError("Invalid capacity source inventory")
    if profile.get("scale_rows") != {str(n): n for n in SCALES}:
        raise ValueError("Missing actual capacity scales")
    times = profile.get("scale_seconds", {})
    if (set(times) != {str(n) for n in SCALES} or times != evidence.get("scale_seconds")
            or any(not number(v, positive=True) for v in times.values())
            or evidence.get("inference_seconds") != times["4000"]):
        raise ValueError("Missing or inconsistent measured capacity costs")
    files = profile.get("files", {})
    expected = {f"capacity-{n}.parquet" for n in (*SCALES, "stress")}
    if {Path(n).name for n in files} != expected or len(files) != len(expected) or any(evidence.get("files", {}).get(n) != h for n, h in files.items()):
        raise ValueError("Unbound capacity outputs")
    stress = profile.get("stress", {})
    batch = profile.get("encoder_batch_size")
    neural = evidence.get("execution", {}).get("encoder") is not None
    if neural and (not isinstance(batch, int) or isinstance(batch, bool) or batch < 1):
        raise ValueError("Missing encoder batch size")
    settings = evidence.get("execution", {}).get("runtime", {}).get("settings", {})
    if (neural and batch != settings.get("batch_size")) or (not neural and batch is not None):
        raise ValueError("Capacity encoder batch differs from execution identity")
    if (stress.get("rows") != max(ADAPTER_BATCH, batch or 1)
            or stress.get("adapter_batch_size") != stress["rows"]
            or not number(stress.get("seconds"), positive=True)):
        raise ValueError("Missing full-batch capacity stress")
    if neural:
        for tokens, count in ((profile.get("tokens", {}), len(sources)), (stress.get("tokens", {}), stress["rows"])):
            if (tokens.get("rows") != count or tokens.get("max_length") != 512
                    or not all(number(tokens.get(k)) for k in ("min", "max", "truncated_rows", "truncation_rate"))):
                raise ValueError("Missing neural token-length profile")
        if stress["tokens"]["min"] < 512:
            raise ValueError("Missing maximum-token full-batch stress")
    return profile
