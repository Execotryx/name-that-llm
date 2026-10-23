"""Persisted nested grouped partitions and leakage checks."""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold

from .labels import CLASSES


def assert_split(frame: pd.DataFrame, train: np.ndarray, valid: np.ndarray) -> None:
    if set(train) & set(valid) or set(frame.prompt_id.iloc[train]) & set(frame.prompt_id.iloc[valid]):
        raise ValueError("Prompt overlap")
    if set(frame.model.iloc[train]) != set(CLASSES) or set(frame.model.iloc[valid]) != set(CLASSES):
        raise ValueError("Every evaluation side requires all classes")


def folds(frame: pd.DataFrame, count: int) -> np.ndarray:
    result = np.full(len(frame), -1, dtype=int)
    splitter = StratifiedGroupKFold(count, shuffle=True, random_state=2027)
    for fold, (train, valid) in enumerate(splitter.split(frame.text, frame.model, frame.prompt_id)):
        assert_split(frame, train, valid)
        result[valid] = fold
    if (result < 0).any():
        raise ValueError("Incomplete fold coverage")
    return result


def manifests(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    outer = pd.DataFrame(frame[["id"]]).copy()
    outer["fold"] = folds(frame, 5)
    inner = []
    for fold in range(5):
        subset = frame.loc[outer.fold != fold].reset_index(drop=True)
        item = subset[["id"]].copy()
        item["outer_fold"] = fold
        item["fold"] = folds(subset, 4)
        inner.append(item)
    final = pd.DataFrame(frame[["id"]]).copy()
    final["fold"] = folds(frame, 4)
    return outer, pd.concat(inner, ignore_index=True), final
