"""Lossless CSV parsing, source audit and development allowlists."""
from __future__ import annotations

import csv
from difflib import SequenceMatcher
from itertools import combinations
from pathlib import Path

import pandas as pd

from .common import digest, read_json, record, verify_files, write_json
from .labels import CLASSES

TRAIN_COLUMNS = ["id", "prompt_id", "text", "model"]


def read_csv(path: str | Path, columns: list[str]) -> pd.DataFrame:
    # csv distinguishes a missing trailing field (None) from a literal empty string.
    with Path(path).open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != columns:
            raise ValueError(f"Expected ordered columns {columns}, got {reader.fieldnames}")
        rows = list(reader)
    if any(None in row or any(v is None for v in row.values()) for row in rows):
        raise ValueError("Missing or extra CSV fields")
    frame = pd.DataFrame(rows, columns=columns, dtype="string")
    validate(frame, training="model" in columns)
    return frame


def validate(frame: pd.DataFrame, *, training: bool = False) -> None:
    required = TRAIN_COLUMNS if training else ["id", "text"]
    if not set(required) <= set(frame.columns):
        raise ValueError(f"Required columns: {required}")
    for column in required:
        if any(not isinstance(x, str) for x in frame[column]):
            raise ValueError(f"{column} must contain strings, no nulls")
        if column != "text" and any(not x.strip() for x in frame[column]):
            raise ValueError(f"Empty {column}")
    if frame.id.duplicated().any():
        raise ValueError("IDs must be unique")
    if training:
        if set(frame.model) != set(CLASSES):
            raise ValueError("Training requires the exact 18 labels")
        if frame.duplicated(["prompt_id", "model"]).any():
            raise ValueError("Duplicate prompt/model pair")


def audit(frame: pd.DataFrame, source: Path) -> dict:
    validate(frame, training=True)
    normalized = [" ".join(t.split()) for t in frame.text]
    # Fixed, label-independent rule: normalized sequence similarity >= .95.
    links = []
    for i, j in combinations(range(len(frame)), 2):
        a, b = normalized[i], normalized[j]
        if frame.prompt_id.iloc[i] == frame.prompt_id.iloc[j]:
            continue
        if max(len(a), len(b)) and min(len(a), len(b)) / max(len(a), len(b)) < .905:
            continue
        matcher = SequenceMatcher(None, a, b, autojunk=False)
        if matcher.quick_ratio() >= .95 and matcher.ratio() >= .95:
            links.append([str(frame.id.iloc[i]), str(frame.id.iloc[j])])
    words = frame.text.str.split().str.len()
    missing = [[str(p), c] for p, rows in frame.groupby("prompt_id")
               for c in CLASSES if c not in set(rows.model)]
    return {"sha256": digest(source), "rows": len(frame), "prompts": frame.prompt_id.nunique(),
            "class_counts": frame.model.value_counts().to_dict(), "missing_pairs": missing,
            "exact_duplicates": int(frame.text.duplicated().sum()),
            "normalized_duplicates": len(normalized) - len(set(normalized)),
            "word_count": {"min": int(words.min()), "max": int(words.max()), "median": float(words.median())},
            "near_duplicate_rule": "whitespace-normalized SequenceMatcher >= .95, autojunk=False",
            "cross_prompt_links": links}


def load_development(root: str | Path) -> pd.DataFrame:
    root = Path(root)
    manifest = read_json(root / "manifest.json")
    try:
        verify_files(root, manifest["files"])
        frame = read_csv(root / "development.csv", TRAIN_COLUMNS)
        allowed = set(manifest["development_ids"])
        if set(frame.id) != allowed or set(frame.id) & set(manifest["locked_ids"]):
            raise ValueError("Development input violates role allowlist")
    except Exception as error:
        record(root / "access.jsonl", action="development", status="denied", reason=str(error))
        raise
    record(root / "access.jsonl", action="development", status="allowed", rows=len(frame))
    return frame


def check_source(path: Path, expected: str, report: Path) -> None:
    actual = digest(path)
    if actual != expected:
        write_json(report, {"expected": expected, "actual": actual, "status": "source_discrepancy"}, exclusive=True)
        raise ValueError("Source integrity discrepancy; register a versioned amendment")
