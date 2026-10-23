"""Selection consumes only inner OOF predictions and their inner labels."""
from __future__ import annotations

import numpy as np

from .evaluation import report
from .models import probabilities


def configurations(inner_probabilities: dict, labels) -> list[dict]:
    result = []
    for (architecture, c), p in inner_probabilities.items():
        if architecture not in ("S", "F") or c not in (.5, 1, 2, 4):
            raise ValueError("Unregistered candidate")
        result.append({"config": {"architecture": architecture, "C": c},
                       "score": report(labels, p)["balanced_accuracy"]})
    if any(a == "F" for a, _ in inner_probabilities):
        for sc in (.5, 1, 2, 4):
            for fc in (.5, 1, 2, 4):
                for w in [i / 10 for i in range(1, 10)]:
                    p = probabilities(w * inner_probabilities["S", sc] + (1-w) * inner_probabilities["F", fc])
                    result.append({"config": {"architecture": "H", "sparse_C": sc, "frozen_C": fc, "weight": w},
                                   "score": report(labels, p)["balanced_accuracy"]})
    return result


def cost_key(config: dict, costs: dict) -> tuple:
    a = config["architecture"]
    return (costs[a], 2 if a == "H" else 1, config.get("C", config.get("sparse_C")),
            config.get("frozen_C", 0), -config.get("weight", 1 if a == "S" else 0))


def choose(candidates: list[dict], costs: dict) -> tuple[dict, dict[str, dict]]:
    if any(row["config"]["architecture"] not in ("S", "F", "H") for row in candidates):
        raise ValueError("Unregistered selection architecture")
    if any(not np.isfinite(value) or value <= 0 for value in costs.values()):
        raise ValueError("Selection costs must be measured finite positive values")
    if any(not np.isfinite(row["score"]) for row in candidates):
        raise ValueError("Nonfinite selection score")
    best = {}
    for architecture in ("S", "F", "H"):
        rows = [r for r in candidates if r["config"]["architecture"] == architecture]
        if rows:
            maximum = max(r["score"] for r in rows)
            best[architecture] = min([r for r in rows if r["score"] >= maximum - 1e-12],
                                     key=lambda r: cost_key(r["config"], costs))
    if "S" not in best:
        raise ValueError("Sparse anchor required")
    eligible = [r for r in candidates if r["config"]["architecture"] != "S"
                and r["score"] >= best["S"]["score"] + .03 - 1e-12]
    winner = best["S"]
    if eligible:
        maximum = max(r["score"] for r in eligible)
        winner = min([r for r in eligible if r["score"] >= maximum - .005 - 1e-12],
                     key=lambda r: cost_key(r["config"], costs))
    return winner["config"], {a: r["config"] for a, r in best.items()}
