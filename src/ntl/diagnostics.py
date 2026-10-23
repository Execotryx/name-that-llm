"""Registered artifact interventions and development-only topic-proxy stress."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from typing import Any, cast
from sklearn.cluster import KMeans
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from .common import digest, identity, read_json, record, write_json, source_revision, verify_files
from .data import load_development
from .evaluation import metrics, report
from .features import sparse_features, style_features
from .gates import require_gate
from .labels import CLASSES, PROVIDER
from .models import fit_checked, logistic, probabilities
from .protocol import registered
from .provenance import execution, assert_execution, dependency_execution, lineage
from .runner import ExperimentLog, eligibility, fold_assignments, inner_predictions
from .selection import choose, configurations
from .splits import assert_split, folds
from .views import VERSION, transform


def supported_report(frame, p) -> dict:
    support = frame.model.value_counts().to_dict()
    return {"rows": len(frame), "support": support,
            "metrics": report(frame.model, p) if set(support) == set(CLASSES) else None,
            "status": "scored" if set(support) == set(CLASSES) else "insufficient_class_support"}


def artifact_diagnostics(root: Path, run: Path, output: Path) -> None:
    protocol = registered(root)
    frame = load_development(root)
    run_execution = read_json(run / "G2.json").get("execution", {})
    require_gate(run / "G2.json", "G2", digest(root / "manifest.json"), current=dependency_execution(run_execution))
    if output.exists():
        raise ValueError("Preserve existing diagnostics")
    output.mkdir(parents=True)
    assignments = fold_assignments(frame, pd.read_csv(root / "outer_folds.csv", dtype={"id": str}))
    tables = {}
    for name in protocol["diagnostics"] + [f"prefix-{n}" for n in protocol["prefixes"]]:
        p = np.full((len(frame), 18), np.nan)
        for fold in range(5):
            train, valid = np.flatnonzero(assignments != fold), np.flatnonzero(assignments == fold)
            assert_split(frame, train, valid)
            xtrain, xvalid = frame.text.iloc[train].tolist(), frame.text.iloc[valid].tolist()
            record(output / "experiment_registry.jsonl", diagnostic=name, fold=fold, status="started",
                   training_ids=frame.id.iloc[train].tolist(), C=2, seed=2027, role="diagnostic")
            try:
                if name in ("stylometry", "length-only", "no-length"):
                    kwargs = {"length_only": name == "length-only", "no_length": name == "no-length"}
                    estimator = Pipeline([("scale", StandardScaler()), ("classifier", logistic(2))])
                    xtrain, xvalid = style_features(xtrain, **kwargs), style_features(xvalid, **kwargs)
                else:
                    view = "raw" if name == "word-only" else name
                    xtrain, xvalid = [transform(t, view) for t in xtrain], [transform(t, view) for t in xvalid]
                    estimator = Pipeline([("features", sparse_features(word_only=name == "word-only")),
                                          ("classifier", logistic(2))])
                fit_checked(estimator, xtrain, frame.model.iloc[train].tolist())
                p[valid] = probabilities(estimator.predict_proba(xvalid), estimator.classes_)
            except Exception as error:
                record(output / "experiment_registry.jsonl", diagnostic=name, fold=fold, status="failed", reason=str(error))
                raise
            record(output / "experiment_registry.jsonl", diagnostic=name, fold=fold, status="completed", convergence=getattr(estimator, "convergence_log_"))
        np.save(output / f"{name}.npy", p, allow_pickle=False)
        tables[name] = {"row_ids": frame.id.tolist(), **supported_report(frame, p), "refitted": True, "C": 2, "view_version": VERSION}
    # Primary prefix perturbations reuse each raw fold's frozen C=2 model;
    # raw comparisons use the same eligible rows, including a common >=120 subset.
    raw = np.full((len(frame), 18), np.nan)
    prefixes = {n: raw.copy() for n in protocol["prefixes"]}
    for fold in range(5):
        train, valid = np.flatnonzero(assignments != fold), np.flatnonzero(assignments == fold)
        from .inference import load_model
        gate = read_json(run / "G2.json")
        name = f"S_fold_{fold}.joblib"
        model = load_model(run / name, gate["files"][name])
        raw[valid] = model.predict_proba(frame.text.iloc[valid].tolist())
        for n, p in prefixes.items():
            p[valid] = model.predict_proba([transform(t, f"prefix-{n}") for t in frame.text.iloc[valid]])
    lengths = frame.text.str.split().str.len().to_numpy()
    comparisons = {}
    for n, p in prefixes.items():
        comparisons[str(n)] = {}
        for subset, mask in {"eligible": lengths >= n, "common_120": lengths >= 120}.items():
            comparisons[str(n)][subset] = {"row_ids": frame.id.loc[mask].tolist(), "view_version": VERSION, "perturbed": supported_report(frame.loc[mask], p[mask]),
                                          "raw": supported_report(frame.loc[mask], raw[mask]), "refitted": False}
    write_json(output / "artifact_report.json", {"controls": tables, "prefixes": comparisons,
               "limitations": ["Formatting transforms can damage code/math", "Masking preserves length; rate features may indirectly encode length"],
               "budget_note": "60 fixed-C diagnostic fits; primary prefix perturbations reuse G2 outer S models with inner-selected C"})
    write_json(output / "manifest.json", {"execution": execution(), "view_version": VERSION, "run_hash": digest(run / "G2.json"),
               "development_manifest_hash": digest(root / "manifest.json"),
               "files": {p.name: digest(p) for p in output.iterdir() if p.is_file()}})


def topic_stress(root: Path, output: Path, *, encoder=None, neural_gate: Path | None = None) -> None:
    frame = load_development(root)
    if output.exists():
        raise ValueError("Preserve existing topic diagnostics")
    output.mkdir(parents=True)
    if encoder is None:
        write_json(output / "topic_report.json", {"status": "blocked", "reason": "No verified frozen topic representation; not passed"})
        _topic_manifest(root, output, execution(), {})
        return
    revision = source_revision()
    eligible, costs = eligibility(root, neural_gate, encoder)
    vectors = encoder.cache(frame, output / "cache", view="format-stripped", allowed_ids=set(frame.id))
    prompt_vectors: Any = pd.DataFrame(vectors).assign(prompt_id=frame.prompt_id.to_numpy()).groupby("prompt_id").mean()
    clusters = KMeans(n_clusters=6, n_init=cast(Any, 50), random_state=2027).fit_predict(prompt_vectors)
    membership = dict(zip(prompt_vectors.index, clusters.tolist()))
    assignments = frame.prompt_id.map(membership).to_numpy()
    np.save(output / "prompt_vectors.npy", prompt_vectors.to_numpy(), allow_pickle=False)
    write_json(output / "clusters.json", {"membership": membership, "seed": 2027, "n_init": 50})
    log = ExperimentLog(output / "experiment_registry.jsonl", 228)
    log.cache_embeddings(frame, encoder, output / "raw_cache")
    oof = {a: np.full((len(frame), 18), np.nan) for a in eligible["eligible"]}
    fold_reports = []
    for fold in range(6):
        train, valid = np.flatnonzero(assignments != fold), np.flatnonzero(assignments == fold)
        assert_split(frame, train, valid)
        training = frame.iloc[train].reset_index(drop=True)
        inner_assignments = folds(training, 4)
        pd.DataFrame({"id": training.id.tolist(), "fold": inner_assignments}).to_csv(output / f"inner_folds_{fold}.csv", index=False)
        inner = inner_predictions(training, inner_assignments, log, encoder=encoder)
        _, selected = choose(configurations(inner, training.model), costs)
        scores = {}
        for a, config in selected.items():
            model = log.fit(training, config, encoder=encoder, role="diagnostic")
            oof[a][valid] = log.predict(model, frame.iloc[valid])
            scores[a] = supported_report(frame.iloc[valid], oof[a][valid])
        fold_reports.append({"selected": selected, "cluster": fold, "rows": len(valid), "prompts": len(set(frame.prompt_id.iloc[valid])), "scores": scores})
    for a, p in oof.items():
        np.save(output / f"{a}.npy", probabilities(p), allow_pickle=False)
    write_json(output / "topic_report.json", {"status": "completed", "clusters": fold_reports,
               "pooled": {a: report(frame.model, p) for a, p in oof.items()},
               "development_manifest_hash": digest(root / "manifest.json"),
               "caveat": "Transductive topic-proxy stress partition; style may remain; not independent semantic domains"})
    write_json(output / "rows.json", {"ids": frame.id.tolist(), "folds": assignments.tolist(), "source_revision": revision})
    _topic_manifest(root, output, execution(encoder), lineage({"G1a": root / "G1a.json", **({"G1b": neural_gate} if neural_gate else {})}))


def robustness_veto(frame, sparse, challenger, topic: dict, architecture: str) -> dict:
    s, c = report(frame.model, sparse), report(frame.model, challenger)
    recall_differences = {label: c["recall"][label] - s["recall"][label] for label in CLASSES}
    remaining = {}
    sp, cp = np.asarray(CLASSES)[sparse.argmax(axis=1)], np.asarray(CLASSES)[challenger.argmax(axis=1)]
    for provider in sorted(set(PROVIDER.values())):
        classes = [label for label in CLASSES if PROVIDER[label] != provider]
        mask = np.array([PROVIDER[label] != provider for label in frame.model])
        # Cross-provider mistakes still count as errors, even if predicted labels
        # belong to the removed provider. Compute recalls directly.
        y = frame.model.to_numpy()[mask]
        remaining[provider] = float(np.mean([np.mean(cp[mask][y == label] == label) -
                                              np.mean(sp[mask][y == label] == label) for label in classes]))
    topic_gain = None
    if topic["status"] == "completed":
        topic_gain = topic["pooled"][architecture]["balanced_accuracy"] - topic["pooled"]["S"]["balanced_accuracy"]
    passed = (c["balanced_accuracy"] - s["balanced_accuracy"] >= .03 - 1e-12 and
              min(recall_differences.values()) >= -.10 - 1e-12 and min(remaining.values()) >= -1e-12 and
              topic_gain is not None and topic_gain >= -.02 - 1e-12)
    return {"passed": passed, "recall_differences": recall_differences,
            "leave_provider_gain": remaining, "topic_gain": topic_gain}


def _topic_manifest(root: Path, output: Path, current: dict, upstream: dict) -> None:
    write_json(output / "manifest.json", {"execution": current, "upstream": upstream,
        "view_version": VERSION, "development_manifest_hash": digest(root / "manifest.json"),
        "files": {p.relative_to(output).as_posix(): digest(p) for p in output.rglob("*") if p.is_file()}}, exclusive=True)


def verify_topic(root: Path, path: Path, frame, current: dict, upstream: dict) -> dict:
    manifest = read_json(path.parent / "manifest.json")
    verify_files(path.parent, manifest["files"])
    if path.name != "topic_report.json" or path.name not in manifest["files"]:
        raise ValueError("Unbound topic report")
    if manifest["development_manifest_hash"] != digest(root / "manifest.json") or manifest["view_version"] != VERSION:
        raise ValueError("Stale topic data/view identity")
    topic = read_json(path)
    if topic["status"] == "blocked":
        assert_execution(manifest.get("execution", {}), execution())
        return topic
    if topic["status"] != "completed":
        raise ValueError("Unknown topic evidence status")
    assert_execution(manifest.get("execution", {}), current)
    if manifest["upstream"] != upstream:
        raise ValueError("Topic upstream eligibility drift")
    if topic.get("development_manifest_hash") != digest(root / "manifest.json"):
        raise ValueError("Topic report data identity drift")
    rows = read_json(path.parent / "rows.json")
    if rows["ids"] != frame.id.tolist():
        raise ValueError("Topic prediction row identity mismatch")
    assignments = np.asarray(rows["folds"])
    if len(assignments) != len(frame) or set(assignments) != set(range(6)):
        raise ValueError("Invalid topic fold membership")
    membership = read_json(path.parent / "clusters.json")["membership"]
    if frame.prompt_id.map(membership).tolist() != rows["folds"]:
        raise ValueError("Topic cluster alignment mismatch")
    for fold in range(6):
        train, valid = np.flatnonzero(assignments != fold), np.flatnonzero(assignments == fold)
        assert_split(frame, train, valid)
        training = frame.iloc[train].reset_index(drop=True)
        inner = fold_assignments(training, pd.read_csv(path.parent / f"inner_folds_{fold}.csv", dtype={"id": str}))
        if set(inner) != set(range(4)):
            raise ValueError("Invalid persisted topic inner folds")
        for i in range(4):
            assert_split(training, np.flatnonzero(inner != i), np.flatnonzero(inner == i))
    for a, metrics in topic["pooled"].items():
        name = f"{a}.npy"
        if a not in ("S", "F", "H") or name not in manifest["files"]:
            raise ValueError("Missing registered topic predictions")
        p = np.load(path.parent / name, allow_pickle=False)
        if report(frame.model, p) != metrics:
            raise ValueError("Topic metrics disagree with persisted predictions")
        for fold in range(6):
            mask = assignments == fold
            actual = supported_report(frame.loc[mask], p[mask])
            if topic["clusters"][fold]["cluster"] != fold or topic["clusters"][fold]["scores"][a] != actual:
                raise ValueError("Topic per-cluster metrics disagree with predictions")
    return topic
