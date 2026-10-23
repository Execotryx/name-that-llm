"""Strict ID-preserving submission adapter and trusted artifact loading."""
from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from .common import digest
from .data import validate
from .labels import CLASSES

SCHEMA = pa.schema([pa.field("id", pa.string()), pa.field("model", pa.string())])


def load_model(path: str | Path, expected_sha256: str):
    if digest(path) != expected_sha256:
        raise ValueError("Model hash mismatch")
    # Only call with a trusted manifest and locally authored model: hashes alone
    # do not make pickle safe against a malicious publisher.
    return joblib.load(path)


def build_submission(test_frame: pd.DataFrame, predictor, schema=SCHEMA, *, batch_size: int = 64) -> pd.DataFrame:
    validate(test_frame)
    if batch_size < 1 or schema != SCHEMA:
        raise ValueError("Invalid submission schema or batch size")
    labels = []
    for start in range(0, len(test_frame), batch_size):
        labels.extend(predictor.predict(test_frame.text.iloc[start:start + batch_size].tolist()))
    if len(labels) != len(test_frame) or not set(labels) <= set(CLASSES):
        raise ValueError("Invalid model output")
    return pd.DataFrame({"id": test_frame.id.tolist(), "model": labels}, dtype="string")


def write_submission(path: str | Path, frame: pd.DataFrame) -> None:
    if list(frame.columns) != ["id", "model"] or frame.isna().any().any():
        raise ValueError("Invalid submission fields")
    if frame.id.duplicated().any() or any(not isinstance(i, str) or not i.strip() for i in frame.id):
        raise ValueError("Invalid submission IDs")
    if not set(frame.model) <= set(CLASSES):
        raise ValueError("Invalid labels")
    table = pa.Table.from_pandas(frame, schema=SCHEMA, preserve_index=False)
    pq.write_table(table, path)
    restored = pq.read_table(path)
    if not restored.schema.remove_metadata().equals(SCHEMA) or restored.to_pydict() != table.to_pydict():
        raise ValueError("Parquet round-trip mismatch")


def independent_contract(model, texts: list[str], batch_size: int = 64) -> dict:
    baseline = model.predict_proba(texts)
    for indices in (list(range(len(texts))), list(reversed(range(len(texts))))):
        for size in (1, 2, batch_size):
            chunks = [model.predict_proba([texts[i] for i in indices[start:start + size]])
                      for start in range(0, len(indices), size)]
            candidate = np.concatenate(chunks) if chunks else np.empty((0, 18))
            np.testing.assert_allclose(candidate, baseline[indices], atol=1e-5, rtol=1e-4)
            if not np.array_equal(candidate.argmax(axis=1), baseline[indices].argmax(axis=1)):
                raise ValueError("Batch-dependent labels")
    for i, text in enumerate(texts):
        repeated = model.predict_proba([text, "Unrelated companion response", text])
        np.testing.assert_allclose(repeated[[0, 2]], np.repeat(baseline[i:i+1], 2, axis=0), atol=1e-5, rtol=1e-4)
        if any(j != baseline[i].argmax() for j in repeated[[0, 2]].argmax(axis=1)):
            raise ValueError("Companion-dependent labels")
    return {"status": "passed", "rows": len(texts), "batch_sizes": [1, 2, batch_size]}
