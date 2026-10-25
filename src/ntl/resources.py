"""One resource policy for feasibility producers, consumers and publication."""
from __future__ import annotations

import math
from typing import TypeGuard

VERSION = 1


def number(value: object, *, positive: bool = False) -> TypeGuard[int | float]:
    return (isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
            and (value > 0 if positive else value >= 0))


def validate_budgets(available_memory, limit_seconds) -> None:
    if not all(number(v, positive=True) for v in (available_memory, limit_seconds)):
        raise ValueError("Positive finite runtime budgets are required")


def resource_reasons(evidence: dict) -> list[str]:
    if evidence.get("resource_version") != VERSION:
        raise ValueError("Legacy resource evidence; explicit revalidation required")
    validate_budgets(evidence.get("available_memory_bytes"), evidence.get("limit_seconds"))
    memory, wall, inference = (evidence.get(n) for n in
                              ("peak_memory_bytes", "wall_seconds", "inference_seconds"))
    scale = evidence.get("scale_seconds", {})
    stress = evidence.get("capacity", {}).get("stress", {}).get("seconds")
    if (not number(memory) or not number(wall) or not number(inference, positive=True)
            or not scale or any(not number(v, positive=True) for v in scale.values())
            or not number(stress, positive=True)):
        raise ValueError("Missing or invalid finite resource measurements")
    reasons = []
    if memory >= .8 * evidence["available_memory_bytes"]:
        reasons.append("Insufficient memory reserve")
    if max(wall, inference, stress, *scale.values()) >= .7 * evidence["limit_seconds"]:
        reasons.append("Insufficient time reserve")
    device = evidence.get("execution", {}).get("runtime", {}).get("settings", {}).get("device", "cpu")
    gpu = evidence.get("gpu")
    if device != "cpu" or gpu is not None:
        if (not isinstance(gpu, dict) or gpu.get("device") != device
                or not number(gpu.get("total_bytes"), positive=True)
                or any(not number(gpu.get(n)) for n in ("allocated_bytes", "reserved_bytes"))):
            raise ValueError("Missing or invalid encoder-device memory measurements")
        if max(gpu["allocated_bytes"], gpu["reserved_bytes"]) >= .8 * gpu["total_bytes"]:
            reasons.append("Insufficient GPU memory reserve")
    return reasons


def target_reasons(evidence: dict) -> list[str]:
    reasons = resource_reasons(evidence)
    for flag in ("kaggle", "internet_disabled", "cold_restart", "independent_contract", "parquet_roundtrip"):
        if evidence.get(flag) is not True:
            reasons.append(f"Missing target execution evidence: {flag}")
    return reasons
