# # solguard/cli.py
# import argparse
# from solguard.main import main


# def build_parser() -> argparse.ArgumentParser:
#     parser = argparse.ArgumentParser(
#         prog="solguard",
#         description="SOLGUARD - lightweight Solana threat detection MVP (demo CLI).",
#     )

#     sub = parser.add_subparsers(dest="command", required=True)

#     # solguard run
#     run_cmd = sub.add_parser("run", help="Run the SOLGUARD pipeline.")
#     run_cmd.add_argument(
#         "--demo",
#         action="store_true",
#         help="Run in demo mode (uses built-in demo transactions).",
#     )
#     run_cmd.add_argument(
#         "--output",
#         default="alerts.jsonl",
#         help="Path to write alerts JSONL output (default: alerts.jsonl).",
#     )
#     run_cmd.add_argument(
#         "--quiet",
#         action="store_true",
#         help="Less console output (still writes JSONL).",
#     )

#     return parser


# def cli(argv=None) -> int:
#     parser = build_parser()
#     args = parser.parse_args(argv)

#     if args.command == "run":
#         # We pass parameters to main() if supported.
#         # If your current main() doesn't accept these yet, we'll adjust main.py in the next step.
#         return main(
#             demo=args.demo,
#             output_path=args.output,
#             quiet=args.quiet,
#         )

#     return 0


# if __name__ == "__main__":
#     raise SystemExit(cli())

# def main():
#     cli()


import argparse

from solguard.main import main as run_main


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="solguard",
        description="SOLGUARD - lightweight Solana threat detection MVP (demo CLI).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    run_cmd = sub.add_parser("run", help="Run the SOLGUARD pipeline.")
    run_cmd.add_argument(
        "--demo",
        action="store_true",
        help="Run in demo mode (uses built-in demo transactions).",
    )
    run_cmd.add_argument(
        "--input",
        default=None,
        help="Path to input JSONL transactions file (default: alerts.jsonl).",
    )
    run_cmd.add_argument(
        "--out",
        default="demo_output.jsonl",
        help="Path to write alerts JSONL output (default: demo_output.jsonl).",
    )
    run_cmd.add_argument(
        "--quiet",
        action="store_true",
        help="Less console output (still writes JSONL).",
    )
    return parser


def cli(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "run":
        return run_main(
            demo=args.demo,
            input_path=args.input,
            output_path=args.out,
            quiet=args.quiet,
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(cli())
