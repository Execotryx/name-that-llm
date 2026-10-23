"""Fixed-label metrics and prompt-group conditional uncertainty."""
from __future__ import annotations

import numpy as np
from sklearn.metrics import confusion_matrix

from .labels import CLASSES, PROVIDER
from .models import probabilities


def metrics(truth, predicted, classes=CLASSES) -> dict:
    y, p = np.asarray(truth), np.asarray(predicted)
    if y.shape != p.shape or y.ndim != 1 or not set(y) <= set(classes) or not set(p) <= set(classes):
        raise ValueError("Invalid evaluation labels")
    support = np.array([(y == c).sum() for c in classes])
    if (support == 0).any():
        raise ValueError("Primary macro recall requires every true class")
    recall = np.array([((y == c) & (p == c)).sum() for c in classes]) / support
    return {"balanced_accuracy": float(recall.mean()), "support": dict(zip(classes, support.tolist())),
            "recall": dict(zip(classes, recall.tolist())),
            "confusion": confusion_matrix(y, p, labels=classes, normalize="true").tolist()}


def report(truth, p) -> dict:
    labels = np.asarray(CLASSES)[probabilities(p).argmax(axis=1)]
    result = metrics(truth, labels)
    result["provider"] = metrics([PROVIDER[y] for y in truth], [PROVIDER[y] for y in labels],
                                 sorted(set(PROVIDER.values())))
    result["sibling_confusion_policy"] = "18-column confusion retains cross-provider errors"
    return result


def paired_uncertainty(truth, a, b, groups, *, bootstrap: int = 10000,
                       permutations: int = 100000, seed: int = 2027) -> dict:
    y, a, b, groups = map(np.asarray, (truth, a, b, groups))
    if not (len(y) == len(a) == len(b) == len(groups)):
        raise ValueError("Unaligned uncertainty inputs")
    observed = metrics(y, a)["balanced_accuracy"] - metrics(y, b)["balanced_accuracy"]
    unique = np.unique(groups)
    support = np.zeros((len(unique), 18))
    correct_a, correct_b = support.copy(), support.copy()
    for i, group in enumerate(unique):
        for k, label in enumerate(CLASSES):
            mask = (groups == group) & (y == label)
            support[i, k] = mask.sum()
            correct_a[i, k] = (a[mask] == y[mask]).sum()
            correct_b[i, k] = (b[mask] == y[mask]).sum()
    rng = np.random.default_rng(seed)
    differences, invalid = [], 0
    for _ in range(bootstrap):
        sampled = rng.integers(0, len(unique), len(unique))
        denominator = support[sampled].sum(axis=0)
        if (denominator == 0).any():
            invalid += 1
            continue
        differences.append(float(((correct_a[sampled].sum(axis=0) - correct_b[sampled].sum(axis=0)) / denominator).mean()))
    if not differences:
        raise ValueError("No valid bootstrap replicates")
    contributions = ((correct_a - correct_b) / (18 * support.sum(axis=0))).sum(axis=1)
    extreme = 0
    for start in range(0, permutations, 1000):
        signs = rng.choice([-1, 1], size=(min(1000, permutations - start), len(unique)))
        extreme += int((np.abs(signs @ contributions) >= abs(observed) - 1e-12).sum())
    return {"difference_pp": observed * 100, "interval_pp": (np.percentile(differences, [2.5, 97.5]) * 100).tolist(),
            "p_value": (extreme + 1) / (permutations + 1), "invalid_bootstrap": invalid,
            "bootstrap": bootstrap, "permutations": permutations,
            "caveat": "Conditional on fixed predictions; not selection-adjusted; CV fits share training data. Small holdouts do not establish equivalence."}


def holm(p_values: dict[str, float]) -> dict[str, float]:
    result, previous = {}, 0.0
    for i, (name, p) in enumerate(sorted(p_values.items(), key=lambda item: item[1])):
        previous = max(previous, min(1.0, (len(p_values) - i) * p))
        result[name] = previous
    return result
