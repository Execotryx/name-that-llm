"""Metadata-only dependency capture; optional execution settings are supplied by the encoder."""
from __future__ import annotations

import importlib.metadata as metadata
import platform
import re
import os
import hashlib
import zipfile
from email.parser import Parser
from pathlib import Path

from packaging.requirements import Requirement
from packaging.markers import default_environment
from packaging.utils import canonicalize_name
from packaging.version import Version

from .common import digest, read_json, write_json

CORE = ("pandas", "numpy", "scipy", "scikit-learn", "pyarrow", "joblib", "threadpoolctl", "packaging")
NEURAL = ("torch", "transformers", "tokenizers", "huggingface-hub", "safetensors")


def dependency_closure(names, *, transitive=True) -> tuple[dict, dict]:
    """Validate installed metadata to a fixed point; never import or install packages."""
    roots = sorted(set(names))
    environment = {key: str(value) for key, value in default_environment().items()}
    packages, contexts, edges = {}, set(), set()
    pending = [("root", value, "") for value in roots]
    while pending:
        parent, raw, extra = pending.pop()
        try:
            requirement = Requirement(raw)
            if requirement.marker and not requirement.marker.evaluate({**environment, "extra": extra}):
                continue
            if requirement.url:
                raise ValueError("direct URLs are unsupported by the local-wheel policy")
            name = canonicalize_name(requirement.name)
            dist = metadata.distribution(name)
            version = Version(dist.version)
            if requirement.specifier and not requirement.specifier.contains(version):
                raise ValueError(f"installed version {version} violates {requirement.specifier}")
            requested = {canonicalize_name(e) for e in requirement.extras}
            provided = {canonicalize_name(e) for e in dist.metadata.get_all("Provides-Extra", [])}
            if not requested <= provided:
                raise ValueError(f"unknown extras: {sorted(requested - provided)}")
        except (ValueError, KeyError, metadata.PackageNotFoundError) as error:
            raise ValueError(f"Invalid local dependency from {parent}: {raw}; extra={extra!r}; "
                             f"environment={environment}; {error}") from error
        edges.add((parent, str(requirement), extra))
        if name not in packages:
            records = {n: hashlib.sha256((dist.read_text(n) or "").encode()).hexdigest()
                       for n in ("METADATA", "WHEEL", "RECORD")}
            packages[name] = {"version": dist.version, "installed_build": records}
        if transitive:
            for context in {""} | requested:
                if (name, context) not in contexts:
                    contexts.add((name, context))
                    pending.extend((name, req, context) for req in dist.requires or [])
    return dict(sorted(packages.items())), {"roots": roots, "marker_environment": environment,
                                           "edges": [list(e) for e in sorted(edges)]}


def package_inventory(names, *, transitive=False) -> dict:
    return dependency_closure(names, transitive=transitive)[0]


def runtime_profile(*, neural: bool = False, settings: dict | None = None, tokenizer_packages=()) -> dict:
    roots = CORE + NEURAL + tuple(tokenizer_packages) if neural else CORE
    packages, closure = dependency_closure(roots)
    return {"version": 2, "kind": "neural" if neural else "sparse", "python": platform.python_version(),
            "packages": packages, "closure": closure,
            "settings": settings if neural else {},
            "numerical_environment": {k: os.environ.get(k) for k in
                ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "CUBLAS_WORKSPACE_CONFIG")}}


def validate_profile(profile: dict) -> None:
    if profile.get("version") != 2 or not profile.get("closure", {}).get("roots"):
        raise ValueError("Legacy runtime profile; validated dependency closure requires migration")
    packages, closure = dependency_closure(profile["closure"]["roots"])
    if packages != profile["packages"] or closure != profile["closure"]:
        raise ValueError("Runtime dependency closure changed")


def assert_runtime(expected: dict, current: dict) -> None:
    if not expected or expected.get("version") != 2:
        raise ValueError("Missing runtime identity; legacy evidence requires a versioned migration")
    if expected != current:
        changed = [k for k in set(expected) | set(current) if expected.get(k) != current.get(k)]
        raise ValueError(f"Incompatible runtime profile: {', '.join(sorted(changed))}")


def write_runtime_lock(path: Path, profile: dict, wheels: Path) -> None:
    """Prepare a lock from local wheels; never install or download at execution time."""
    validate_profile(profile)
    inventory, packages, wheel_files = {}, {}, {}
    for wheel in sorted(wheels.glob("*.whl")):
        with zipfile.ZipFile(wheel) as archive:
            meta = [n for n in archive.namelist() if n.endswith(".dist-info/METADATA")]
            if len(meta) != 1:
                raise ValueError(f"Invalid wheel metadata: {wheel.name}")
            parsed = Parser().parsestr(archive.read(meta[0]).decode())
            name = re.sub(r"[-_.]+", "-", str(parsed["Name"]).lower())
            if name in packages:
                raise ValueError(f"Ambiguous staged wheels for {name}")
            packages[name] = str(parsed["Version"])
            wheel_files[name] = wheel.name
        inventory[wheel.name] = digest(wheel)
    missing = [n for n, v in profile["packages"].items() if packages.get(n) != v["version"]]
    if missing:
        raise ValueError(f"Stage matching local wheels for: {missing}")
    write_json(path, {"version": 2, "profile": profile, "wheel_packages": packages,
                      "wheel_sha256": inventory, "wheel_files": wheel_files}, exclusive=True)


def verify_runtime_lock(path: Path, profile: dict) -> dict:
    validate_profile(profile)
    lock = read_json(path)
    if lock.get("version") != 2 or not lock.get("wheel_sha256"):
        raise ValueError("Missing pinned wheel inventory")
    if any(not re.fullmatch(r"[0-9a-f]{64}", h) for h in lock["wheel_sha256"].values()):
        raise ValueError("Invalid wheel SHA-256")
    if any(lock.get("wheel_files", {}).get(n) not in lock["wheel_sha256"] for n in profile["packages"]):
        raise ValueError("Runtime wheel hashes do not cover every required package")
    assert_runtime(lock["profile"], profile)
    if any(lock.get("wheel_packages", {}).get(n) != v["version"] for n, v in profile["packages"].items()):
        raise ValueError("Runtime lock does not cover required installed dependencies")
    return lock
