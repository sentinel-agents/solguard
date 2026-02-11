# import argparse

# from solguard.main import main as run_main


# def build_parser() -> argparse.ArgumentParser:
#     parser = argparse.ArgumentParser(
#         prog="solguard",
#         description="SOLGUARD - lightweight Solana threat detection MVP (demo CLI).",
#     )
#     sub = parser.add_subparsers(dest="command", required=True)

#     run_cmd = sub.add_parser("run", help="Run the SOLGUARD pipeline.")
#     run_cmd.add_argument(
#         "--demo",
#         action="store_true",
#         help="Run in demo mode (uses built-in demo transactions).",
#     )
#     run_cmd.add_argument(
#         "--input",
#         default=None,
#         help="Path to input JSONL transactions file (default: alerts.jsonl).",
#     )
#     run_cmd.add_argument(
#         "--out",
#         default="demo_output.jsonl",
#         help="Path to write alerts JSONL output (default: demo_output.jsonl).",
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
#         return run_main(
#             demo=args.demo,
#             input_path=args.input,
#             output_path=args.out,
#             quiet=args.quiet,
#         )

#     return 0


# if __name__ == "__main__":
#     raise SystemExit(cli())


from solguard.agent import run_once as run_main, agent_main


import argparse

from solguard.main import main as run_main
from solguard.agent import agent_main


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="solguard",
        description="SOLGUARD - lightweight Solana threat detection MVP (demo CLI).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # ---- run (existing pipeline) ----
    run_cmd = sub.add_parser("run", help="Run the SOLGUARD pipeline (batch mode).")
    run_cmd.add_argument(
        "--demo",
        action="store_true",
        help="Run in demo mode (uses built-in demo transactions).",
    )
    run_cmd.add_argument(
        "--input",
        default=None,
        help="Path to input JSONL transactions file (default handled by ingestion).",
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

    # ---- agent (autonomous loop mode) ----
    agent_cmd = sub.add_parser("agent", help="Run SOLGUARD in autonomous agent loop mode.")
    agent_cmd.add_argument(
        "--demo",
        action="store_true",
        help="Run in demo mode (uses built-in demo transactions).",
    )
    agent_cmd.add_argument(
        "--input",
        default=None,
        help="Path to input JSONL transactions file (optional).",
    )
    agent_cmd.add_argument(
        "--out",
        default="agent_output.jsonl",
        help="Path to write alerts JSONL output (default: agent_output.jsonl).",
    )
    agent_cmd.add_argument(
        "--log",
        default="agent_log.jsonl",
        help="Path to write agent decision logs JSONL (default: agent_log.jsonl).",
    )
    agent_cmd.add_argument(
        "--cycles",
        type=int,
        default=3,
        help="Number of autonomous cycles to run (default: 3).",
    )
    agent_cmd.add_argument(
        "--interval",
        type=float,
        default=2.0,
        help="Seconds to sleep between cycles (default: 2.0).",
    )
    agent_cmd.add_argument(
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

    if args.command == "agent":
        return agent_main(
            demo=args.demo,
            input_path=args.input,
            output_path=args.out,
            log_path=args.log,
            cycles=args.cycles,
            interval=args.interval,
            quiet=args.quiet,
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(cli())
