"""Entry point: `psycho run "<society and period>"`.

Wires up the per-run manifest (create or resume) and reports stage status.
Stage execution itself is not implemented yet — each module under
stages/ still raises NotImplementedError (Phase 2+ of BUILD_PLAN.md).
"""

from __future__ import annotations

import argparse
from pathlib import Path

from .manifest import STAGE_ORDER, Manifest


def main() -> None:
    parser = argparse.ArgumentParser(prog="psycho")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run the pipeline for one input string")
    run_parser.add_argument("society_and_period")
    run_parser.add_argument(
        "--runs-dir",
        type=Path,
        default=Path("runs"),
        help="Directory holding per-run artifacts (default: ./runs)",
    )
    run_parser.add_argument(
        "--resume",
        metavar="RUN_ID",
        help="Resume an existing run (by its run-id under --runs-dir) instead of starting a new one",
    )

    args = parser.parse_args()

    if args.command == "run":
        _run(args.society_and_period, args.runs_dir, args.resume)


def _run(society_and_period: str, runs_dir: Path, resume: str | None) -> None:
    runs_dir.mkdir(parents=True, exist_ok=True)
    manifest = Manifest.load(runs_dir / resume) if resume else Manifest.create(runs_dir, society_and_period)

    print(f"[psycho] run '{manifest.run_id}' at {manifest.run_dir}")
    for stage in STAGE_ORDER:
        record = manifest.stages.get(stage)
        print(f"[psycho]   {stage}: {record.status if record else 'pending'}")

    raise NotImplementedError(
        "manifest is wired up, but stage execution isn't implemented yet "
        "-- see BUILD_PLAN.md Phase 1/2 and stages/*.py"
    )


if __name__ == "__main__":
    main()
