"""Entry point: `psycho run "<society and period>"`.

Not implemented yet — Phase 1 of BUILD_PLAN.md. Will drive the stages in
`stages/` in order, writing artifacts and a manifest under
`runs/<run-id>/`, skipping any stage whose recorded output already matches
its recorded input (see docs/02-architecture.md, "Idempotency and
resumability").
"""

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(prog="psycho")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run the pipeline for one input string")
    run_parser.add_argument("society_and_period")

    args = parser.parse_args()

    if args.command == "run":
        raise NotImplementedError("Phase 1: pipeline stages not implemented yet")


if __name__ == "__main__":
    main()
