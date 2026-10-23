"""S, frozen F and registered probability blend H; no metadata at inference."""
from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import Any, Sequence

import numpy as np
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from .features import sparse_features
from .labels import CLASSES
from .views import transform


def texts_only(texts: Sequence[str]) -> list[str]:
    if isinstance(texts, (str, bytes)) or any(not isinstance(t, str) for t in texts):
        raise ValueError("Expected a sequence of strings, no null values")
    return list(texts)


def probabilities(values, classes=CLASSES) -> np.ndarray:
    p = np.asarray(values, dtype=float)
    if p.ndim != 2 or p.shape[1] != len(CLASSES) or set(classes) != set(CLASSES):
        raise ValueError("Expected 18 canonical probability columns")
    p = p[:, [list(classes).index(c) for c in CLASSES]]
    if not np.isfinite(p).all() or (p < 0).any() or not np.allclose(p.sum(axis=1), 1, atol=1e-6, rtol=0):
        raise ValueError("Invalid probabilities (margins are not probabilities)")
    return p


def logistic(c: float, iterations: int = 2500):
    if c not in (.5, 1, 2, 4):
        raise ValueError("Unregistered C")
    # The default penalty is L2; omitting the deprecated penalty argument also
    # supports newer sklearn releases without changing the representation.
    return LogisticRegression(C=c, solver="saga", max_iter=iterations, random_state=2027)


def fit_checked(estimator, x, labels) -> None:
    # Predeclared uniform remedy: retry the same fit at 10,000 iterations.
    attempts = []
    for ceiling in (2500, 10000):
        parameter = "classifier__max_iter" if isinstance(estimator, Pipeline) else "max_iter"
        estimator.set_params(**{parameter: ceiling})
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always", ConvergenceWarning)
            estimator.fit(x, labels)
        messages = [str(w.message) for w in caught if issubclass(w.category, ConvergenceWarning)]
        attempts.append({"ceiling": ceiling, "converged": not messages, "warnings": messages})
        setattr(estimator, "convergence_log_", attempts)
        if not messages:
            return
    raise ValueError(f"Unresolved convergence after registered uniform remedy: {attempts}")


@dataclass
class TextClassifier:
    estimator: Any
    config: dict
    encoder: Any = None
    sparse: Any = None
    frozen: Any = None

    def predict_proba(self, texts: Sequence[str]) -> np.ndarray:
        raw = texts_only(texts)
        if not raw:
            return np.empty((0, len(CLASSES)))
        if self.config["architecture"] == "H":
            w = self.config["weight"]
            return probabilities(w * self.sparse.predict_proba(raw) + (1 - w) * self.frozen.predict_proba(raw))
        viewed = [transform(t, self.config.get("view", "raw")) for t in raw]
        x = self.encoder.encode(viewed) if self.encoder is not None else viewed
        return probabilities(self.estimator.predict_proba(x), self.estimator.classes_)

    def predict(self, texts: Sequence[str]) -> list[str]:
        return [CLASSES[i] for i in self.predict_proba(texts).argmax(axis=1)]


def fit_model(texts: Sequence[str], labels: Sequence[str], config: dict, *, encoder=None,
              embeddings=None) -> TextClassifier:
    raw = texts_only(texts)
    if len(raw) != len(labels) or set(labels) != set(CLASSES):
        raise ValueError("Fit requires aligned texts and all canonical labels")
    architecture = config["architecture"]
    allowed = {"architecture", "sparse_C", "frozen_C", "weight"} if architecture == "H" else {"architecture", "C", "view"}
    if not set(config) <= allowed:
        raise ValueError("Unregistered model parameters")
    if architecture == "H":
        if config["weight"] not in [i / 10 for i in range(11)]:
            raise ValueError("Unregistered blend weight")
        s = fit_model(raw, labels, {"architecture": "S", "C": config["sparse_C"]})
        f = fit_model(raw, labels, {"architecture": "F", "C": config["frozen_C"]}, encoder=encoder, embeddings=embeddings)
        return TextClassifier(None, dict(config), sparse=s, frozen=f)
    viewed = [transform(t, config.get("view", "raw")) for t in raw]
    if architecture == "S":
        estimator = Pipeline([("features", sparse_features()), ("classifier", logistic(config["C"]))])
        x = viewed
    elif architecture == "F" and encoder is not None:
        estimator = logistic(config["C"])
        x = encoder.encode(viewed) if embeddings is None else np.asarray(embeddings)
        if x.ndim != 2 or len(x) != len(raw) or not np.isfinite(x).all():
            raise ValueError("Invalid aligned training embeddings")
    else:
        raise ValueError("Unregistered architecture or missing eligible encoder")
    fit_checked(estimator, x, labels)
    return TextClassifier(estimator, dict(config), encoder=encoder if architecture == "F" else None)
