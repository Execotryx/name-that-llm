"""Synthetic regression coverage for provenance roles and installed requirements."""
import copy
import os
import sys
import shutil
import subprocess
import tempfile
import unittest
from email.message import Message
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from importlib.metadata import PackageNotFoundError

import numpy as np

from ntl.common import digest, read_json, write_json
from ntl.environment import dependency_closure, runtime_profile, validate_profile
from ntl.provenance import execution, artifact_execution, role_envelope, verify_roles, assert_execution
from ntl.decision import freeze
from test_contracts import fixture, dev_root


class SyntheticEncoder:
    manifest = {"revision": "a" * 40}

    def runtime(self):
        profile = runtime_profile()
        return {**profile, "kind": "neural", "settings": {"synthetic": True}}

    def encode(self, texts):
        return np.asarray([[len(t), len(set(t)), t.count("a")] for t in texts], dtype=np.float32)

    def cache(self, frame, directory, **kwargs):
        return self.encode(frame.text)


class Followups(unittest.TestCase):
    def distribution(self, version="1", requires=(), extras=()):
        meta = Message()
        for extra in extras:
            meta["Provides-Extra"] = extra
        return SimpleNamespace(version=version, requires=requires, metadata=meta, read_text=lambda n: n)

    def closure(self, distributions, roots=("parent",)):
        def lookup(name):
            if name not in distributions:
                raise PackageNotFoundError(name)
            return distributions[name]
        with patch("ntl.environment.metadata.distribution", side_effect=lookup):
            return dependency_closure(roots)

    def test_markers_versions_and_inactive_packages(self):
        parent = self.distribution(requires=['child>=2; python_version >= "3.0"'])
        with self.assertRaisesRegex(ValueError, "from parent: child"):
            self.closure({"parent": parent})
        with self.assertRaisesRegex(ValueError, "installed version 0.1"):
            self.closure({"parent": parent, "child": self.distribution("0.1")})
        self.assertIn("child", self.closure({"parent": parent, "child": self.distribution("2+local")})[0])
        parent.requires = ['child>=2; python_version < "1.0" and os_name == "nt"']
        a = self.closure({"parent": parent})
        b = self.closure({"parent": parent, "child": self.distribution("0.1")})
        self.assertEqual(a, b)

    def test_extras_cycles_diamonds_and_order(self):
        distributions = {
            "parent": self.distribution(requires=["child", "other"]),
            "other": self.distribution(requires=["child[fast]>=1"]),
            "child": self.distribution(requires=['leaf; extra == "fast"', "parent"], extras=["fast"]),
            "leaf": self.distribution(),
        }
        first = self.closure(distributions)
        self.assertIn("leaf", first[0])
        distributions["parent"].requires.reverse()
        self.assertEqual(first, self.closure(distributions))
        distributions["other"].requires = ["child>=2"]
        with self.assertRaisesRegex(ValueError, "violates >=2"):
            self.closure(distributions)

    def test_invalid_metadata_and_profiles(self):
        for requirement in ("child @ https://invalid.test/a.whl", "child[unknown]", "!bad"):
            with self.subTest(requirement=requirement), self.assertRaises(ValueError):
                self.closure({"parent": self.distribution(requires=[requirement]), "child": self.distribution()})
        with self.assertRaisesRegex(ValueError, "migration"):
            validate_profile({"version": 1})
        profile = runtime_profile()
        validate_profile(profile)
        profile["packages"]["numpy"]["version"] = "0"
        with self.assertRaisesRegex(ValueError, "closure changed"):
            validate_profile(profile)

    def test_invalid_transitive_encoder_dependency_precedes_import(self):
        from test_corrections import asset_tree
        with tempfile.TemporaryDirectory() as tmp:
            encoder = asset_tree(Path(tmp))
            def lookup(name):
                if name == "child":
                    raise PackageNotFoundError(name)
                return self.distribution(requires=['child>=2; python_version >= "3.0"'] if name == "torch" else [])
            with patch("ntl.environment.metadata.distribution", side_effect=lookup), patch("ntl.encoder.importlib.import_module") as imports:
                with self.assertRaisesRegex(ValueError, "from torch: child"):
                    encoder.runtime()
                imports.assert_not_called()

    def test_freeze_direct_fallback_and_neural_winners(self):
        frame = fixture(10)
        encoder = SyntheticEncoder()
        sparse = {"architecture": "S", "C": .5}
        frozen = {"architecture": "F", "C": .5}
        hybrid = {"architecture": "H", "sparse_C": .5, "frozen_C": .5, "weight": .5}
        for outcome in ("direct", "veto", "F", "H"):
            with self.subTest(outcome=outcome), tempfile.TemporaryDirectory() as tmp:
                base = Path(tmp); root = base/"dev"; dev_root(root, frame)
                run = base/"run"; run.mkdir(); (run/"anchor").write_text("synthetic")
                current = execution(encoder)
                costs = {"S": 1, "F": 2, "H": 3}
                eligible = {"eligible": ["S", "F", "H"]}
                write_json(run/"run.json", {"execution": current, "upstream": {"G1a": digest(root/"G1a.json")}, "costs": costs})
                write_json(run/"eligibility.json", eligible)
                for gate in ("G2", "G3"):
                    write_json(run/f"{gate}.json", {"execution": current, "gate": gate, "status": "passed", "development_manifest_hash": digest(root/"manifest.json"), "files": {"anchor": digest(run/"anchor")}})
                for a in ("S", "F", "H"):
                    np.save(run/f"{a}_oof.npy", np.full((len(frame), 18), 1/18))
                diagnostics = base/"diagnostics"; diagnostics.mkdir()
                write_json(diagnostics/"anchor.json", {})
                write_json(diagnostics/"manifest.json", {"execution": execution(), "run_hash": digest(run/"G2.json"), "development_manifest_hash": digest(root/"manifest.json"), "view_version": "views-v2-preserved-prefix", "files": {"anchor.json": digest(diagnostics/"anchor.json")}})
                from ntl.diagnostics import topic_stress
                topic_stress(root, base/"topic")
                selected = sparse if outcome == "direct" else hybrid if outcome == "H" else frozen
                with patch("ntl.decision.source_revision", return_value="synthetic"), patch("ntl.decision.eligibility", return_value=(eligible, costs)), patch("ntl.decision.inner_predictions", return_value={}), patch("ntl.decision.configurations", return_value=[]), patch("ntl.decision.choose", return_value=(selected, {"S": sparse})), patch("ntl.decision.robustness_veto", return_value={"passed": outcome != "veto"}):
                    freeze(root, run, diagnostics, base/"topic/topic_report.json", base/"decision", base/"receipt.json", encoder=encoder)
                decision = read_json(base/"decision/decision.json")
                roles = verify_roles(decision)
                self.assertEqual(roles, verify_roles(read_json(base/"decision/G4.json")))
                self.assertEqual(roles["selection_execution"], current)
                expected = "S" if outcome in ("direct", "veto") else outcome
                self.assertEqual(decision["architecture"], expected)
                import joblib
                model = joblib.load(base/"decision/selected.joblib")
                assert_execution(roles["artifact_execution"]["selected"], artifact_execution(model))
                self.assertEqual(roles["artifact_execution"]["selected"]["encoder"] is None, expected == "S")
                if expected != "S":
                    self.assertIsNone(roles["artifact_execution"]["reference"]["encoder"])
                from ntl.locked_eval import prediction_models
                prediction_models(base/"decision", decision)
                drifted = copy.deepcopy(decision)
                role = "reference" if expected != "S" else "selected"
                drifted["artifact_execution"][role]["encoder"] = "changed"
                with self.assertRaises(ValueError):
                    prediction_models(base/"decision", drifted)
                self.assertFalse((base/"consumption_ledger.json").exists())
                # Exercise the actual receipt and G5 lifecycle for every outcome.
                repository = Path(__file__).resolve().parents[1]
                shutil.copytree(repository/"src", base/"src", ignore=shutil.ignore_patterns("__pycache__"))
                for name in ("configs", "notebooks"):
                    shutil.copytree(repository/name, base/name)
                for name in ("pyproject.toml", "uv.lock", "requirements-runtime.txt"):
                    shutil.copy2(repository/name, base/name)
                (base/".gitignore").write_text("dev/\nrun/\ndiagnostics/\ntopic/\ndecision/\nsealed/\n__pycache__/\n")
                def git(*args):
                    subprocess.run(["git", *args], cwd=base, check=True, capture_output=True)
                git("init"); git("config", "user.name", "Synthetic Test"); git("config", "user.email", "test@example.invalid")
                git("add", "."); git("commit", "-m", "freeze synthetic receipt")
                sealed = base/"sealed"; sealed.mkdir()
                locked = fixture(2)
                locked[["id", "prompt_id", "text"]].to_csv(sealed/"texts.csv", index=False)
                locked[["id", "model"]].to_csv(sealed/"labels.csv", index=False)
                write_json(sealed/"manifest.json", {"development_manifest_hash": digest(root/"manifest.json"), "ids": locked.id.tolist(), "prompts": sorted(set(locked.prompt_id)), "files": {n: digest(sealed/n) for n in ("texts.csv", "labels.csv")}})
                script = "from pathlib import Path; from ntl.locked_eval import confirm; confirm(Path('dev'),Path('sealed'),Path('decision'),Path('receipt.json'),operator='SYNTHETIC')"
                environment = {**os.environ, "PYTHONPATH": os.pathsep.join([str(base/"src"), str(repository/"tests")])}
                first = subprocess.run([sys.executable, "-c", script], cwd=base, env=environment, capture_output=True, text=True)
                self.assertEqual(first.returncode, 0, first.stderr)
                ledger = (sealed/"consumption_ledger.json").read_bytes()
                second = subprocess.run([sys.executable, "-c", script], cwd=base, env=environment, capture_output=True, text=True)
                self.assertNotEqual(second.returncode, 0)
                self.assertEqual((sealed/"consumption_ledger.json").read_bytes(), ledger)
                bad = copy.deepcopy(decision); bad["artifact_execution"]["extra"] = execution()
                with self.assertRaises(ValueError): verify_roles(bad)
                bad = copy.deepcopy(decision); bad.pop("provenance_version")
                with self.assertRaisesRegex(ValueError, "migration"): verify_roles(bad)
