"""Check the lock-derived export; optionally prove a fresh local-wheel runtime.

uv run python scripts/verify_runtime.py [--wheelhouse PATH] [--report PATH]
The acquisition phase must stage wheels first. No installer runs during inference.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

ROOT = Path(__file__).resolve().parents[1]


def requirements(text: str) -> set[str]:
    result = set()
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parsed = Requirement(line)
        if parsed.url:
            raise ValueError("Runtime export must use locked local-wheel requirements")
        result.add(str(Requirement(canonicalize_name(parsed.name) + str(parsed)[len(parsed.name):])))
    return result


def check_export(root: Path = ROOT) -> dict:
    expected = subprocess.check_output(["uv", "export", "--locked", "--no-dev", "--no-hashes",
        "--no-emit-project", "--format", "requirements-txt"], cwd=root, text=True)
    actual = requirements((root / "requirements-runtime.txt").read_text())
    wanted = requirements(expected)
    if actual != wanted:
        raise ValueError(f"Runtime export drift: missing={sorted(wanted-actual)}, unexpected={sorted(actual-wanted)}")
    return {"status": "passed", "requirements": sorted(actual)}


def isolated_runtime(wheels: Path, root: Path = ROOT) -> dict:
    from ntl.common import code_files, digest
    wheels = wheels.resolve()
    with tempfile.TemporaryDirectory(prefix="ntl-runtime-") as temporary:
        base = Path(temporary)
        venv = base / "venv"
        subprocess.run(["uv", "venv", "--python", sys.executable, str(venv)], check=True)
        python = venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        subprocess.run(["uv", "pip", "install", "--python", str(python), "--no-index", "--find-links",
                        str(wheels), "-r", str(root / "requirements-runtime.txt")], check=True)
        bundle = base / "bundle"
        shutil.copytree(root / "src/ntl", bundle / "source/ntl", ignore=shutil.ignore_patterns("__pycache__"))
        for name in code_files():
            if not name.startswith("src/ntl/"):
                target = bundle / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(root / name, target)
        probe = r'''
import contextlib, io, json, socket, sys
from pathlib import Path
def denied(*args, **kwargs):
    raise AssertionError("isolated runtime attempted network access")
socket.socket.connect = denied
socket.socket.connect_ex = denied
socket.create_connection = denied
from ntl.release import replay
from ntl.provenance import execution
from ntl.labels import CLASSES
from ntl.models import fit_model
from ntl.inference import build_submission, write_submission, independent_contract
from ntl.schema import DEFAULT_CONTRACT
from ntl.cli import main
import pandas as pd
import pyarrow.parquet as pq
sys.argv = ["ntl", "--help"]
with contextlib.redirect_stdout(io.StringIO()):
    try: main()
    except SystemExit as error: assert error.code == 0
texts = ["sparse marker " + str(i) for i in range(18)] * 2
model = fit_model(texts, CLASSES * 2, {"architecture":"S", "C":2})
independent_contract(model, ["", "NA", "数学 — code"])
test = pd.DataFrame({"id":["one", "two"], "text":["", "sample"]}, dtype="string")
write_submission("probe.parquet", build_submission(test, model), DEFAULT_CONTRACT)
assert pq.read_table("probe.parquet")["id"].to_pylist() == ["one", "two"]
assert "torch" not in sys.modules and "transformers" not in sys.modules
print(json.dumps({"status":"passed", "prefix":sys.prefix, "execution":execution(), "rows":len(test)}))
'''
        env = {**os.environ, "PYTHONPATH": str(bundle / "source"), "PYTHONNOUSERSITE": "1"}
        result = subprocess.run([str(python), "-s", "-c", probe], cwd=base, env=env,
                                check=True, text=True, capture_output=True)
        record = json.loads(result.stdout)
        if Path(record["prefix"]).resolve() != venv.resolve():
            raise ValueError("Runtime probe escaped the isolated environment")
        return {**record, "wheel_sha256": {p.name: digest(p) for p in sorted(wheels.glob("*.whl"))}}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wheelhouse", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    report = {"export": check_export()}
    if args.wheelhouse is not None:
        report["isolated_runtime"] = isolated_runtime(args.wheelhouse)
    content = json.dumps(report, indent=2) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        with args.report.open("x") as stream:
            stream.write(content)
    print(content)


if __name__ == "__main__":
    main()
