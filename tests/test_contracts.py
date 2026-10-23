from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from typing import Any, cast

import joblib
import numpy as np
import pandas as pd

from ntl.common import digest, identity, read_json, write_json
from ntl.provenance import execution
from ntl.schema import DEFAULT_CONTRACT
from ntl.data import TRAIN_COLUMNS, load_development, read_csv
from ntl.diagnostics import robustness_veto
from ntl.encoder import FrozenEncoder
from ntl.evaluation import holm, metrics, paired_uncertainty
from ntl.gates import require_gate
from ntl.inference import build_submission, independent_contract, load_model, write_submission
from ntl.labels import CLASSES
from ntl.locked_eval import confirm
from ntl.models import fit_model, probabilities
from ntl.protocol import DEFAULT, validate_protocol
from ntl.runner import evaluate
from ntl.runtime import offline
from ntl.selection import choose
from ntl.splits import assert_split, manifests
from ntl.views import transform
from ntl.diagnostics import artifact_diagnostics, topic_stress
from ntl.decision import freeze
from ntl.release import refit, replay


def fixture(prompts: int = 10) -> pd.DataFrame:
    return pd.DataFrame([{"id": f"p{p}-{k}", "prompt_id": f"p{p}",
                          "text": f"Unique style marker{chr(97+k)} repeated marker{chr(97+k)}. Another sentence here." + " extra" * (k + p % 3),
                          "model": label}
                         for p in range(prompts) for k, label in enumerate(CLASSES)], dtype="string")


def dev_root(root: Path, frame: pd.DataFrame) -> None:
    root.mkdir(parents=True)
    frame.to_csv(root / "development.csv", index=False)
    outer, inner, final = manifests(frame)
    for name, table in [("outer_folds", outer), ("inner_folds", inner), ("final_selection_folds", final)]:
        table.to_csv(root / f"{name}.csv", index=False)
    write_json(root / "protocol.json", DEFAULT)
    write_json(root / "submission_schema.json", DEFAULT_CONTRACT)
    write_json(root / "manifest.json", {"execution": execution(), "files": {p.name: digest(p) for p in root.iterdir() if p.is_file()},
               "development_ids": frame.id.tolist(), "locked_ids": ["sealed-id"], "source_hash": "synthetic-source"})
    (root / "target-log.txt").write_text("SYNTHETIC TEST EVIDENCE ONLY", encoding="utf-8")
    write_json(root / "G1a.json", {"execution": execution(), "gate": "G1a", "status": "passed",
               "development_manifest_hash": digest(root / "manifest.json"), "files": {"target-log.txt": digest(root / "target-log.txt")},
               "kaggle": True, "cold_restart": True, "internet_disabled": True,
               "independent_contract": True, "parquet_roundtrip": True, "environment": {"test": True},
               "source_revision": "synthetic-test", "peak_memory_bytes": 1, "available_memory_bytes": 100,
               "wall_seconds": 1, "limit_seconds": 100, "inference_seconds": 1})


class Contracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frame = fixture()
        cls.model = fit_model(cls.frame.text.tolist(), cls.frame.model.tolist(), {"architecture": "S", "C": .5})

    def test_independent_and_reload(self):
        sample = ["", " ", "Unicode — 中文", "```x=1``` $x^2$", "NA", "long " * 2000]
        independent_contract(self.model, sample, 7)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "model.joblib"
            joblib.dump(self.model, path)
            restored = load_model(path, digest(path))
            np.testing.assert_array_equal(self.model.predict_proba(sample), restored.predict_proba(sample))
            independent_contract(restored, sample)
            with self.assertRaises(ValueError):
                load_model(path, "wrong")

    def test_no_validation_vocabulary(self):
        features = self.model.estimator.named_steps["features"]
        for _, branch in features.transformer_list:
            self.assertNotIn("heldoutsentinel", branch.vocabulary_)
        self.model.predict(["heldoutsentinel"])
        for _, branch in features.transformer_list:
            self.assertNotIn("heldoutsentinel", branch.vocabulary_)

    def test_empty_training_view_retains_all_rows(self):
        model = fit_model([""] * 36, CLASSES * 2, {"architecture": "S", "C": 2})
        self.assertEqual(model.predict_proba(["", "unseen"]).shape, (2, 18))

    def test_probabilities_alignment_and_rejection(self):
        p = self.model.predict_proba(["example"])
        np.testing.assert_array_equal(probabilities(p[:, ::-1], CLASSES[::-1]), p)
        for invalid in (p * 2, np.full((1, 18), np.nan), np.zeros((1, 18)), np.zeros((1, 17))):
            with self.assertRaises(ValueError):
                probabilities(invalid)
        for texts in ([None], [12], "bare string"):
            with self.assertRaises(ValueError):
                self.model.predict(cast(Any, texts))

    def test_parquet_and_adapter_identity(self):
        frame = pd.DataFrame({"id": ["a", "b", "c"], "text": ["NA", "", "math—code"], "prompt_id": ["x", "x", "y"]}, dtype="string")
        expected = build_submission(frame, self.model, batch_size=1)
        reversed_frame = frame.iloc[::-1].copy()
        reversed_frame["prompt_id"] = "unrelated"
        reversed_frame["id"] = ["new-c", "new-b", "new-a"]
        actual = build_submission(reversed_frame, self.model)
        self.assertEqual(actual.model.tolist(), expected.model.tolist()[::-1])
        with tempfile.TemporaryDirectory() as tmp:
            for data in (expected, build_submission(frame.iloc[:0], self.model)):
                write_submission(Path(tmp) / "out.parquet", data)
        for column, value in (("id", ["a", "a", "b"]), ("id", ["", "b", "c"]), ("text", ["a", None, "c"])):
            bad = frame.copy()
            bad[column] = value
            with self.assertRaises(ValueError):
                build_submission(bad, self.model)

    def test_csv_literal_na_empty_and_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "test.csv"
            path.write_text('id,text\na,NA\nb,""\nc,"line one\nline two"\n', encoding="utf-8", newline="")
            frame = read_csv(path, ["id", "text"])
            self.assertEqual(frame.text.tolist(), ["NA", "", "line one\nline two"])
            path.write_text("id,text\na\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                read_csv(path, ["id", "text"])

    def test_incomplete_block_metric_and_group_uncertainty(self):
        y = CLASSES + [CLASSES[0]]
        predicted = CLASSES + [CLASSES[1]]
        self.assertAlmostEqual(metrics(y, predicted)["balanced_accuracy"], 17.5 / 18)
        with self.assertRaises(ValueError):
            metrics(y[1:18], predicted[1:18])
        truth = CLASSES + CLASSES[:-1]
        b = list(truth)
        b[0] = CLASSES[1]
        u = paired_uncertainty(truth, truth, b, ["a"] * 18 + ["b"] * 17, bootstrap=100, permutations=200)
        self.assertAlmostEqual(u["difference_pp"], 100 / 36)
        self.assertGreater(u["invalid_bootstrap"], 0)
        self.assertGreaterEqual(u["p_value"], 1 / 201)
        self.assertEqual(holm({"F": .02, "H": .03}), {"F": .04, "H": .04})

    def test_group_splits_allowlist_and_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "dev"
            dev_root(root, self.frame)
            self.assertEqual(len(load_development(root)), len(self.frame))
            for assignment in (manifests(self.frame)[0], manifests(self.frame)[2]):
                for fold in set(assignment.fold):
                    assert_split(self.frame, np.flatnonzero(assignment.fold != fold), np.flatnonzero(assignment.fold == fold))
            with (root / "development.csv").open("a") as stream:
                stream.write("tampered\n")
            with self.assertRaises(ValueError):
                load_development(root)
            self.assertIn("denied", (root / "access.jsonl").read_text())

    def test_selector_margin_cost_ties_and_diagnostic_rejection(self):
        s = {"config": {"architecture": "S", "C": .5}, "score": .4}
        f = {"config": {"architecture": "F", "C": 1}, "score": .429}
        costs = {"S": 1, "F": 2, "H": 3}
        self.assertEqual(choose([s, f], costs)[0]["architecture"], "S")
        f["score"] = .43
        self.assertEqual(choose([s, f], costs)[0]["architecture"], "F")
        h = {"config": {"architecture": "H", "sparse_C": 1, "frozen_C": 1, "weight": .5}, "score": .434}
        self.assertEqual(choose([s, f, h], costs)[0]["architecture"], "F")
        with self.assertRaises(ValueError):
            fit_model(self.frame.text.tolist(), self.frame.model.tolist(), {"architecture": "LinearSVC", "C": 1})
        protocol = copy.deepcopy(DEFAULT)
        protocol["seed"] = 42
        with self.assertRaises(ValueError):
            validate_protocol(protocol)

    def test_missing_topic_veto_and_transform_rows(self):
        p = self.model.predict_proba(self.frame.text.tolist())
        self.assertFalse(robustness_veto(self.frame, p, p, {"status": "blocked"}, "F")["passed"])
        self.assertEqual(transform("Only one sentence.", "opening-removed"), "")
        self.assertEqual(transform("", "prefix-40"), "")
        self.assertEqual(transform("```x=1``` $x^2$", "format-only"), "```x=x``` $x^x$")

    def test_encoder_cache_identity_and_order(self):
        encoder = FrozenEncoder.__new__(FrozenEncoder)
        encoder.manifest = {"revision": "a" * 40}
        encoder.batch_size = 1
        frame = self.frame.iloc[:3]
        def encode(texts):
            return np.asarray([[len(t), len(set(t))] for t in texts], dtype=np.float32)
        with tempfile.TemporaryDirectory() as tmp, patch.object(encoder, "encode", side_effect=encode), patch.object(encoder, "runtime", return_value={"synthetic": True}):
            directory = Path(tmp)
            a = encoder.cache(frame, directory, view="raw", allowed_ids=set(frame.id))
            b = encoder.cache(frame.iloc[::-1], directory, view="raw", allowed_ids=set(frame.id))
            np.testing.assert_array_equal(a[::-1], b)
            encoder.manifest["revision"] = "b" * 40
            encoder.cache(frame, directory, view="raw", allowed_ids=set(frame.id))
            self.assertEqual(len(list(directory.glob("*.npy"))), 6)
            with self.assertRaises(ValueError):
                encoder.cache(frame, directory, view="raw", allowed_ids=set())

    def test_offline_guard(self):
        import socket
        with offline(), self.assertRaises(RuntimeError):
            socket.create_connection(("example.com", 443))

    def test_gate_not_passed_from_documentation(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "G1a.json"
            write_json(path, {"gate": "G1a", "status": "passed", "development_manifest_hash": "x", "files": {}})
            with self.assertRaises(ValueError):
                require_gate(path, "G1a", "x")

    def test_locked_predictions_before_labels_and_single_consumption(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root, sealed, decision_dir = base / "dev", base / "sealed", base / "decision"
            root.mkdir(); sealed.mkdir(); decision_dir.mkdir()
            write_json(root / "manifest.json", {"synthetic": True})
            frame = fixture(2)
            frame[["id", "prompt_id", "text"]].to_csv(sealed / "texts.csv", index=False)
            frame[["id", "model"]].to_csv(sealed / "labels.csv", index=False)
            write_json(sealed / "manifest.json", {"development_manifest_hash": digest(root / "manifest.json"),
                       "files": {n: digest(sealed / n) for n in ("texts.csv", "labels.csv")},
                       "ids": frame.id.tolist(), "prompts": sorted(set(frame.prompt_id))})
            joblib.dump(self.model, decision_dir / "selected.joblib")
            decision = {"artifacts": {"selected": {"file": "selected.joblib", "sha256": digest(decision_dir / "selected.joblib"), "config": self.model.config}}}
            write_json(decision_dir / "decision.json", decision)
            original = pd.read_csv
            def audited_read(path, *args, **kwargs):
                if Path(path).name == "labels.csv":
                    self.assertTrue((sealed / "predictions_sealed.json").is_file())
                    self.assertEqual(read_json(sealed / "consumption_ledger.json")["state"], "exposed")
                return original(path, *args, **kwargs)
            with patch("ntl.locked_eval.verify_decision", return_value=decision), patch("pandas.read_csv", side_effect=audited_read):
                confirm(root, sealed, decision_dir, Path("receipt.json"), operator="SYNTHETIC-TEST")
                self.assertEqual(read_json(sealed / "consumption_ledger.json")["state"], "closed")
                with self.assertRaises(FileExistsError):
                    confirm(root, sealed, decision_dir, Path("receipt.json"), operator="SYNTHETIC-TEST")

    def test_complete_nested_sparse_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, output = Path(tmp) / "dev", Path(tmp) / "run"
            dev_root(root, self.frame)
            with patch("ntl.runner.source_revision", return_value="SYNTHETIC-TEST"):
                evaluate(root, output)
            a = np.load(output / "S_oof.npy", allow_pickle=False)
            b = np.load(output / "selector_oof.npy", allow_pickle=False)
            np.testing.assert_array_equal(a, b)
            self.assertEqual(a.shape, (len(self.frame), 18))
            self.assertEqual(read_json(output / "eligibility.json")["not_evaluated"], ["F", "H"])
            require_gate(output / "G2.json", "G2", digest(root / "manifest.json"))
            self.assertEqual(len(read_json(output / "selections.json")), 5)
            diagnostics, topic, decision = Path(tmp) / "diagnostics", Path(tmp) / "topic", Path(tmp) / "decision"
            artifact_diagnostics(root, output, diagnostics)
            topic_stress(root, topic)
            self.assertEqual(read_json(topic / "topic_report.json")["status"], "blocked")
            receipt = Path(tmp) / "receipt.json"
            # A stale implementation or replaced cost profile must fail before
            # final-selection fitting and before producing a frozen receipt.
            stale = copy.deepcopy(execution())
            stale["code"]["src/ntl/models.py"] = "0" * 64
            with patch("ntl.decision.source_revision", return_value="SYNTHETIC-TEST"), patch("ntl.decision.execution", return_value=stale), self.assertRaises(ValueError):
                freeze(root, output, diagnostics, topic / "topic_report.json", decision, receipt)
            self.assertFalse(decision.exists())
            original_gate = (root / "G1a.json").read_bytes()
            changed_gate = read_json(root / "G1a.json")
            changed_gate["inference_seconds"] = 2
            write_json(root / "G1a.json", changed_gate)
            with patch("ntl.decision.source_revision", return_value="SYNTHETIC-TEST"), self.assertRaisesRegex(ValueError, "eligibility evidence changed"):
                freeze(root, output, diagnostics, topic / "topic_report.json", decision, receipt)
            self.assertFalse(receipt.exists())
            (root / "G1a.json").write_bytes(original_gate)
            with patch("ntl.decision.source_revision", return_value="SYNTHETIC-TEST"):
                freeze(root, output, diagnostics, topic / "topic_report.json", decision, receipt)
            frozen = read_json(decision / "decision.json")
            self.assertEqual(frozen["architecture"], "S")
            self.assertEqual(read_json(receipt)["decision_sha256"], digest(decision / "decision.json"))

    def test_post_confirmation_refit_and_local_fixed_refit_replay(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root, sealed, decision_dir = base / "dev", base / "sealed", base / "decision"
            root.mkdir(); sealed.mkdir(); decision_dir.mkdir()
            write_json(root / "submission_schema.json", DEFAULT_CONTRACT)
            frame = fixture(150).iloc[1:].reset_index(drop=True)
            source = base / "train.csv"
            frame.to_csv(source, index=False)
            write_json(root / "manifest.json", {"development_ids": frame.id.iloc[:2100].tolist(),
                       "locked_ids": frame.id.iloc[2100:].tolist()})
            decision = {"execution": execution(), "submission_schema": DEFAULT_CONTRACT, "architecture": "S", "config": {"architecture": "S", "C": .5},
                        "source_hash": digest(source), "classes": CLASSES}
            write_json(decision_dir / "decision.json", decision)
            write_json(sealed / "confirmation.json", {"test": "synthetic-only"})
            write_json(sealed / "consumption_ledger.json", {"state": "closed", "decision_sha256": digest(decision_dir / "decision.json"),
                       "confirmation_sha256": digest(sealed / "confirmation.json")})
            for attached in (False, True):
                bundle = base / str(attached)
                with patch("ntl.release.verify_decision", return_value=decision), patch("ntl.release.source_revision", return_value="SYNTHETIC-TEST"):
                    refit(root, sealed, decision_dir, Path("receipt.json"), source, bundle, task_artifacts_permitted=attached)
                manifest = read_json(bundle / "refit_manifest.json")
                self.assertEqual(manifest["rows"], 2699)
                self.assertEqual(manifest["config"], decision["config"])
                if attached:
                    model = load_model(bundle / "model.joblib", manifest["files"]["model.joblib"])
                    self.assertEqual(model.config, decision["config"])
                else:
                    test = base / "test.csv"
                    pd.DataFrame({"id": ["1", "2", "3"], "text": ["", "NA", "independent"]}, dtype="string").to_csv(test, index=False)
                    result = replay(bundle, test, base / "output", available_memory=32 * 1024**3)
                    self.assertEqual(result["rows"], 3)
                    self.assertEqual(result["status"], "blocked")
                    self.assertEqual(set(result["scale_seconds"]), {"0", "1", "3", "4000", "8000"})


if __name__ == "__main__":
    unittest.main()
