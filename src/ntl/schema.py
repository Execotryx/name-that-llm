"""Persisted logical UTF-8 and physical Arrow submission contract."""
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from .common import read_json

NAMES = ["id", "model"]
DEFAULT_CONTRACT = {"version": 1, "fields": [{"name": n, "type": "string"} for n in NAMES]}


def arrow_schema(contract: dict) -> pa.Schema:
    if contract.get("version") != 1 or [f.get("name") for f in contract.get("fields", [])] != NAMES:
        raise ValueError("Missing or unsupported submission contract; prepare a versioned campaign")
    types = {"string": pa.string(), "large_string": pa.large_string()}
    if any(set(f) != {"name", "type"} or f["type"] not in types for f in contract["fields"]):
        raise ValueError("Submission fields must be UTF-8 string or large_string")
    return pa.schema([pa.field(f["name"], types[f["type"]]) for f in contract["fields"]])


def sample_contract(sample: Path, test_ids: list[str]) -> dict:
    table = pq.read_table(sample)
    contract = {"version": 1, "fields": [{"name": f.name, "type": str(f.type)} for f in table.schema]}
    arrow_schema(contract)
    if any(table.column(n).null_count for n in NAMES):
        raise ValueError("Null sample fields")
    ids = table.column("id").to_pylist()
    if len(ids) != len(set(ids)) or any(not i.strip() for i in ids) or ids != test_ids:
        raise ValueError("Sample/test row identity drift")
    return contract


def load_contract(root: Path) -> dict:
    contract = read_json(root / "submission_schema.json")
    arrow_schema(contract)
    return contract
