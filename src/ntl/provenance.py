"""Versioned execution identities and exact stage lineage (no Git receipt dependency)."""
from pathlib import Path

from .common import code_files, identity, digest
from .environment import runtime_profile, assert_runtime


def execution(encoder=None) -> dict:
    runtime = encoder.runtime() if encoder is not None else runtime_profile()
    return {"version": 2, "code": code_files(), "runtime": runtime,
            "encoder": identity(encoder.manifest) if encoder is not None else None}


def assert_execution(expected: dict, current: dict) -> None:
    if not expected or expected.get("version") != 2:
        raise ValueError("Missing execution identity; preserve legacy evidence and register a migration")
    if expected.get("code") != current.get("code") or expected.get("encoder") != current.get("encoder"):
        raise ValueError("Implementation or encoder changed since upstream evidence")
    assert_runtime(expected["runtime"], current["runtime"])


def lineage(paths: dict[str, Path]) -> dict:
    return {name: digest(path) for name, path in sorted(paths.items())}


def dependency_execution(expected: dict) -> dict:
    """Validate installed metadata while consuming earlier neural results without importing torch.

    Accelerator settings describe the producer, not this CPU-only consumer. Neural stages
    must instead call execution(encoder), which measures those settings again.
    """
    neural = expected.get("encoder") is not None
    extras = tuple(n for n in ("sentencepiece", "protobuf") if n in expected.get("runtime", {}).get("packages", {}))
    return {"version": 2, "code": code_files(), "encoder": expected.get("encoder"),
            "runtime": runtime_profile(neural=neural, settings=expected.get("runtime", {}).get("settings"),
                                       tokenizer_packages=extras)}
