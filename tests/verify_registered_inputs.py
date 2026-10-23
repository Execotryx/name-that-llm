"""Run G0 against registered originals in a disposable committed source snapshot.

Usage: uv run python tests/verify_registered_inputs.py PATH_TO_REGISTERED_INPUTS
No scoring, lock consumption or permanent campaign artifacts are produced.
"""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

source = Path(__file__).resolve().parents[1]
inputs = Path(sys.argv[1]).resolve()
with tempfile.TemporaryDirectory(prefix="ntl-input-review-") as directory:
    repo = Path(directory)
    for name in ("src", "configs", "notebooks", "pyproject.toml", "uv.lock"):
        item = source / name
        if item.is_dir():
            shutil.copytree(item, repo / name, ignore=shutil.ignore_patterns("__pycache__"))
        else:
            shutil.copy2(item, repo / name)
    (repo / ".gitignore").write_text("artifacts/\n__pycache__/\n")
    for args in (("init",), ("config", "user.name", "Disposable QA"),
                 ("config", "user.email", "qa@example.invalid"), ("add", "."),
                 ("commit", "-m", "disposable implementation snapshot")):
        subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)
    script = '''
from pathlib import Path
import json
from ntl.protocol import prepare, DEFAULT
from ntl.common import read_json, digest
from ntl.data import read_csv, TRAIN_COLUMNS
import os
inputs=Path(os.environ['NTL_QA_INPUT_DIR'])
root=Path('artifacts/dev');sealed=Path('artifacts/sealed')
prepare(inputs/'01-train.csv',root,sealed,DEFAULT,test=inputs/'02-test.csv',sample=inputs/'03-sample_submission.parquet')
print(json.dumps({'scope':'disposable G0 verification only; no scoring or consumption','source_hash':digest(inputs/'01-train.csv'),'submission_schema':read_json(root/'submission_schema.json'),'development_rows':len(read_csv(root/'development.csv',TRAIN_COLUMNS)),'locked_prompts':len(read_json(root/'manifest.json')['locked_prompts']),'ledger_exists':(sealed/'consumption_ledger.json').exists()},sort_keys=True))
'''
    subprocess.run([sys.executable, "-c", script], cwd=repo,
                   env={**os.environ, "PYTHONPATH": str(repo / "src"), "NTL_QA_INPUT_DIR": str(inputs)}, check=True)
