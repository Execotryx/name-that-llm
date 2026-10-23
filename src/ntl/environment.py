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

from .common import identity, digest, read_json, write_json

CORE = ("pandas", "numpy", "scipy", "scikit-learn", "pyarrow", "joblib", "threadpoolctl")
NEURAL = ("torch", "transformers", "tokenizers", "huggingface-hub", "safetensors")


def package_inventory(names, *, transitive=False) -> dict:
    result = {}
    pending = list(names)
    while pending:
        name = re.sub(r"[-_.]+", "-", pending.pop().lower())
        if name in result:
            continue
        try:
            dist = metadata.distribution(name)
        except metadata.PackageNotFoundError as error:
            raise ValueError(f"Missing local dependency: {name}; stage the pinned wheels offline") from error
        records = {n: hashlib.sha256((dist.read_text(n) or "").encode()).hexdigest()
                   for n in ("METADATA", "WHEEL", "RECORD")}
        result[name] = {"version": dist.version, "installed_build": records}
        if transitive:
            for req in dist.requires or []:
                if "extra ==" in req or "extra==" in req:
                    continue
                dependency = re.match(r"[\w.-]+", req)
                if dependency:
                    dep = dependency.group()
                    try:
                        metadata.distribution(dep)
                    except metadata.PackageNotFoundError:
                        if ";" not in req:
                            raise ValueError(f"Missing local dependency: {dep} required by {name}")
                    else:
                        pending.append(dep)
    return dict(sorted(result.items()))


def runtime_profile(*, neural: bool = False, settings: dict | None = None, tokenizer_packages=()) -> dict:
    return {"version": 1, "kind": "neural" if neural else "sparse", "python": platform.python_version(),
            "packages": package_inventory(CORE + NEURAL + tuple(tokenizer_packages) if neural else CORE,
                                          transitive=True),
            "settings": settings if neural else {},
            "numerical_environment": {k: os.environ.get(k) for k in
                ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "CUBLAS_WORKSPACE_CONFIG")}}


def assert_runtime(expected: dict, current: dict) -> None:
    if not expected or expected.get("version") != 1:
        raise ValueError("Missing runtime identity; legacy evidence requires a versioned migration")
    if expected != current:
        changed = [k for k in set(expected) | set(current) if expected.get(k) != current.get(k)]
        raise ValueError(f"Incompatible runtime profile: {', '.join(sorted(changed))}")


def write_runtime_lock(path: Path, profile: dict, wheels: Path) -> None:
    """Prepare a lock from local wheels; never install or download at execution time."""
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
    write_json(path, {"version": 1, "profile": profile, "wheel_packages": packages,
                      "wheel_sha256": inventory, "wheel_files": wheel_files}, exclusive=True)


def verify_runtime_lock(path: Path, profile: dict) -> dict:
    lock = read_json(path)
    if lock.get("version") != 1 or not lock.get("wheel_sha256"):
        raise ValueError("Missing pinned wheel inventory")
    if any(not re.fullmatch(r"[0-9a-f]{64}", h) for h in lock["wheel_sha256"].values()):
        raise ValueError("Invalid wheel SHA-256")
    if any(lock.get("wheel_files", {}).get(n) not in lock["wheel_sha256"] for n in profile["packages"]):
        raise ValueError("Runtime wheel hashes do not cover every required package")
    assert_runtime(lock["profile"], profile)
    if any(lock.get("wheel_packages", {}).get(n) != v["version"] for n, v in profile["packages"].items()):
        raise ValueError("Runtime lock does not cover required installed dependencies")
    return lock
