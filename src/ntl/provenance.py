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


def artifact_execution(model) -> dict:
    """Derive identity from the actual branch layout, not just a declared name."""
    architecture = model.config["architecture"]
    if architecture == "H":
        if model.sparse.config["architecture"] != "S" or model.frozen.config["architecture"] != "F":
            raise ValueError("Invalid hybrid branches")
        sparse = artifact_execution(model.sparse)
        frozen = artifact_execution(model.frozen)
        if sparse["code"] != frozen["code"]:
            raise ValueError("Hybrid implementation mismatch")
        return frozen
    if architecture not in ("S", "F") or (model.encoder is None) != (architecture == "S"):
        raise ValueError("Artifact architecture/encoder mismatch")
    return execution(model.encoder)


def role_envelope(selection: dict, artifacts: dict) -> dict:
    return {"provenance_version": 3, "selection_execution": selection,
            "artifact_execution": artifacts, "execution": artifacts["selected"]}


def verify_roles(document: dict) -> dict:
    if document.get("provenance_version") != 3:
        raise ValueError("Legacy ambiguous provenance; register a role-envelope migration")
    roles = document.get("artifact_execution", {})
    if set(roles) not in ({"selected"}, {"selected", "reference"}):
        raise ValueError("Missing or unexpected artifact roles")
    selection = document.get("selection_execution", {})
    for value in [selection, *roles.values()]:
        if value.get("version") != 2 or value.get("runtime", {}).get("version") != 2:
            raise ValueError("Legacy execution/runtime role; migration required")
        if value.get("code") != selection.get("code"):
            raise ValueError("Selection/artifact implementation mismatch")
    if document.get("execution") != roles["selected"]:
        raise ValueError("Selected execution role mismatch")
    return role_envelope(selection, roles)
