"""Small shared integrity and persistence primitives."""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
import platform
import subprocess
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def digest(path: str | Path) -> str:
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def identity(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     allow_nan=False).encode()).hexdigest()


def read_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path: str | Path, value: Any, *, exclusive: bool = False) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("x" if exclusive else "w", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)
        stream.write("\n")


def record(path: str | Path, **fields: Any) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps({"time": now(), **fields}, sort_keys=True) + "\n")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def environment() -> dict:
    return {"python": platform.python_version(), "platform": platform.platform(),
            "cpu": {"processor": platform.processor(), "logical_count": os.cpu_count()},
            "packages": {p: importlib.metadata.version(p) for p in
                         ("pandas", "numpy", "scipy", "scikit-learn", "pyarrow", "joblib")}}


def source_revision() -> str:
    # A clean unrelated working directory must not attest to this package's source.
    package = Path(__file__).resolve().parent
    repository = Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"], cwd=package, text=True).strip())
    if subprocess.check_output(["git", "status", "--porcelain"], cwd=repository, text=True).strip():
        raise ValueError("A clean committed checkout is required for registered execution")
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repository, text=True).strip()


def verify_files(root: Path, files: dict[str, str]) -> None:
    for name, expected in files.items():
        path = (root / name).resolve()
        if not path.is_relative_to(root.resolve()) or digest(path) != expected:
            raise ValueError(f"Missing, escaped or changed artifact: {name}")


def code_files() -> dict[str, str]:
    # Resolve the executing package, never the caller's working directory.
    package = Path(__file__).resolve().parent
    root = package.parents[1]
    paths = {f"src/ntl/{p.name}": p for p in package.glob("*.py")}
    for name in ("pyproject.toml", "uv.lock", "requirements-runtime.txt", "configs/protocol.json", "configs/labels.json",
                 "notebooks/submission.ipynb"):
        paths[name] = root / name
    return {name: digest(path) for name, path in sorted(paths.items())}
