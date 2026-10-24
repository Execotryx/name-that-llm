"""Validate evidence rather than deriving gate success from a checklist."""
from __future__ import annotations

from pathlib import Path

from .common import read_json, verify_files
from .provenance import execution, assert_execution, verify_roles


def require_gate(path: Path, gate: str, manifest_hash: str, *, current: dict | None = None) -> dict:
    evidence = read_json(path)
    if evidence.get("gate") != gate or evidence.get("status") != "passed":
        raise ValueError(f"{gate} is not passed")
    if evidence.get("development_manifest_hash") != manifest_hash:
        raise ValueError("Gate evidence belongs to a different data protocol")
    if not evidence.get("files"):
        raise ValueError("Gate needs hashed execution evidence")
    verify_files(path.parent, evidence["files"])
    if gate == "G4":
        verify_roles(evidence)
    assert_execution(evidence.get("execution", {}), current if current is not None else execution())
    if gate in ("G1a", "G1b", "G6"):
        for flag in ("kaggle", "internet_disabled", "cold_restart", "independent_contract", "parquet_roundtrip"):
            if evidence.get(flag) is not True:
                raise ValueError(f"Missing target execution evidence: {flag}")
        if evidence["peak_memory_bytes"] >= .8 * evidence["available_memory_bytes"]:
            raise ValueError("Insufficient memory reserve")
        if evidence["wall_seconds"] >= .7 * evidence["limit_seconds"]:
            raise ValueError("Insufficient time reserve")
        if not evidence.get("environment") or not evidence.get("source_revision"):
            raise ValueError("Missing environment/source evidence")
    return evidence
