"""Single-use holdout state machine: persist predictions before opening labels."""
from __future__ import annotations

import subprocess
from pathlib import Path

import numpy as np

from .common import code_files, digest, now, read_json, record, source_revision, verify_files, write_json
from .data import read_csv
from .evaluation import paired_uncertainty, report
from .gates import require_gate
from .inference import load_model
from .labels import CLASSES


def verify_decision(root: Path, decision_dir: Path, receipt: Path) -> dict:
    source_revision()
    # A tracked receipt makes the exact decision reviewable before holdout access.
    repository = Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip())
    relative_receipt = receipt.resolve().relative_to(repository.resolve()).as_posix()
    tracked = subprocess.check_output(["git", "show", f"HEAD:{relative_receipt}"], text=True)
    import json
    committed = json.loads(tracked)
    if committed != read_json(receipt) or committed["decision_sha256"] != digest(decision_dir / "decision.json"):
        raise ValueError("Decision must match its committed receipt")
    if committed["G4_sha256"] != digest(decision_dir / "G4.json"):
        raise ValueError("G4 evidence drift")
    decision = read_json(decision_dir / "decision.json")
    if decision["code_files"] != code_files():
        raise ValueError("Implementation changed after decision freeze")
    manifest_hash = digest(root / "manifest.json")
    require_gate(decision_dir / "G4.json", "G4", manifest_hash)
    require_gate(root / "G1a.json", "G1a", manifest_hash)
    if decision["development_manifest_hash"] != manifest_hash or decision["classes"] != CLASSES:
        raise ValueError("Decision data or classes drift")
    if decision["evidence"]["G1a"] != digest(root / "G1a.json"):
        raise ValueError("G1 evidence drift")
    for artifact in decision["artifacts"].values():
        verify_files(decision_dir, {artifact["file"]: artifact["sha256"]})
    return decision


def confirm(root: Path, sealed: Path, decision_dir: Path, receipt: Path, *, operator: str) -> None:
    decision = verify_decision(root, decision_dir, receipt)
    manifest = read_json(sealed / "manifest.json")
    if manifest["development_manifest_hash"] != digest(root / "manifest.json"):
        raise ValueError("Sealed manifest provenance drift")
    verify_files(sealed, manifest["files"])
    # Atomic exclusive creation reserves the entire attempt, including crashes.
    ledger = sealed / "consumption_ledger.json"
    write_json(ledger, {"state": "reserved", "operator": operator, "time": now(),
               "decision_sha256": digest(decision_dir / "decision.json")}, exclusive=True)
    record(sealed / "access.jsonl", action="confirmation", status="reserved", operator=operator)
    try:
        texts = read_csv(sealed / "texts.csv", ["id", "prompt_id", "text"])
        if texts.id.tolist() != manifest["ids"] or sorted(set(texts.prompt_id)) != manifest["prompts"]:
            raise ValueError("Locked membership drift")
        predictions = {}
        for name, artifact in decision["artifacts"].items():
            model = load_model(decision_dir / artifact["file"], artifact["sha256"])
            if model.config != artifact["config"]:
                raise ValueError("Loaded recipe drift")
            predictions[name] = model.predict_proba(texts.text.tolist())
            np.save(sealed / f"{name}_predictions.npy", predictions[name], allow_pickle=False)
        prediction_hashes = {name: digest(sealed / f"{name}_predictions.npy") for name in predictions}
        write_json(sealed / "predictions_sealed.json", {"hashes": prediction_hashes,
                   "decision": digest(decision_dir / "decision.json"), "time": now()}, exclusive=True)
        # Mark exposure conservatively before parsing labels. Any later failure
        # remains consumed and cannot become a second confirmation trial.
        write_json(ledger, {"state": "exposed", "operator": operator, "predictions": prediction_hashes,
                   "time": now(), "decision_sha256": digest(decision_dir / "decision.json")})
        import pandas as pd
        labels = pd.read_csv(sealed / "labels.csv", dtype=str, keep_default_na=False)
        if list(labels.columns) != ["id", "model"] or labels.id.tolist() != texts.id.tolist():
            raise ValueError("Sealed labels row alignment drift")
        results = {name: report(labels.model, p) for name, p in predictions.items()}
        interpretation, uncertainty = "Sparse-only confirmation; no challenger comparison", None
        if "reference" in predictions:
            uncertainty = paired_uncertainty(labels.model, np.asarray(CLASSES)[predictions["selected"].argmax(axis=1)],
                                              np.asarray(CLASSES)[predictions["reference"].argmax(axis=1)], texts.prompt_id)
            delta, (low, high) = uncertainty["difference_pp"], uncertainty["interval_pp"]
            if delta <= -3 or high < 0:
                interpretation = "Material contradiction; withhold robust superiority claim; frozen candidate unchanged"
            elif low > 0:
                interpretation = "Positive direction supported on limited holdout; frozen candidate unchanged"
            else:
                interpretation = "Inconclusive; frozen candidate unchanged"
            if delta < 0:
                interpretation += "; directional reversal"
        write_json(sealed / "confirmation.json", {"results": results, "paired": uncertainty,
                   "interpretation": interpretation, "decision_sha256": digest(decision_dir / "decision.json"),
                   "predictions": prediction_hashes, "input_files": manifest["files"], "operator": operator,
                   "caveat": "30 prompt groups give limited evidence; nonsignificance does not establish equivalence"}, exclusive=True)
        write_json(ledger, {"state": "closed", "operator": operator, "time": now(),
                   "decision_sha256": digest(decision_dir / "decision.json"),
                   "confirmation_sha256": digest(sealed / "confirmation.json"), "predictions": prediction_hashes})
        record(sealed / "access.jsonl", action="confirmation", status="closed")
    except Exception as error:
        record(sealed / "incidents.jsonl", error=str(error), state=read_json(ledger)["state"],
               recovery="No automatic reset; pre-exposure repair requires custodian incident review")
        raise
