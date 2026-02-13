# # """
# # SOLGUARD agent mode (autonomous loop).

# # This module provides:
# # - run_once(): run the pipeline once (batch mode)
# # - agent_main(): run the pipeline in cycles (autonomous mode)
# # """

# # from __future__ import annotations

# # import time
# # from typing import Dict, Any, Optional, List

# # from solguard.ingestion import load_transactions
# # from solguard.scoring import score_transaction
# # from solguard.alerts import generate_alert
# # from solguard.writer import write_jsonl



# # def _tx_id(tx: Dict[str, Any]) -> str:
# #     """Best-effort transaction identifier (no drama if missing)."""
# #     return (
# #         str(tx.get("transaction_id"))
# #         if tx.get("transaction_id") is not None
# #         else str(tx.get("id")) if tx.get("id") is not None
# #         else str(tx.get("signature")) if tx.get("signature") is not None
# #         else "unknown"
# #     )


# # def _print_alert(alert: Dict[str, Any], quiet: bool) -> None:
# #     if quiet:
# #         return

# #     reasons = alert.get("reasons") or []
# #     print(f"Transaction ID: {alert.get('transaction_id', 'unknown')}")
# #     print(f"Risk score: {alert.get('score')}")
# #     print(f"Alert: {alert.get('severity')}")
# #     print(f"Reason: {', '.join(reasons) if reasons else 'N/A'}")
# #     print("-" * 40)


# # def run_once(
# #     demo: bool = False,
# #     input_path: Optional[str] = None,
# #     output_path: str = "demo_output.jsonl",
# #     quiet: bool = False,
# # ) -> int:
# #     """
# #     Run SOLGUARD pipeline once:
# #     - load transactions
# #     - score each
# #     - generate alert
# #     - write alerts JSONL
# #     - print summary
# #     """
# #     if not quiet:
# #         print("🛡 SOLGUARD starting...\n")

# #     transactions = load_transactions(demo=demo, input_path=input_path)

# #     alerts: List[Dict[str, Any]] = []
# #     for tx in transactions:
# #         result = score_transaction(tx)

# #         # Ensure alert has a tx id
# #         txid = _tx_id(tx)
# #         alert = generate_alert(tx, result.score, result.reasons)
# #         if "transaction_id" not in alert or not alert.get("transaction_id"):
# #             alert["transaction_id"] = txid

# #         alerts.append(alert)
# #         _print_alert(alert, quiet=quiet)

# #         # IMPORTANT: writer.py expects (record, path)
# #         write_jsonl(alert, output_path)

# #     if not quiet:
# #         high = sum(1 for a in alerts if a.get("severity") == "HIGH RISK")
# #         med = sum(1 for a in alerts if a.get("severity") == "MEDIUM RISK")
# #         low = sum(1 for a in alerts if a.get("severity") == "LOW RISK")

# #         print("\n🛡 SOLGUARD SESSION SUMMARY")
# #         print(f"- Total transactions analyzed: {len(alerts)}")
# #         print(f"- High risk alerts: {high}")
# #         print(f"- Medium risk alerts: {med}")
# #         print(f"- Low risk alerts: {low}")

# #         print("\nRECOMMENDATIONS:")
# #         if high > 0:
# #             print("- Investigate HIGH RISK transactions immediately")
# #         elif med > 0:
# #             print("- Review MEDIUM RISK transactions")
# #         else:
# #             print("- No suspicious activity detected in this run")

# #     return 0



# # def agent_main(
# #     demo: bool = False,
# #     input_path: Optional[str] = None,
# #     output_path: str = "agent_output.jsonl",
# #     log_path: str = "agent_log.jsonl",
# #     cycles: int = 3,
# #     interval: float = 2.0,
# #     quiet: bool = False,
# # ) -> int:
# #     """
# #     Autonomous loop:
# #     - repeats run_once-like logic for N cycles
# #     - appends alerts to output_path
# #     - appends agent events to log_path
# #     """
# #     if not quiet:
# #         print("🤖 SOLGUARD AGENT MODE starting...\n")

# #     for c in range(1, cycles + 1):
# #         if not quiet:
# #             print(f"===== Cycle {c}/{cycles} =====")

# #         start_ts = time.time()
# #         event: Dict[str, Any] = {
# #             "type": "agent_cycle_start",
# #             "cycle": c,
# #             "timestamp": start_ts,
# #             "demo": demo,
# #             "input_path": input_path,
# #             "output_path": output_path,
# #         }
# #         write_jsonl(event, log_path)

# #         # Run one cycle
# #         transactions = load_transactions(demo=demo, input_path=input_path)

# #         cycle_alerts: List[Dict[str, Any]] = []
# #         for tx in transactions:
# #             result = score_transaction(tx)
# #             txid = _tx_id(tx)

# #             alert = generate_alert(tx, result.score, result.reasons)
# #             if "transaction_id" not in alert or not alert.get("transaction_id"):
# #                 alert["transaction_id"] = txid

# #             cycle_alerts.append(alert)
# #             _print_alert(alert, quiet=quiet)

# #             # IMPORTANT: writer.py expects (record, path)
# #             write_jsonl(alert, output_path)

# #         end_ts = time.time()
# #         summary = {
# #             "type": "agent_cycle_end",
# #             "cycle": c,
# #             "timestamp": end_ts,
# #             "duration_sec": round(end_ts - start_ts, 3),
# #             "alerts_emitted": len(cycle_alerts),
# #         }
# #         write_jsonl(summary, log_path)

# #         if c < cycles:
# #             time.sleep(interval)

# #     if not quiet:
# #         print("\n🤖 AGENT MODE finished.\n")

# #     return 0


# """
# SOLGUARD agent mode (autonomous loop).

# This module provides:
# - run_once(): run the pipeline once (batch mode)
# - agent_main(): run the pipeline in cycles (autonomous mode)
# """

# from __future__ import annotations

# import time
# from typing import Dict, Any, Optional, List

# from solguard.ingestion import load_transactions
# from solguard.scoring import score_transaction
# from solguard.alerts import generate_alert
# from solguard.writer import write_jsonl

# # ✅ LLM decision helper (Mode A: simulated transactions)
# from solguard.llm import llm_decide_next_step


# def _tx_id(tx: Dict[str, Any]) -> str:
#     """Best-effort transaction identifier (no drama if missing)."""
#     if tx.get("transaction_id") is not None:
#         return str(tx.get("transaction_id"))
#     if tx.get("id") is not None:
#         return str(tx.get("id"))
#     if tx.get("signature") is not None:
#         return str(tx.get("signature"))
#     return "unknown"


# def _print_alert(alert: Dict[str, Any], quiet: bool) -> None:
#     if quiet:
#         return

#     reasons = alert.get("reasons") or []
#     print(f"Transaction ID: {alert.get('transaction_id') or 'unknown'}")
#     print(f"Risk score: {alert.get('score')}")
#     print(f"Alert: {alert.get('severity')}")
#     print(f"Reason: {', '.join(reasons) if reasons else 'N/A'}")
#     print("-" * 40)


# def run_once(
#     demo: bool = False,
#     input_path: Optional[str] = None,
#     output_path: str = "demo_output.jsonl",
#     quiet: bool = False,
# ) -> int:
#     """
#     Run SOLGUARD pipeline once:
#     - load transactions
#     - score each
#     - generate alert
#     - write alerts JSONL
#     - print summary
#     """
#     if not quiet:
#         print("🛡 SOLGUARD starting...\n")

#     transactions = load_transactions(demo=demo, input_path=input_path)

#     alerts: List[Dict[str, Any]] = []
#     for tx in transactions:
#         result = score_transaction(tx)

#         txid = _tx_id(tx)
#         alert = generate_alert(tx, result.score, result.reasons)

#         # Ensure alert has a tx id
#         if not alert.get("transaction_id"):
#             alert["transaction_id"] = txid

#         alerts.append(alert)
#         _print_alert(alert, quiet=quiet)

#         # writer.py expects (record, path)
#         write_jsonl(alert, output_path)

#     if not quiet:
#         high = sum(1 for a in alerts if a.get("severity") == "HIGH RISK")
#         med = sum(1 for a in alerts if a.get("severity") == "MEDIUM RISK")
#         low = sum(1 for a in alerts if a.get("severity") == "LOW RISK")

#         print("\n🛡 SOLGUARD SESSION SUMMARY")
#         print(f"- Total transactions analyzed: {len(alerts)}")
#         print(f"- High risk alerts: {high}")
#         print(f"- Medium risk alerts: {med}")
#         print(f"- Low risk alerts: {low}")

#         print("\nRECOMMENDATIONS:")
#         if high > 0:
#             print("- Investigate HIGH RISK transactions immediately")
#         elif med > 0:
#             print("- Review MEDIUM RISK transactions")
#         else:
#             print("- No suspicious activity detected in this run")

#     return 0


# def agent_main(
#     demo: bool = False,
#     input_path: Optional[str] = None,
#     output_path: str = "agent_output.jsonl",
#     log_path: str = "agent_log.jsonl",
#     cycles: int = 3,
#     interval: float = 2.0,
#     quiet: bool = False,
# ) -> int:
#     """
#     Autonomous loop:
#     - repeats run_once-like logic for N cycles
#     - appends alerts to output_path
#     - appends agent events (including LLM decisions) to log_path
#     """
#     if not quiet:
#         print("🤖 SOLGUARD AGENT MODE starting...\n")

#     for c in range(1, cycles + 1):
#         if not quiet:
#             print(f"===== Cycle {c}/{cycles} =====")

#         start_ts = time.time()

#         # Log cycle start
#         write_jsonl(
#             {
#                 "type": "agent_cycle_start",
#                 "cycle": c,
#                 "timestamp": start_ts,
#                 "demo": demo,
#                 "input_path": input_path,
#                 "output_path": output_path,
#             },
#             log_path,
#         )

#         # Run one cycle
#         transactions = load_transactions(demo=demo, input_path=input_path)

#         cycle_alerts: List[Dict[str, Any]] = []
#         for tx in transactions:
#             result = score_transaction(tx)
#             txid = _tx_id(tx)

#             alert = generate_alert(tx, result.score, result.reasons)
#             if not alert.get("transaction_id"):
#                 alert["transaction_id"] = txid

#             cycle_alerts.append(alert)
#             _print_alert(alert, quiet=quiet)

#             # Write alert to output JSONL
#             write_jsonl(alert, output_path)

#         # ✅ LLM decision step (after cycle alerts are collected)
#         llm_event: Dict[str, Any] = {
#             "type": "agent_llm_decision",
#             "cycle": c,
#             "timestamp": time.time(),
#             "input_alerts": len(cycle_alerts),
#         }

#         try:
#             decision = llm_decide_next_step(cycle_alerts)
#             # decision can be str or dict; store it safely
#             llm_event["decision"] = decision
#             llm_event["status"] = "ok"
#         except Exception as e:
#             llm_event["status"] = "error"
#             llm_event["error"] = str(e)

#         write_jsonl(llm_event, log_path)

#         # Log cycle end
#         end_ts = time.time()
#         write_jsonl(
#             {
#                 "type": "agent_cycle_end",
#                 "cycle": c,
#                 "timestamp": end_ts,
#                 "duration_sec": round(end_ts - start_ts, 3),
#                 "alerts_emitted": len(cycle_alerts),
#             },
#             log_path,
#         )

#         if c < cycles:
#             time.sleep(interval)

#     if not quiet:
#         print("\n🤖 AGENT MODE finished.\n")

#     return 0

"""
SOLGUARD agent mode (autonomous loop).
"""

from __future__ import annotations

import time
from typing import Dict, Any, Optional, List

from solguard.ingestion import load_transactions
from solguard.scoring import score_transaction
from solguard.alerts import generate_alert
from solguard.writer import write_jsonl
from solguard.llm import llm_decide_next_step



def _tx_id(tx: Dict[str, Any]) -> str:
    return (
        str(tx.get("transaction_id"))
        if tx.get("transaction_id") is not None
        else str(tx.get("id")) if tx.get("id") is not None
        else str(tx.get("signature")) if tx.get("signature") is not None
        else "unknown"
    )


def _print_alert(alert: Dict[str, Any], quiet: bool) -> None:
    if quiet:
        return

    reasons = alert.get("reasons") or []
    print(f"Transaction ID: {alert.get('transaction_id', 'unknown')}")
    print(f"Risk score: {alert.get('score')}")
    print(f"Alert: {alert.get('severity')}")
    print(f"Reason: {', '.join(reasons) if reasons else 'N/A'}")
    print("-" * 40)

def run_once(
    demo: bool = False,
    input_path: Optional[str] = None,
    output_path: str = "demo_output.jsonl",
    quiet: bool = False,
) -> int:
    """
    Run SOLGUARD pipeline once (batch mode).
    CLI expects this symbol: run_once.
    """
    if not quiet:
        print("🛡 SOLGUARD starting...\n")

    transactions = load_transactions(demo=demo, input_path=input_path)

    alerts: List[Dict[str, Any]] = []
    for tx in transactions:
        result = score_transaction(tx)
        txid = _tx_id(tx)

        alert = generate_alert(tx, result.score, result.reasons)
        if "transaction_id" not in alert or not alert.get("transaction_id"):
            alert["transaction_id"] = txid

        alerts.append(alert)
        _print_alert(alert, quiet=quiet)

        # writer.py expects (record, path)
        write_jsonl(alert, output_path)

    if not quiet:
        high = sum(1 for a in alerts if a.get("severity") == "HIGH RISK")
        med = sum(1 for a in alerts if a.get("severity") == "MEDIUM RISK")
        low = sum(1 for a in alerts if a.get("severity") == "LOW RISK")

        print("\n🛡 SOLGUARD SESSION SUMMARY")
        print(f"- Total transactions analyzed: {len(alerts)}")
        print(f"- High risk alerts: {high}")
        print(f"- Medium risk alerts: {med}")
        print(f"- Low risk alerts: {low}")

        print("\nRECOMMENDATIONS:")
        if high > 0:
            print("- Investigate HIGH RISK transactions immediately")
        elif med > 0:
            print("- Review MEDIUM RISK transactions")
        else:
            print("- No suspicious activity detected in this run")

    return 0


def agent_main(
    demo: bool = False,
    input_path: Optional[str] = None,
    output_path: str = "agent_output.jsonl",
    log_path: str = "agent_log.jsonl",
    cycles: int = 3,
    interval: float = 2.0,
    quiet: bool = False,
) -> int:

    if not quiet:
        print("🤖 SOLGUARD AGENT MODE starting...\n")

    for c in range(1, cycles + 1):
        if not quiet:
            print(f"===== Cycle {c}/{cycles} =====")

        start_ts = time.time()

        write_jsonl(
            {
                "type": "agent_cycle_start",
                "cycle": c,
                "timestamp": start_ts,
            },
            log_path,
        )

        transactions = load_transactions(demo=demo, input_path=input_path)

        cycle_alerts: List[Dict[str, Any]] = []

        for tx in transactions:
            result = score_transaction(tx)
            txid = _tx_id(tx)

            alert = generate_alert(tx, result.score, result.reasons)

            if "transaction_id" not in alert or not alert.get("transaction_id"):
                alert["transaction_id"] = txid

            cycle_alerts.append(alert)
            _print_alert(alert, quiet=quiet)

            write_jsonl(alert, output_path)

        # =========================
        # 🧠 LLM DECISION PHASE
        # =========================
        try:
            decision = llm_decide_next_step(
                cycle=c,
                txs=transactions,
                alerts=cycle_alerts,
            )

            write_jsonl(
                {
                    "type": "agent_llm_decision",
                    "cycle": c,
                    "timestamp": time.time(),
                    "decision": decision,
                },
                log_path,
            )

            if not quiet:
                print("\n🧠 LLM Decision:")
                print("Summary:", decision.get("agent_summary"))
                print("Next Action:", decision.get("next_action"))
                print("Suggested Checks:", decision.get("suggested_checks"))
                print("-" * 50)

            # 🔥 Agent ACTS based on LLM
            if decision.get("next_action") == "raise_attention":
                print("🚨 AGENT ESCALATION: High risk cluster detected.")
            elif decision.get("next_action") == "stop":
                print("🛑 AGENT STOPPING based on LLM recommendation.")
                break

            action = decision.get("next_action", "continue_monitoring")

            if action == "raise_attention":
                write_jsonl(
                     {
            "type": "agent_action",
            "cycle": c,
            "timestamp": time.time(),
            "action": "raise_attention",
            "details": {
                "reason": "LLM raised attention based on alert cluster",
                "alerts_in_cycle": len(cycle_alerts),
            },
        },
        log_path,
    )
            elif action == "stop":
                write_jsonl(
        {
            "type": "agent_action",
            "cycle": c,
            "timestamp": time.time(),
            "action": "stop",
            "details": {"reason": "LLM recommended stop"},
        },
        log_path,
    )


        except Exception as e:
            write_jsonl(
                {
                    "type": "agent_llm_error",
                    "cycle": c,
                    "timestamp": time.time(),
                    "error": str(e),
                },
                log_path,
            )

        # =========================

        end_ts = time.time()

        write_jsonl(
            {
                "type": "agent_cycle_end",
                "cycle": c,
                "timestamp": end_ts,
                "duration_sec": round(end_ts - start_ts, 3),
                "alerts_emitted": len(cycle_alerts),
            },
            log_path,
        )

        if c < cycles:
            time.sleep(interval)

    if not quiet:
        print("\n🤖 AGENT MODE finished.\n")

    return 0

