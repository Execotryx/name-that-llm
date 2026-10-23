"""Thin commands; research, lock access and final refit stay separate."""
from __future__ import annotations

import argparse
from pathlib import Path

from .common import read_json


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser("prepare", help="Audit and freeze development/sealed manifests")
    prepare.add_argument("--train", type=Path, required=True)
    prepare.add_argument("--test", type=Path, required=True)
    prepare.add_argument("--sample", type=Path, required=True)
    prepare.add_argument("--root", type=Path, required=True)
    prepare.add_argument("--sealed", type=Path, required=True)
    prepare.add_argument("--protocol", type=Path, default=Path("configs/protocol.json"))
    for name in ("smoke", "evaluate", "diagnose", "topic", "freeze", "confirm", "refit"):
        command = commands.add_parser(name)
        command.add_argument("--root", type=Path, required=True)
        if name not in ("confirm",):
            command.add_argument("--output", type=Path, required=True)
        if name in ("diagnose", "freeze"):
            command.add_argument("--run", type=Path, required=True)
        if name in ("freeze", "confirm", "refit"):
            command.add_argument("--receipt", type=Path, default=Path("configs/decision-receipt.json"))
        if name in ("confirm", "refit"):
            command.add_argument("--decision", type=Path, required=True)
            command.add_argument("--sealed", type=Path, required=True)
        if name == "freeze":
            command.add_argument("--diagnostics", type=Path, required=True)
            command.add_argument("--topic-report", type=Path, required=True)
        if name in ("evaluate", "topic", "freeze"):
            command.add_argument("--encoder-assets", type=Path)
            command.add_argument("--neural-gate", type=Path)
            command.add_argument("--device", default="cpu")
        if name == "confirm":
            command.add_argument("--operator", required=True)
        if name == "refit":
            command.add_argument("--train", type=Path, required=True)
            command.add_argument("--task-artifacts-permitted", action="store_true")
        if name == "smoke":
            command.add_argument("--test", type=Path, required=True)
            command.add_argument("--available-memory", type=int, required=True, help="Measured target memory allowance in bytes")
            command.add_argument("--limit-seconds", type=float, default=32400)
            command.add_argument("--cold-restart", action="store_true")
    replay = commands.add_parser("replay")
    replay.add_argument("--bundle", type=Path, required=True)
    replay.add_argument("--test", type=Path, required=True)
    replay.add_argument("--output", type=Path, required=True)
    replay.add_argument("--available-memory", type=int, required=True)
    replay.add_argument("--limit-seconds", type=float, default=32400)
    replay.add_argument("--cold-restart", action="store_true")
    args = parser.parse_args()
    encoder = None
    if getattr(args, "encoder_assets", None):
        from .encoder import FrozenEncoder
        encoder = FrozenEncoder(args.encoder_assets, device=args.device)
    if args.command == "prepare":
        from .protocol import prepare as run
        run(args.train, args.root, args.sealed, read_json(args.protocol), test=args.test, sample=args.sample)
    elif args.command == "smoke":
        from .smoke import cpu_smoke
        cpu_smoke(args.root, args.test, args.output, available_memory=args.available_memory,
                  limit_seconds=args.limit_seconds, cold_restart=args.cold_restart)
    elif args.command == "evaluate":
        from .runner import evaluate
        evaluate(args.root, args.output, encoder=encoder, neural_gate=args.neural_gate)
    elif args.command == "diagnose":
        from .diagnostics import artifact_diagnostics
        artifact_diagnostics(args.root, args.run, args.output)
    elif args.command == "topic":
        from .diagnostics import topic_stress
        topic_stress(args.root, args.output, encoder=encoder, neural_gate=args.neural_gate)
    elif args.command == "freeze":
        from .decision import freeze
        freeze(args.root, args.run, args.diagnostics, args.topic_report, args.output, args.receipt,
               encoder=encoder, neural_gate=args.neural_gate)
    elif args.command == "confirm":
        from .locked_eval import confirm
        confirm(args.root, args.sealed, args.decision, args.receipt, operator=args.operator)
    elif args.command == "refit":
        from .release import refit
        refit(args.root, args.sealed, args.decision, args.receipt, args.train, args.output,
              task_artifacts_permitted=args.task_artifacts_permitted)
    else:
        from .release import replay as run_replay, require_release
        report = run_replay(args.bundle, args.test, args.output, available_memory=args.available_memory,
                   limit_seconds=args.limit_seconds, cold_restart=args.cold_restart)
        require_release(report)


if __name__ == "__main__":
    main()
