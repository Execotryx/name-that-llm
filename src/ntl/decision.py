"""Freeze the final development recipe and commit-ready decision receipt."""
from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from .common import code_files, digest, environment, identity, read_json, source_revision, verify_files, write_json
from .data import load_development
from .diagnostics import robustness_veto, verify_topic
from .gates import require_gate
from .inference import independent_contract, load_model
from .labels import CLASSES
from .protocol import registered
from .schema import load_contract
from .provenance import execution, assert_execution, lineage
from .views import VERSION
from .runner import ExperimentLog, eligibility, fold_assignments, inner_predictions
from .selection import choose, configurations


def freeze(root: Path, run: Path, diagnostics: Path, topic_path: Path, output: Path,
           receipt: Path, *, encoder=None, neural_gate: Path | None = None) -> None:
    revision = source_revision()
    protocol = registered(root)
    frame = load_development(root)
    manifest_hash = digest(root / "manifest.json")
    current = execution(encoder)
    require_gate(run / "G2.json", "G2", manifest_hash, current=current)
    require_gate(run / "G3.json", "G3", manifest_hash, current=current)
    diagnostic_manifest = read_json(diagnostics / "manifest.json")
    verify_files(diagnostics, diagnostic_manifest["files"])
    if diagnostic_manifest["run_hash"] != digest(run / "G2.json") or diagnostic_manifest["development_manifest_hash"] != manifest_hash:
        raise ValueError("Diagnostics provenance mismatch")
    assert_execution(diagnostic_manifest.get("execution", {}), execution())
    if diagnostic_manifest.get("view_version") != VERSION:
        raise ValueError("Stale diagnostic view")
    upstream = lineage({"G1a": root / "G1a.json", **({"G1b": neural_gate} if neural_gate else {})})
    run_record = read_json(run / "run.json")
    assert_execution(run_record.get("execution", {}), current)
    if run_record.get("upstream") != upstream:
        raise ValueError("Evaluation eligibility evidence changed")
    topic = verify_topic(root, topic_path, frame, current, upstream)
    eligible, costs = eligibility(root, neural_gate, encoder)
    if costs != run_record["costs"]:
        raise ValueError("Measured selection costs changed")
    if eligible != read_json(run / "eligibility.json"):
        raise ValueError("Candidate eligibility changed after nested evaluation")
    if output.exists() or receipt.exists():
        raise ValueError("Never replace a frozen decision or receipt")
    output.mkdir(parents=True)
    log = ExperimentLog(output / "experiment_registry.jsonl", 38)
    if encoder is not None:
        log.cache_embeddings(frame, encoder, output / "embedding_cache")
    assignments = fold_assignments(frame, pd.read_csv(root / "final_selection_folds.csv", dtype={"id": str}))
    inner = inner_predictions(frame, assignments, log, encoder=encoder)
    selected, per_candidate = choose(configurations(inner, frame.model), costs)
    veto = None
    if selected["architecture"] != "S":
        veto = robustness_veto(frame, np.load(run / "S_oof.npy", allow_pickle=False),
                               np.load(run / f"{selected['architecture']}_oof.npy", allow_pickle=False),
                               topic, selected["architecture"])
        if not veto["passed"]:
            selected = per_candidate["S"]
    configs = {"selected": selected}
    if selected["architecture"] != "S":
        configs["reference"] = per_candidate["S"]
    artifacts = {}
    for name, config in configs.items():
        model = log.fit(frame, config, encoder=encoder)
        path = output / f"{name}.joblib"
        joblib.dump(model, path)
        restored = load_model(path, digest(path))
        contract = independent_contract(restored, ["", "  ", "Unicode — 数学", "```python\nx=1\n```", "long " * 600])
        np.testing.assert_allclose(model.predict_proba(frame.text.iloc[:3].tolist()),
                                   restored.predict_proba(frame.text.iloc[:3].tolist()), atol=1e-5, rtol=1e-4)
        artifacts[name] = {"file": path.name, "sha256": digest(path), "config": config, "contract": contract}
    decision = {"execution": current, "upstream": upstream, "submission_schema": load_contract(root), "architecture": selected["architecture"], "config": selected, "classes": CLASSES,
                "protocol_hash": identity(protocol), "development_manifest_hash": manifest_hash,
                "source_hash": read_json(root / "manifest.json")["source_hash"], "code_revision": revision,
                "code_files": code_files(),
                "environment": environment(), "artifacts": artifacts, "training_ids": frame.id.tolist(),
                "seed": 2027, "precision": "float32-features", "batch_size": protocol["batch_size"],
                "view": "raw", "encoder": encoder.manifest if encoder is not None else None,
                "eligibility": eligible, "veto": veto, "topic": topic, "holdout": protocol["holdout"],
                "rationale": "Fixed full-development inner selection, outer promotion margin and registered vetoes; otherwise S",
                "caveat": "Chosen development score is selection-affected. Selector OOF covers inner selection, not later diagnostic vetoes.",
                "evidence": {"G1a": digest(root / "G1a.json"), "G2": digest(run / "G2.json"),
                             "diagnostics": digest(diagnostics / "manifest.json"), "topic": digest(topic_path)}}
    write_json(output / "decision.json", decision, exclusive=True)
    write_json(output / "G4.json", {"execution": current, "upstream": upstream, "gate": "G4", "status": "passed", "development_manifest_hash": manifest_hash,
               "files": {p.relative_to(output).as_posix(): digest(p) for p in output.rglob("*") if p.is_file()},
               "blocked_diagnostics": ["topic-proxy"] if topic["status"] == "blocked" else []}, exclusive=True)
    write_json(receipt, {"decision_sha256": digest(output / "decision.json"),
               "G4_sha256": digest(output / "G4.json"), "protocol_sha256": identity(protocol)}, exclusive=True)
