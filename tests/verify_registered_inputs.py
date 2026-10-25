"""Run G0 against registered originals in a disposable committed source snapshot.

Usage: uv run python tests/verify_registered_inputs.py PATH_TO_REGISTERED_INPUTS [--smoke --available-memory BYTES]
No scoring, lock consumption or permanent campaign artifacts are produced.
"""
import os
import argparse
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

source = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("inputs", type=Path)
parser.add_argument("--smoke", action="store_true", help="Also run an unscored LOCAL sparse capacity probe; never passes a target gate")
parser.add_argument("--available-memory", type=int, help="Measured local memory allowance for --smoke")
options = parser.parse_args()
if options.smoke and (options.available_memory is None or options.available_memory <= 0):
    parser.error("--smoke requires a positive measured --available-memory allowance")
inputs = options.inputs.resolve()
with tempfile.TemporaryDirectory(prefix="ntl-input-review-") as directory:
    repo = Path(directory)
    for name in ("src", "configs", "notebooks", "pyproject.toml", "uv.lock", "requirements-runtime.txt"):
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
if os.environ.get('NTL_QA_SMOKE') == '1':
    from ntl.smoke import cpu_smoke
    allowance = int(os.environ['NTL_QA_MEMORY'])
    result = cpu_smoke(root, inputs/'02-test.csv', root/'local-smoke', available_memory=allowance)
    assert result['status'] == 'blocked' and not result['kaggle']
    assert not (sealed/'consumption_ledger.json').exists()
    print(json.dumps({'scope':'disposable unscored LOCAL smoke; no target gate or confirmation',
        **{key:result[key] for key in ('status','reasons','wall_seconds','phase_seconds','peak_memory_bytes','available_memory_bytes','scale_seconds','inference_seconds')},
        'workload_hash':result['capacity']['workload_hash'],'ledger_exists':False},sort_keys=True))
'''
    subprocess.run([sys.executable, "-c", script], cwd=repo,
                   env={**os.environ, "PYTHONPATH": str(repo / "src"), "NTL_QA_INPUT_DIR": str(inputs),
                        "NTL_QA_SMOKE": "1" if options.smoke else "0",
                        "NTL_QA_MEMORY": str(options.available_memory)}, check=True)
