"""Registered artifact interventions and development-only topic-proxy stress."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from typing import Any, cast
from sklearn.cluster import KMeans
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from .common import digest, identity, read_json, record, write_json
from .data import load_development
from .evaluation import metrics, report
from .features import sparse_features, style_features
from .gates import require_gate
from .labels import CLASSES, PROVIDER
from .models import fit_checked, logistic, probabilities
from .protocol import registered
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
    require_gate(run / "G2.json", "G2", digest(root / "manifest.json"))
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
        tables[name] = {**supported_report(frame, p), "refitted": True, "C": 2, "view_version": VERSION}
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
            comparisons[str(n)][subset] = {"perturbed": supported_report(frame.loc[mask], p[mask]),
                                          "raw": supported_report(frame.loc[mask], raw[mask]), "refitted": False}
    write_json(output / "artifact_report.json", {"controls": tables, "prefixes": comparisons,
               "limitations": ["Formatting transforms can damage code/math", "Masking preserves length; rate features may indirectly encode length"],
               "budget_note": "60 fixed-C diagnostic fits; primary prefix perturbations reuse G2 outer S models with inner-selected C"})
    write_json(output / "manifest.json", {"run_hash": digest(run / "G2.json"),
               "development_manifest_hash": digest(root / "manifest.json"),
               "files": {p.name: digest(p) for p in output.iterdir() if p.is_file()}})


def topic_stress(root: Path, output: Path, *, encoder=None, neural_gate: Path | None = None) -> None:
    frame = load_development(root)
    if output.exists():
        raise ValueError("Preserve existing topic diagnostics")
    output.mkdir(parents=True)
    if encoder is None:
        write_json(output / "topic_report.json", {"status": "blocked", "reason": "No verified frozen topic representation; not passed"})
        return
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
        inner = inner_predictions(training, folds(training, 4), log, encoder=encoder)
        _, selected = choose(configurations(inner, training.model), costs)
        scores = {}
        for a, config in selected.items():
            model = log.fit(training, config, encoder=encoder, role="diagnostic")
            oof[a][valid] = log.predict(model, frame.iloc[valid])
            scores[a] = supported_report(frame.iloc[valid], oof[a][valid])
        fold_reports.append({"cluster": fold, "rows": len(valid), "prompts": len(set(frame.prompt_id.iloc[valid])), "scores": scores})
    for a, p in oof.items():
        np.save(output / f"{a}.npy", probabilities(p), allow_pickle=False)
    write_json(output / "topic_report.json", {"status": "completed", "clusters": fold_reports,
               "pooled": {a: report(frame.model, p) for a, p in oof.items()},
               "development_manifest_hash": digest(root / "manifest.json"),
               "caveat": "Transductive topic-proxy stress partition; style may remain; not independent semantic domains"})


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
