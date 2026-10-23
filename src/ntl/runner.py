"""Finite grouped nested selection; validation labels stay outside selection calls."""
from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import pandas as pd
import joblib

from .common import digest, identity, read_json, record, source_revision, write_json
from .data import load_development
from .evaluation import holm, paired_uncertainty, report
from .gates import require_gate
from .labels import CLASSES
from .models import fit_model, probabilities
from .protocol import registered
from .selection import choose, configurations
from .splits import assert_split


class ExperimentLog:
    def __init__(self, path: Path, maximum: int):
        if path.exists():
            raise ValueError("Run ID already exists; preserve failed runs")
        self.path, self.maximum, self.count = path, maximum, 0
        self.embeddings: dict = {}

    def cache_embeddings(self, frame, encoder, directory: Path):
        vectors = encoder.cache(frame, directory, view="raw", allowed_ids=set(frame.id))
        self.embeddings = dict(zip(frame.id, vectors))

    def predict(self, model, frame):
        if model.config["architecture"] == "H":
            w = model.config["weight"]
            return probabilities(w*self.predict(model.sparse, frame) + (1-w)*self.predict(model.frozen, frame))
        if model.config["architecture"] == "F" and self.embeddings:
            return probabilities(model.estimator.predict_proba(np.stack([self.embeddings[i] for i in frame.id])), model.estimator.classes_)
        return model.predict_proba(frame.text.tolist())

    def fit(self, frame, config, *, encoder=None, role="selection"):
        if self.count >= self.maximum:
            raise ValueError("Registered fit budget exhausted")
        self.count += 1
        start = time.perf_counter()
        fields = dict(experiment_id=self.count, hypothesis="registered-v1", role=role,
                      parameters=config, seed=2027, training_ids=frame.id.tolist(),
                      permitted_inputs="development-only", maximum_fits=self.maximum)
        record(self.path, status="started", **fields)
        try:
            embeddings = np.stack([self.embeddings[i] for i in frame.id]) if self.embeddings and config["architecture"] in ("F", "H") else None
            model = fit_model(frame.text.tolist(), frame.model.tolist(), config, encoder=encoder, embeddings=embeddings)
        except Exception as error:
            record(self.path, status="failed", reason=str(error), **fields)
            raise
        estimators = ([model.sparse.estimator, model.frozen.estimator] if config["architecture"] == "H" else [model.estimator])
        convergence = []
        for estimator in estimators:
            from sklearn.pipeline import Pipeline
            classifier = estimator.named_steps["classifier"] if isinstance(estimator, Pipeline) else estimator
            convergence.append({"iterations": classifier.n_iter_.tolist(), "attempts": getattr(estimator, "convergence_log_")})
        record(self.path, status="completed", fit_seconds=time.perf_counter()-start, convergence=convergence, **fields)
        return model


def fold_assignments(frame, table: pd.DataFrame) -> np.ndarray:
    if table.id.duplicated().any() or set(table.id) != set(frame.id):
        raise ValueError("Fold membership mismatch")
    return table.set_index("id").loc[frame.id, "fold"].to_numpy(dtype=int)


def inner_predictions(frame, assignments, log, *, encoder=None) -> dict:
    if set(assignments) != set(range(4)):
        raise ValueError("Expected four registered inner folds")
    predictions = {}
    for architecture in (["S", "F"] if encoder is not None else ["S"]):
        for c in (.5, 1, 2, 4):
            p = np.full((len(frame), 18), np.nan)
            for fold in range(4):
                train, valid = np.flatnonzero(assignments != fold), np.flatnonzero(assignments == fold)
                assert_split(frame, train, valid)
                model = log.fit(frame.iloc[train], {"architecture": architecture, "C": c}, encoder=encoder)
                p[valid] = log.predict(model, frame.iloc[valid])
            predictions[architecture, c] = probabilities(p)
    return predictions


def eligibility(root: Path, neural_gate: Path | None, encoder):
    manifest_hash = digest(root / "manifest.json")
    cpu = require_gate(root / "G1a.json", "G1a", manifest_hash)
    costs = {"S": cpu["inference_seconds"]}
    if neural_gate is None:
        if encoder is not None:
            raise ValueError("Encoder requires G1b")
        return {"eligible": ["S"], "not_evaluated": ["F", "H"],
                "reason": "No passing G1b evidence; neural comparisons not run"}, costs
    neural = require_gate(neural_gate, "G1b", manifest_hash)
    if encoder is None or neural["encoder_hash"] != identity(encoder.manifest):
        raise ValueError("G1b asset identity mismatch")
    costs["F"] = neural["inference_seconds"]
    costs["H"] = costs["S"] + costs["F"]
    return {"eligible": ["S", "F", "H"], "not_evaluated": []}, costs


def evaluate(root: Path, output: Path, *, encoder=None, neural_gate: Path | None = None) -> None:
    revision = source_revision()
    protocol = registered(root)
    frame = load_development(root)
    eligible, costs = eligibility(root, neural_gate, encoder)
    if output.exists():
        raise ValueError("Use a fresh run directory")
    output.mkdir(parents=True)
    write_json(output / "eligibility.json", eligible)
    write_json(output / "run.json", {"source_revision": revision, "protocol_hash": identity(protocol),
               "development_manifest_hash": digest(root / "manifest.json"), "costs": costs})
    log = ExperimentLog(output / "experiment_registry.jsonl", 190)
    if encoder is not None:
        log.cache_embeddings(frame, encoder, output / "embedding_cache")
    outer = fold_assignments(frame, pd.read_csv(root / "outer_folds.csv", dtype={"id": str}))
    if set(outer) != set(range(5)):
        raise ValueError("Expected five outer folds")
    inner_table = pd.read_csv(root / "inner_folds.csv", dtype={"id": str})
    oof = {a: np.full((len(frame), 18), np.nan) for a in eligible["eligible"] + ["selector"]}
    selections = []
    for fold in range(5):
        train, valid = np.flatnonzero(outer != fold), np.flatnonzero(outer == fold)
        assert_split(frame, train, valid)
        training = frame.iloc[train].reset_index(drop=True)
        assignments = fold_assignments(training, inner_table.loc[inner_table.outer_fold == fold])
        inner = inner_predictions(training, assignments, log, encoder=encoder)
        selected, candidates = choose(configurations(inner, training.model), costs)
        candidates["selector"] = selected
        selections.append({"fold": fold, "selected": selected, "candidates": candidates})
        fitted = {}
        for architecture, config in candidates.items():
            # Deduplicate component fits shared by H and single-branch candidates.
            components = ([{"architecture": "S", "C": config["sparse_C"]},
                           {"architecture": "F", "C": config["frozen_C"]}]
                          if config["architecture"] == "H" else [config])
            for component in components:
                key = identity(component)
                if key not in fitted:
                    fitted[key] = log.fit(training, component, encoder=encoder)
            predicted = [log.predict(fitted[identity(c)], frame.iloc[valid]) for c in components]
            oof[architecture][valid] = (config["weight"] * predicted[0] + (1-config["weight"]) * predicted[1]
                                         if len(predicted) == 2 else predicted[0])
            if architecture == "S":
                joblib.dump(fitted[identity(config)], output / f"S_fold_{fold}.joblib")
    results = {}
    for a, p in oof.items():
        probabilities(p)
        np.save(output / f"{a}_oof.npy", p, allow_pickle=False)
        results[a] = report(frame.model, p)
        results[a]["folds_descriptive"] = [report(frame.model.loc[outer == fold], p[outer == fold])["balanced_accuracy"] for fold in range(5)]
        results[a]["fold_mean"] = float(np.mean(results[a]["folds_descriptive"]))
        results[a]["fold_sd"] = float(np.std(results[a]["folds_descriptive"], ddof=1))
        results[a]["fold_caveat"] = "Overlapping training sets; these folds are not independent experiments"
    paired = {}
    s = np.asarray(CLASSES)[oof["S"].argmax(axis=1)]
    for a in ("F", "H"):
        if a in oof:
            paired[a] = paired_uncertainty(frame.model, np.asarray(CLASSES)[oof[a].argmax(axis=1)], s, frame.prompt_id)
    write_json(output / "paired.json", {"comparisons": paired, "holm": holm({a: v["p_value"] for a, v in paired.items()})})
    write_json(output / "metrics.json", results)
    write_json(output / "selections.json", selections)
    # A CSV view keeps all starts, failures and retries visible to basic tools.
    import json
    pd.DataFrame([json.loads(line) for line in log.path.read_text().splitlines()]).to_csv(output / "experiment_registry.csv", index=False)
    write_json(output / "G3.json", {"gate": "G3", "status": "passed", "source_revision": revision,
               "development_manifest_hash": digest(root / "manifest.json"), "eligibility": eligible,
               "scope": "nested S/F/H" if encoder is not None else "S-only eligibility; F/H not evaluated",
               "files": {name: digest(output / name) for name in ("eligibility.json", "metrics.json", "selections.json")}}, exclusive=True)
    write_json(output / "G2.json", {"gate": "G2", "status": "passed", "source_revision": revision,
               "development_manifest_hash": digest(root / "manifest.json"),
               "files": {p.relative_to(output).as_posix(): digest(p) for p in output.rglob("*") if p.is_file()}}, exclusive=True)
