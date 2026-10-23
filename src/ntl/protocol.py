"""G0 setup: immutable input inventory, manifests and experiment policy."""
from __future__ import annotations

from pathlib import Path
import copy
import re

import numpy as np

from .common import digest, environment, identity, read_json, source_revision, write_json
from .data import TRAIN_COLUMNS, audit, check_source, read_csv
from .labels import CLASSES, PROVIDERS
from .splits import manifests

DEFAULT = {
    "version": "1.1", "seed": 2027, "candidates": ["S", "F", "H"],
    "C": [.5, 1, 2, 4], "weights": [i / 10 for i in range(11)],
    "promotion": .03, "tie_band": .005, "outer_folds": 5, "inner_folds": 4,
    "bootstrap": 10000, "permutations": 100000,
    "veto": {"topic_loss": .02, "recall_loss": .10, "leave_provider_gain": 0},
    "encoder": {"model": "microsoft/deberta-v3-small", "revision": None,
                "max_length": 512, "pooling": "masked-mean-including-special", "dtype": "float32"},
    "budgets": {"outer_inner_component": 160, "outer_refits": 30, "final_inner_component": 32,
                "diagnostic": 60, "topic_inner_component": 192, "topic_refits": 36},
    "convergence": {"initial": 2500, "uniform_retry": 10000, "unresolved": "abort"},
    "batch_size": 64, "memory_fraction": .8, "time_fraction": .7,
    "diagnostics": ["word-only", "stylometry", "length-only", "format-only", "no-length",
                    "format-stripped", "lexical-only", "opening-only", "opening-removed"],
    "prefixes": [40, 80, 120], "prefix_primary": "frozen-model-perturbation",
    "source_sha256": "40a22ce8d88c5f46feb4637a099db815bef5f713ffe53e89dbe1b7b21de77707",
    "holdout": {"prompts": 30, "contradiction": .03},
}


def validate_protocol(protocol: dict) -> None:
    comparison = copy.deepcopy(protocol)
    revision = comparison["encoder"]["revision"]
    if revision is not None and not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("Encoder revision must be an exact commit")
    comparison["encoder"]["revision"] = None
    if comparison != DEFAULT:
        raise ValueError("Unregistered protocol; register and implement a versioned amendment first")


def prepare(source: Path, root: Path, sealed: Path, protocol: dict, *, test: Path, sample: Path) -> None:
    validate_protocol(protocol)
    revision = source_revision()
    if root.exists() or sealed.exists():
        raise ValueError("Never overwrite an existing protocol or lock")
    if sealed.resolve().is_relative_to(root.resolve()) or root.resolve().is_relative_to(sealed.resolve()):
        raise ValueError("Development and sealed inputs must have separate roots")
    check_source(source, protocol["source_sha256"], root.parent / "source-discrepancy.json")
    check_source(test, "4545aa3a3459f4c0724f97ad5bd06c4caa3506bdfea5fab905e8203184fc0c57", root.parent / "test-discrepancy.json")
    check_source(sample, "ccf86796b80fd7f83d8463664603fd1208e17559abcf416f198776b819646188", root.parent / "sample-discrepancy.json")
    frame = read_csv(source, TRAIN_COLUMNS)
    test_frame = read_csv(test, ["id", "text"])
    import pyarrow as pa
    import pyarrow.parquet as pq
    sample_table = pq.read_table(sample)
    if sample_table.column_names != ["id", "model"] or any(not pa.types.is_string(field.type) for field in sample_table.schema):
        raise ValueError("Sample Parquet schema drift")
    if sample_table.column("id").to_pylist() != test_frame.id.tolist():
        raise ValueError("Sample/test row identity drift")
    if set(frame.id) & set(test_frame.id) or set(frame.text) & set(test_frame.text):
        raise ValueError("Train/test overlap requires protocol review")
    inventory = audit(frame, source)
    inventory["other_sources"] = {"test": {"sha256": digest(test), "rows": len(test_frame)},
                                  "sample": {"sha256": digest(sample), "rows": sample_table.num_rows}}
    write_json(root / "audit.json", inventory)
    if len(frame) != 2699 or frame.prompt_id.nunique() != 150 or inventory["missing_pairs"] != [["p002", "claude-fable-5"]]:
        raise ValueError("Benchmark structure drift; resolve before modeling")
    if inventory["cross_prompt_links"]:
        raise ValueError("Cross-prompt duplicate links require a component-aware protocol amendment")
    prompts = np.array(sorted(frame.prompt_id.unique()))
    np.random.default_rng(2027).shuffle(prompts)
    locked = set(prompts[:30])
    roles = frame[["id", "prompt_id"]].copy()
    roles["role"] = ["locked" if p in locked else "development" for p in roles.prompt_id]
    development = frame.loc[roles.role == "development"].reset_index(drop=True)
    holdout = frame.loc[roles.role == "locked"].reset_index(drop=True)
    sealed.mkdir(parents=True)
    development.to_csv(root / "development.csv", index=False)
    holdout[["id", "prompt_id", "text"]].to_csv(sealed / "texts.csv", index=False)
    holdout[["id", "model"]].to_csv(sealed / "labels.csv", index=False)
    roles.to_csv(root / "split_roles.csv", index=False)
    outer, inner, final = manifests(development)
    for name, table in [("outer_folds", outer), ("inner_folds", inner), ("final_selection_folds", final)]:
        table.to_csv(root / f"{name}.csv", index=False)
    write_json(root / "protocol.json", protocol)
    write_json(root / "classes.json", {"classes": CLASSES, "providers": PROVIDERS})
    write_json(root / "environment.json", environment())
    names = ["development.csv", "split_roles.csv", "outer_folds.csv", "inner_folds.csv",
             "final_selection_folds.csv", "protocol.json", "classes.json", "environment.json", "audit.json"]
    manifest = {"files": {n: digest(root / n) for n in names}, "development_ids": development.id.tolist(),
                "locked_ids": holdout.id.tolist(), "locked_prompts": sorted(locked),
                "protocol_hash": identity(protocol), "source_hash": digest(source), "code_revision": revision,
                "isolation": "Loader allowlist and separate paths; operator retains raw-file access. Use separate credentials/custodian for stronger isolation."}
    write_json(root / "manifest.json", manifest, exclusive=True)
    write_json(sealed / "manifest.json", {"files": {n: digest(sealed / n) for n in ["texts.csv", "labels.csv"]},
               "development_manifest_hash": digest(root / "manifest.json"), "ids": holdout.id.tolist(),
               "prompts": sorted(locked)}, exclusive=True)
    (root / "audit.md").write_text(f"# Dataset audit\n\n{len(frame)} unchanged rows; 150 prompts; 18 labels.\n\nMissing pair: p002 / claude-fable-5.\n", encoding="utf-8")


def registered(root: Path) -> dict:
    protocol = read_json(root / "protocol.json")
    validate_protocol(protocol)
    return protocol
