# Make feasibility producers and consumers agree

## Why

At reviewed commit `8fdf97a`, `neural_smoke` checks projected inference time but omits total wall time from its pass predicate (`smoke.py:99`). `require_gate` instead checks total wall time (`gates.py:28`). A deterministic synthetic reproduction emits G1b `passed` with wall time 100 seconds against a 100-second allowance, then the real consumer rejects it with `Insufficient time reserve` because the registered ceiling is 70 seconds.

This is a conditional neural training blocker: it can falsely announce eligibility that G3 cannot consume. G1a and G6 should share the same applicable resource semantics rather than acquire further divergent predicates. Maps to G1a/G1b/G6, P05–P06 and P19; mandatory before F/H eligibility, with sparse regression coverage.

## What Changes

- Share a small resource validation function between evidence production and consumption.
- Require valid positive finite budgets, valid finite measurements and the existing strict 80% memory/70% time reserves.
- Distinguish end-to-end wall time from workload inference time; check every applicable limit consistently, including the explicit neural device's GPU evidence.
- Emit specific blocked reasons rather than a contradictory `passed` record.

## Capabilities

### New Capabilities
- `feasibility-resource-consistency`: an unchanged generated feasibility record satisfies the same resource rules at its consumer.

### Modified Capabilities
- None; supplements changes 02, 04, 10 and 11.

## Impact

Affected: `smoke.py`, `gates.py`, resource helpers, relevant release checks, tests and runbook. Coordinate the measured workload schema with change 18. Depend on change 16 for a complete target runtime.

Non-goals: relaxing headroom, making local runs pass Kaggle gates, altering selection thresholds/budgets, introducing a generic gate framework, or requiring neural feasibility for S-only execution.
