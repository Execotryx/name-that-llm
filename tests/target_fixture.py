"""Synthetic target records ONLY. These are never real deployment evidence."""
from ntl.capacity import SCALES, workload
from ntl.common import digest, identity
from ntl.provenance import execution


def target_record(root, frame) -> dict:
    plan = workload(frame, set(frame.id), digest(root / "manifest.json"))
    files = {}
    for scale in (*SCALES, "stress"):
        path = root / f"capacity-{scale}.parquet"
        path.write_text("SYNTHETIC CONTROL-FLOW FIXTURE; NOT A PARQUET OR TARGET RUN")
        files[path.name] = digest(path)
    capacity = {"version": 1, "workload": plan, "workload_hash": identity(plan),
                "scale_seconds": {str(n): 1 for n in SCALES}, "scale_rows": {str(n): n for n in SCALES},
                "encoder_batch_size": None, "tokens": None, "files": files,
                "stress": {"rows": 64, "adapter_batch_size": 64, "seconds": 1}}
    return {"resource_version": 1, "execution": execution(), "gate": "G1a", "status": "passed",
            "development_manifest_hash": digest(root / "manifest.json"), "files": files,
            "kaggle": True, "cold_restart": True, "internet_disabled": True,
            "independent_contract": True, "parquet_roundtrip": True, "environment": {"synthetic": True},
            "source_revision": "SYNTHETIC", "peak_memory_bytes": 1, "available_memory_bytes": 100,
            "wall_seconds": 1, "limit_seconds": 100, "inference_seconds": 1,
            "scale_seconds": capacity["scale_seconds"], "capacity": capacity, "gpu": None}
