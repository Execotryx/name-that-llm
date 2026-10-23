"""Regression boundaries for corrective OpenSpecs 08–13. All campaign fixtures are synthetic."""
from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

import joblib
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from ntl.common import digest, identity, read_json, write_json, code_files
from ntl.schema import DEFAULT_CONTRACT, arrow_schema, sample_contract
from ntl.protocol import prepare, DEFAULT
from ntl.inference import write_submission
from ntl.encoder import FrozenEncoder
from ntl.environment import runtime_profile, assert_runtime, verify_runtime_lock, write_runtime_lock
from ntl.provenance import execution, assert_execution
from ntl.models import fit_model
from ntl.labels import CLASSES
from ntl.release import replay, require_release
from ntl.diagnostics import verify_topic, supported_report
from ntl.evaluation import report
from ntl.views import transform, VERSION
from ntl.splits import folds
from test_contracts import fixture

ROOT = Path(__file__).resolve().parents[1]


def asset_tree(root: Path, *, sharded=False) -> FrozenEncoder:
    root.mkdir(exist_ok=True)
    for name, value in {"config.json": {}, "tokenizer_config.json": {}, "tokenizer.json": {}, "runtime-lock.json": {}}.items():
        write_json(root / name, value)
    if sharded:
        (root / "model-00001-of-00001.safetensors").write_bytes(b"synthetic shard")
        write_json(root / "model.safetensors.index.json", {"weight_map": {"weight": "model-00001-of-00001.safetensors"}})
    else:
        (root / "model.safetensors").write_bytes(b"synthetic weights")
    seal_assets(root)
    return FrozenEncoder(root)


def seal_assets(root: Path) -> None:
    write_json(root / "encoder.json", {"model": "microsoft/deberta-v3-small", "revision": "a"*40,
        "files": {p.name: digest(p) for p in root.iterdir() if p.is_file() and p.name != "encoder.json"}})


class Corrections(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        frame = fixture(2)
        cls.model = fit_model(frame.text.tolist(), frame.model.tolist(), {"architecture": "S", "C": .5})

    def test_prepare_string_contract_and_negative_inputs(self):
        # Exercise prepare itself, with only the fixture's source hashes and expensive
        # duplicate audit replaced. Real registered inputs are verified separately.
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            frame = fixture(150)
            frame["prompt_id"] = [f"p{int(p[1:]):03d}" for p in frame.prompt_id]
            frame = frame.loc[~((frame.prompt_id == "p002") & (frame.model == "claude-fable-5"))]
            train = base / "train.csv"; frame.to_csv(train, index=False)
            test = base / "test.csv"; test.write_text('id,text\nt1,hello\nt2,""\n')
            sample = base / "sample.parquet"
            audit = {"missing_pairs": [["p002", "claude-fable-5"]], "cross_prompt_links": []}
            for i, types in enumerate(((pa.string(), pa.string()), (pa.large_string(), pa.large_string()), (pa.string(), pa.large_string()))):
                table = pa.table({"id": pa.array(["t1", "t2"], type=types[0]), "model": pa.array(["placeholder", "placeholder"], type=types[1])})
                pq.write_table(table, sample)
                root, sealed = base / f"dev{i}", base / f"sealed{i}"
                with patch("ntl.protocol.source_revision", return_value="SYNTHETIC"), patch("ntl.protocol.check_source"), patch("ntl.protocol.audit", return_value=copy.deepcopy(audit)):
                    prepare(train, root, sealed, DEFAULT, test=test, sample=sample)
                contract = read_json(root / "submission_schema.json")
                self.assertEqual([f["type"] for f in contract["fields"]], [str(t) for t in types])
                self.assertEqual(len(read_json(root / "manifest.json")["locked_prompts"]), 30)
                for values in ((["α", "β"], [CLASSES[0], CLASSES[1]]), ([], [])):
                    out = pd.DataFrame(dict(zip(("id", "model"), values)), dtype="string")
                    write_submission(base / "out.parquet", out, contract)
                    restored = pq.read_table(base / "out.parquet")
                    self.assertTrue(restored.schema.remove_metadata().equals(arrow_schema(contract)))
                    self.assertEqual(restored.column("id").to_pylist(), values[0])
            invalid = [pa.table({"id": [1, 2], "model": ["x", "x"]}),
                       pa.table({"id": ["t1", "t1"], "model": ["x", "x"]}),
                       pa.table({"id": ["t2", "t1"], "model": ["x", "x"]}),
                       pa.table({"id": ["t1", "t2"], "model": ["x", None]}),
                       pa.table({"model": ["x", "x"], "id": ["t1", "t2"]})]
            for table in invalid:
                pq.write_table(table, sample)
                with self.assertRaises(ValueError): sample_contract(sample, ["t1", "t2"])
                with patch("ntl.protocol.source_revision", return_value="SYNTHETIC"), patch("ntl.protocol.check_source"), self.assertRaises(ValueError):
                    prepare(train, base/"bad", base/"badsealed", DEFAULT, test=test, sample=sample)
                self.assertFalse((base/"bad"/"manifest.json").exists())

    def test_restored_encoder_rejects_changed_assets_before_loader(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            encoder = asset_tree(root)
            model_file = root.parent / (root.name + ".joblib")
            try:
                joblib.dump(encoder, model_file)
                (root / "model.safetensors").write_bytes(b"changed")
                restored = joblib.load(model_file)
                with patch("ntl.encoder.importlib.import_module") as loader, self.assertRaises(ValueError):
                    restored.load()
                loader.assert_not_called()
            finally:
                model_file.unlink(missing_ok=True)

    def test_encoder_inventory_and_relocation(self):
        import shutil
        for mutation in ("marker", "tokenizer", "config", "shard", "alternate", "escape", "manifest"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp) / "assets"; encoder = asset_tree(root, sharded=mutation == "shard")
                manifest = read_json(root / "encoder.json")
                if mutation == "marker":
                    (root / "marker.txt").write_text("marker")
                    manifest["files"] = {"marker.txt": digest(root/"marker.txt")}
                elif mutation in ("tokenizer", "config"):
                    manifest["files"].pop("tokenizer.json" if mutation == "tokenizer" else "config.json")
                elif mutation == "shard":
                    (root / "model-00001-of-00001.safetensors").unlink()
                elif mutation == "alternate":
                    (root / "pytorch_model.bin").write_bytes(b"unlisted alternate")
                elif mutation == "escape":
                    manifest["files"]["../escaped.json"] = "0"*64
                else:
                    manifest["revision"] = "b"*40
                write_json(root/"encoder.json", manifest)
                if mutation == "manifest":
                    with self.assertRaises(ValueError): encoder.verify_assets()
                else:
                    with self.assertRaises((ValueError, FileNotFoundError)): FrozenEncoder(root)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); encoder = asset_tree(root/"old")
            encoder._model = object(); encoder._tokenizer = object()
            shutil.copytree(root/"old", root/"new")
            encoder.rebind(root/"new")
            self.assertIsNone(encoder._model)
            encoder.verify_assets()
            self.assertEqual(identity(encoder.manifest), encoder.manifest_hash)

    def test_valid_restored_encoder_loads_only_verified_local_assets(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp); encoder=asset_tree(base/"assets")
            joblib.dump(encoder,base/"encoder.joblib")
            restored=joblib.load(base/"encoder.joblib")
            torch, transformers = MagicMock(), MagicMock()
            with patch.object(restored,"runtime",return_value={"synthetic":True}), patch("ntl.encoder.importlib.import_module",side_effect=lambda n: torch if n=="torch" else transformers):
                restored.load()
            transformers.AutoModel.from_pretrained.assert_called_once_with(str(restored.assets),local_files_only=True,trust_remote_code=False)
            transformers.AutoTokenizer.from_pretrained.assert_called_once()

    def test_missing_neural_dependency_precedes_optional_import(self):
        with tempfile.TemporaryDirectory() as tmp:
            encoder=asset_tree(Path(tmp))
            with patch("ntl.encoder.package_inventory",side_effect=ValueError("Missing local dependency: torch")), patch("ntl.encoder.importlib.import_module") as loader, self.assertRaisesRegex(ValueError,"Missing local dependency"):
                encoder.load()
            loader.assert_not_called()

    def test_warm_encoder_rejects_numerical_setting_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            encoder=asset_tree(Path(tmp))
            encoder._loaded_runtime={"version":1,"kind":"neural","packages":{},"numerical_environment":{},
                "settings":{"device":"cpu","batch_size":8,"deterministic":True,"tf32_matmul":False,"tf32_cudnn":False}}
            torch=MagicMock();torch.are_deterministic_algorithms_enabled.return_value=False
            torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
            with patch.object(encoder,"load"), patch("ntl.encoder.importlib.import_module",return_value=torch), self.assertRaisesRegex(ValueError,"Incompatible runtime"):
                encoder.encode(["independent text"])
            torch.inference_mode.assert_not_called()

    def test_cache_runtime_drift_changes_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp); encoder=asset_tree(base/"assets"); frame=fixture(2).iloc[:3]
            profile={"version":1,"settings":{"tf32":False}}
            with patch.object(encoder,"runtime",side_effect=lambda:copy.deepcopy(profile)), patch.object(encoder,"encode",side_effect=lambda texts:np.asarray([[len(t),1] for t in texts],dtype=np.float32)):
                first=encoder.cache(frame,base/"cache",view="raw",allowed_ids=set(frame.id))
                profile["settings"]["tf32"]=True
                second=encoder.cache(frame,base/"cache",view="raw",allowed_ids=set(frame.id))
            np.testing.assert_array_equal(first,second)
            self.assertEqual(len(list((base/"cache").glob("*.npy"))),6)

    def test_local_wheel_lock_covers_every_required_package(self):
        import zipfile
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp); wheels=base/"wheels";wheels.mkdir()
            profile={"version":1,"kind":"neural","packages":{"torch":{"version":"1"},"transformers":{"version":"2"}},"settings":{}}
            for name,version in (("torch","1"),("transformers","2")):
                with zipfile.ZipFile(wheels/f"{name}-{version}-py3-none-any.whl","w") as archive:
                    archive.writestr(f"{name}-{version}.dist-info/METADATA",f"Name: {name}\nVersion: {version}\n")
            write_runtime_lock(base/"lock.json",profile,wheels)
            lock=verify_runtime_lock(base/"lock.json",profile)
            self.assertEqual(set(lock["wheel_files"]),set(profile["packages"]))
            changed=copy.deepcopy(profile);changed["packages"]["torch"]["version"]="3"
            with self.assertRaises(ValueError):verify_runtime_lock(base/"lock.json",changed)
            (wheels/"torch-1-py3-none-any.whl").unlink()
            with self.assertRaisesRegex(ValueError,"Stage matching"):write_runtime_lock(base/"missing.json",profile,wheels)

    def test_prefix_is_a_literal_original_slice(self):
        for limit in (40, 80, 120):
            for text in ("", " \t\n", "\n  " + "\t word\n"*(limit-1) + "\u2003数學  \n"):
                self.assertLessEqual(len(text.split()), limit)
                self.assertEqual(transform(text, f"prefix-{limit}"), text)
            text = "\n" + "\t".join(["```α" if i % 3 == 0 else "x^2```" for i in range(limit+5)])
            import re
            expected = text[:list(re.finditer(r"\S+", text))[limit-1].end()]
            self.assertEqual(transform(text, f"prefix-{limit}"), expected)
            self.assertTrue(text.startswith(expected))
            self.assertEqual(len(expected.split()), limit)

    def bundle(self, base: Path) -> tuple[Path, Path]:
        bundle = base/"bundle"; bundle.mkdir()
        joblib.dump(self.model, bundle/"model.joblib")
        write_json(bundle/"submission_schema.json", DEFAULT_CONTRACT)
        write_json(bundle/"profile_texts.json", fixture(2).text.tolist())
        write_json(bundle/"decision.json", {"submission_schema": DEFAULT_CONTRACT, "config": self.model.config, "execution": execution()})
        write_json(bundle/"confirmation.json", {"synthetic": True})
        manifest = {"execution": execution(), "mode": "attached-model", "config": self.model.config,
            "source_revision": "SYNTHETIC", "development_manifest_hash": "SYNTHETIC",
            "decision_sha256": digest(bundle/"decision.json"), "G5_sha256": digest(bundle/"confirmation.json"),
            "files": {p.name: digest(p) for p in bundle.iterdir()}}
        write_json(bundle/"refit_manifest.json", manifest)
        test = base/"test.csv"; test.write_text('id,text\n1,""\n2,Unicode\n')
        return bundle, test

    def test_release_resource_failure_and_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp); bundle,test=self.bundle(base)
            with patch("ntl.release.is_kaggle", return_value=True):
                blocked = replay(bundle,test,base/"blocked",available_memory=1,cold_restart=True)
                self.assertEqual(blocked["status"], "blocked")
                self.assertFalse((base/"blocked"/"submission.parquet").exists())
                self.assertTrue((base/"blocked"/"release_manifest.json").exists())
                with self.assertRaises(RuntimeError): require_release(blocked)
                passed = replay(bundle,test,base/"passed",available_memory=10**12,cold_restart=True)
            final=base/"passed"/"submission.parquet"
            self.assertEqual(passed["status"], "passed")
            self.assertEqual(passed["files"], {"submission.parquet": digest(final)})
            require_release(passed)
            before=final.read_bytes()
            with self.assertRaises(ValueError): replay(bundle,test,base/"passed",available_memory=10**12)
            self.assertEqual(final.read_bytes(), before)

    def test_release_other_failures_and_publication_recovery(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp); bundle,test=self.bundle(base)
            for name, kwargs in (("local", {}), ("notcold", {"cold_restart": False}),
                                 ("time", {"cold_restart": True, "limit_seconds": .00001})):
                with patch("ntl.release.is_kaggle", return_value=name != "local"):
                    result=replay(bundle,test,base/name,available_memory=10**12,**kwargs)
                self.assertEqual(result["status"], "blocked")
                self.assertFalse((base/name/"submission.parquet").exists())
            with patch("ntl.release.independent_contract", side_effect=ValueError("batch dependent")), self.assertRaisesRegex(ValueError,"batch dependent"):
                replay(bundle,test,base/"contract",available_memory=10**12)
            self.assertEqual(read_json(base/"contract"/"release_manifest.json")["status"], "failed")
            with patch("ntl.release.is_kaggle", return_value=True), patch.object(Path,"rename",side_effect=OSError("rename failed")), self.assertRaises(OSError):
                replay(bundle,test,base/"rename",available_memory=10**12,cold_restart=True)
            self.assertFalse((base/"rename"/"submission.parquet").exists())
            original=write_json
            def fail_manifest(path,*args,**kwargs):
                if Path(path).name=="release_manifest.json": raise OSError("disk failed")
                return original(path,*args,**kwargs)
            with patch("ntl.release.is_kaggle",return_value=True), patch("ntl.release.write_json",side_effect=fail_manifest), self.assertRaises(OSError):
                replay(bundle,test,base/"disk",available_memory=10**12,cold_restart=True)
            self.assertFalse((base/"disk"/"submission.parquet").exists())
            self.assertTrue((base/"disk"/"incidents.jsonl").exists())
            with self.assertRaises(ValueError): replay(bundle,test,base/"disk",available_memory=10**12)

    def test_runtime_and_implementation_drift(self):
        current=execution()
        for field in ("code", "encoder", "runtime"):
            changed=copy.deepcopy(current)
            if field=="code": changed[field]["src/ntl/models.py"]="0"*64
            elif field=="encoder": changed[field]="other"
            else: changed[field]["packages"]["numpy"]["version"]="unregistered"
            with self.assertRaises(ValueError): assert_execution(changed,current)
        neural={"version":1,"kind":"neural","packages":{"torch":{"version":"1"},"transformers":{"version":"2"}},"settings":{"tf32":False}}
        for package in ("torch","transformers"):
            changed=copy.deepcopy(neural); changed["packages"][package]["version"]="other"
            with self.assertRaises(ValueError): assert_runtime(neural,changed)
        changed=copy.deepcopy(neural); changed["settings"]["tf32"]=True
        with self.assertRaises(ValueError): assert_runtime(neural,changed)
        assert_runtime(neural,copy.deepcopy(neural))
        with tempfile.TemporaryDirectory() as tmp:
            lock=Path(tmp)/"runtime-lock.json"; write_json(lock,{"version":1,"profile":neural,"wheel_packages":{"torch":"1","transformers":"2"},"wheel_sha256":{"torch.whl":"a"*64,"transformers.whl":"b"*64},"wheel_files":{"torch":"torch.whl","transformers":"transformers.whl"}})
            verify_runtime_lock(lock,neural)
            with self.assertRaises(ValueError): verify_runtime_lock(lock,changed)

    def test_sparse_metadata_imports_no_optional_packages(self):
        result=subprocess.run([sys.executable,"-c","from ntl.environment import runtime_profile; import sys; runtime_profile(); assert 'torch' not in sys.modules and 'transformers' not in sys.modules"],check=True,capture_output=True,text=True)
        self.assertEqual(result.returncode,0)

    def test_topic_report_requires_aligned_hashed_predictions(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp); root=base/"dev"; root.mkdir(); output=base/"topic"; output.mkdir()
            write_json(root/"manifest.json",{"synthetic":True})
            frame=fixture(12); p=self.model.predict_proba(frame.text.tolist()); assignments=np.repeat(np.arange(6),36)
            np.save(output/"S.npy",p,allow_pickle=False)
            write_json(output/"rows.json",{"ids":frame.id.tolist(),"folds":assignments.tolist()})
            write_json(output/"clusters.json",{"membership":dict(zip(frame.prompt_id.unique(),np.repeat(np.arange(6),2).tolist()))})
            topic={"development_manifest_hash":digest(root/"manifest.json"),"status":"completed","pooled":{"S":report(frame.model,p)},"clusters":[{"cluster":i,"scores":{"S":supported_report(frame.loc[assignments==i],p[assignments==i])}} for i in range(6)]}
            write_json(output/"topic_report.json",topic)
            for fold in range(6):
                training=frame.loc[assignments!=fold].reset_index(drop=True)
                pd.DataFrame({"id":training.id.tolist(),"fold":folds(training,4)}).to_csv(output/f"inner_folds_{fold}.csv",index=False)
            def manifest():
                write_json(output/"manifest.json",{"execution":execution(),"upstream":{},"view_version":VERSION,"development_manifest_hash":digest(root/"manifest.json"),"files":{f.name:digest(f) for f in output.iterdir() if f.name!='manifest.json'}})
            with self.assertRaises(FileNotFoundError): verify_topic(root,output/"topic_report.json",frame,execution(),{})
            manifest(); verify_topic(root,output/"topic_report.json",frame,execution(),{})
            stale=read_json(output/"manifest.json");stale["view_version"]="views-v1"
            write_json(output/"manifest.json",stale)
            with self.assertRaisesRegex(ValueError,"Stale topic"): verify_topic(root,output/"topic_report.json",frame,execution(),{})
            manifest()
            topic["pooled"]["S"]["balanced_accuracy"] += .01
            write_json(output/"topic_report.json",topic); manifest()
            with self.assertRaisesRegex(ValueError,"metrics disagree"): verify_topic(root,output/"topic_report.json",frame,execution(),{})

    def test_notebook_and_cli_fail_on_blocked_result(self):
        notebook=read_json(ROOT/"notebooks/submission.ipynb")
        with patch.dict(os.environ,{"NTL_BUNDLE":"synthetic","NTL_AVAILABLE_MEMORY_BYTES":"100"}), patch("ntl.release.replay",return_value={"status":"blocked","reasons":["synthetic"]}):
            with self.assertRaises(RuntimeError): exec(''.join(notebook['cells'][1]['source']),{})
        from ntl.cli import main
        with patch.object(sys,"argv",["ntl","replay","--bundle","synthetic","--test","test.csv","--output","out","--available-memory","100"]), patch("ntl.release.replay",return_value={"status":"blocked"}):
            with self.assertRaises(RuntimeError): main()

    def test_real_git_receipt_allows_docs_and_rejects_code_drift(self):
        # Run the actual verifier in an isolated committed source snapshot. No
        # verify_decision/source_revision mocks and no real locked data.
        import shutil
        with tempfile.TemporaryDirectory() as tmp:
            repo=Path(tmp)
            shutil.copytree(ROOT/"src",repo/"src",ignore=shutil.ignore_patterns("__pycache__"))
            for name in ("pyproject.toml","uv.lock","configs","notebooks"):
                source=ROOT/name; target=repo/name
                if source.is_dir(): shutil.copytree(source,target)
                else: shutil.copy2(source,target)
            (repo/".gitignore").write_text('artifacts/\n__pycache__/\n')
            def git(*args): subprocess.run(["git",*args],cwd=repo,check=True,capture_output=True,text=True)
            git("init");git("config","user.name","Synthetic Test");git("config","user.email","test@example.invalid")
            git("add",".");git("commit","-m","synthetic source snapshot")
            script='''
from pathlib import Path
import joblib
from ntl.common import *
from ntl.provenance import execution
from ntl.environment import runtime_profile
from ntl.protocol import DEFAULT
from ntl.schema import DEFAULT_CONTRACT
from ntl.models import fit_model
from ntl.labels import CLASSES
root=Path('artifacts/dev');root.mkdir(parents=True)
write_json(root/'protocol.json',DEFAULT)
write_json(root/'manifest.json',{'files':{'protocol.json':digest(root/'protocol.json')}})
(root/'target.txt').write_text('SYNTHETIC ONLY')
write_json(root/'G1a.json',{'execution':execution(),'gate':'G1a','status':'passed','development_manifest_hash':digest(root/'manifest.json'),'files':{'target.txt':digest(root/'target.txt')},'kaggle':True,'cold_restart':True,'internet_disabled':True,'independent_contract':True,'parquet_roundtrip':True,'peak_memory_bytes':1,'available_memory_bytes':100,'wall_seconds':1,'limit_seconds':100,'environment':{'synthetic':True},'source_revision':source_revision()})
out=Path('artifacts/decision');out.mkdir()
model=fit_model(['marker'+str(i) for i in range(18)]*2,CLASSES*2,{'architecture':'S','C':.5})
joblib.dump(model,out/'selected.joblib')
decision={'execution':execution(),'code_files':code_files(),'protocol_hash':identity(DEFAULT),'development_manifest_hash':digest(root/'manifest.json'),'classes':CLASSES,'evidence':{'G1a':digest(root/'G1a.json')},'artifacts':{'selected':{'file':'selected.joblib','sha256':digest(out/'selected.joblib'),'config':model.config}}}
write_json(out/'decision.json',decision)
write_json(out/'G4.json',{'execution':execution(),'gate':'G4','status':'passed','development_manifest_hash':digest(root/'manifest.json'),'files':{p.name:digest(p) for p in out.iterdir()}})
write_json('configs/decision-receipt.json',{'decision_sha256':digest(out/'decision.json'),'G4_sha256':digest(out/'G4.json'),'protocol_sha256':identity(DEFAULT)})
'''
            env={**os.environ,"PYTHONPATH":str(repo/"src")}
            subprocess.run([sys.executable,"-c",script],cwd=repo,env=env,check=True,capture_output=True,text=True)
            git("add","configs/decision-receipt.json");git("commit","-m","freeze receipt")
            verify="from pathlib import Path; from ntl.locked_eval import verify_decision; verify_decision(Path('artifacts/dev'),Path('artifacts/decision'),Path('configs/decision-receipt.json'))"
            subprocess.run([sys.executable,"-c",verify],cwd=repo,env=env,check=True,capture_output=True,text=True)
            (repo/"notes.md").write_text('docs only');git("add","notes.md");git("commit","-m","docs")
            subprocess.run([sys.executable,"-c",verify],cwd=repo,env=env,check=True,capture_output=True,text=True)
            confirmation = """
from pathlib import Path
import pandas as pd
from ntl.common import write_json,digest
from ntl.labels import CLASSES
from ntl.locked_eval import confirm
sealed=Path('artifacts/sealed');sealed.mkdir()
ids=[str(i) for i in range(36)]
pd.DataFrame({'id':ids,'prompt_id':['g1']*18+['g2']*18,'text':['independent']*36}).to_csv(sealed/'texts.csv',index=False)
pd.DataFrame({'id':ids,'model':CLASSES*2}).to_csv(sealed/'labels.csv',index=False)
write_json(sealed/'manifest.json',{'development_manifest_hash':digest('artifacts/dev/manifest.json'),'ids':ids,'prompts':['g1','g2'],'files':{n:digest(sealed/n) for n in ('texts.csv','labels.csv')}})
confirm(Path('artifacts/dev'),sealed,Path('artifacts/decision'),Path('configs/decision-receipt.json'),operator='SYNTHETIC')
"""
            subprocess.run([sys.executable,"-c",confirmation],cwd=repo,env=env,check=True,capture_output=True,text=True)
            ledger = repo/"artifacts/sealed/consumption_ledger.json"
            consumed_bytes = ledger.read_bytes()
            repeated = "from pathlib import Path; from ntl.locked_eval import confirm; confirm(Path('artifacts/dev'),Path('artifacts/sealed'),Path('artifacts/decision'),Path('configs/decision-receipt.json'),operator='SYNTHETIC')"
            repeat_result = subprocess.run([sys.executable,"-c",repeated],cwd=repo,env=env,capture_output=True,text=True)
            self.assertNotEqual(repeat_result.returncode,0)
            self.assertEqual(ledger.read_bytes(), consumed_bytes)
            path=repo/"src/ntl/models.py";path.write_text(path.read_text()+'\n# implementation drift\n')
            git("add","src/ntl/models.py");git("commit","-m","code drift")
            result=subprocess.run([sys.executable,"-c",verify],cwd=repo,env=env,capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0)
            self.assertIn('Implementation changed',result.stderr)
            self.assertEqual(ledger.read_bytes(), consumed_bytes)
            self.assertEqual(read_json(ledger)["state"], "closed")


if __name__ == '__main__':
    unittest.main()
