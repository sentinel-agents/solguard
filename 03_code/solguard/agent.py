# # """
# # SOLGUARD agent mode (autonomous loop).
# # """

# # from __future__ import annotations

# # import time
# # from typing import Dict, Any, Optional, List

# # from solguard.ingestion import load_transactions
# # from solguard.scoring import score_transaction
# # from solguard.alerts import generate_alert
# # from solguard.writer import write_jsonl
# # from solguard.llm import llm_decide_next_step
# # from solguard.memory import AgentMemory




# # def _tx_id(tx: Dict[str, Any]) -> str:
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
# #     Run SOLGUARD pipeline once (batch mode).
# #     CLI expects this symbol: run_once.
# #     """
# #     if not quiet:
# #         print("🛡 SOLGUARD starting...\n")

# #     transactions = load_transactions(demo=demo, input_path=input_path)

# #     alerts: List[Dict[str, Any]] = []
# #     for tx in transactions:
# #         result = score_transaction(tx)
# #         txid = _tx_id(tx)

# #         alert = generate_alert(tx, result.score, result.reasons)
# #         if "transaction_id" not in alert or not alert.get("transaction_id"):
# #             alert["transaction_id"] = txid

# #         alerts.append(alert)
# #         _print_alert(alert, quiet=quiet)

# #         # writer.py expects (record, path)
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
# #     memory = AgentMemory()

# # ) -> int:

# #     if not quiet:
# #         print("🤖 SOLGUARD AGENT MODE starting...\n")

# #     for c in range(1, cycles + 1):
# #         if not quiet:
# #             print(f"===== Cycle {c}/{cycles} =====")

# #         start_ts = time.time()

# #         write_jsonl(
# #             {
# #                 "type": "agent_cycle_start",
# #                 "cycle": c,
# #                 "timestamp": start_ts,
# #             },
# #             log_path,
# #         )

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

# #             write_jsonl(alert, output_path)

# #         # =========================
# #         # 🧠 LLM DECISION PHASE
# #         # =========================
# #         try:
# #             decision = llm_decide_next_step(
# #                 cycle=c,
# #                 txs=transactions,
# #                 alerts=cycle_alerts,
# #             )

# #             write_jsonl(
# #                 {
# #                     "type": "agent_llm_decision",
# #                     "cycle": c,
# #                     "timestamp": time.time(),
# #                     "decision": decision,
# #                 },
# #                 log_path,
# #             )

# #             if not quiet:
# #                 print("\n🧠 LLM Decision:")
# #                 print("Summary:", decision.get("agent_summary"))
# #                 print("Next Action:", decision.get("next_action"))
# #                 print("Suggested Checks:", decision.get("suggested_checks"))
# #                 print("-" * 50)

# #             # 🔥 Agent ACTS based on LLM
# #             if decision.get("next_action") == "raise_attention":
# #                 print("🚨 AGENT ESCALATION: High risk cluster detected.")
# #             elif decision.get("next_action") == "stop":
# #                 print("🛑 AGENT STOPPING based on LLM recommendation.")
# #                 break

# #             memory.update(cycle_alerts, decision)

# #             trend = memory.risk_trend()

# #             if not quiet:
# #                 print("📊 Agent Memory Trend:", trend)
# #                 print("Total Escalations:", memory.total_escalations)


# #             action = decision.get("next_action", "continue_monitoring")

# #             if action == "raise_attention":
# #                 write_jsonl(
# #                      {
# #             "type": "agent_action",
# #             "cycle": c,
# #             "timestamp": time.time(),
# #             "action": "raise_attention",
# #             "details": {
# #                 "reason": "LLM raised attention based on alert cluster",
# #                 "alerts_in_cycle": len(cycle_alerts),
# #             },
# #         },
# #         log_path,
# #     )
# #             elif action == "stop":
# #                 write_jsonl(
# #         {
# #             "type": "agent_action",
# #             "cycle": c,
# #             "timestamp": time.time(),
# #             "action": "stop",
# #             "details": {"reason": "LLM recommended stop"},
# #         },
# #         log_path,
# #     )


# #         except Exception as e:
# #             write_jsonl(
# #                 {
# #                     "type": "agent_llm_error",
# #                     "cycle": c,
# #                     "timestamp": time.time(),
# #                     "error": str(e),
# #                 },
# #                 log_path,
# #             )

# #         # =========================

# #         end_ts = time.time()

# #         write_jsonl(
# #             {
# #                 "type": "agent_cycle_end",
# #                 "cycle": c,
# #                 "timestamp": end_ts,
# #                 "duration_sec": round(end_ts - start_ts, 3),
# #                 "alerts_emitted": len(cycle_alerts),
# #             },
# #             log_path,
# #         )

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
# from solguard.llm import llm_decide_next_step
# from solguard.memory import AgentMemory


# def _tx_id(tx: Dict[str, Any]) -> str:
#     """Best-effort transaction identifier."""
#     return (
#         str(tx.get("transaction_id"))
#         if tx.get("transaction_id") is not None
#         else str(tx.get("id")) if tx.get("id") is not None
#         else str(tx.get("signature")) if tx.get("signature") is not None
#         else "unknown"
#     )


# def _print_alert(alert: Dict[str, Any], quiet: bool) -> None:
#     if quiet:
#         return

#     reasons = alert.get("reasons") or []
#     print(f"Transaction ID: {alert.get('transaction_id', 'unknown')}")
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
#         if "transaction_id" not in alert or not alert.get("transaction_id"):
#             alert["transaction_id"] = txid

#         alerts.append(alert)
#         _print_alert(alert, quiet=quiet)

#         # IMPORTANT: writer.py expects (record, path)
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
#     memory: Optional[AgentMemory] = None,
# ) -> int:
#     """
#     Autonomous loop:
#     - repeats run_once-like logic for N cycles
#     - appends alerts to output_path
#     - appends agent events to log_path
#     - uses AgentMemory to adapt scoring (trend-aware)
#     - asks LLM to decide next action after each cycle
#     """
#     mem = memory or AgentMemory()

#     if not quiet:
#         print("🤖 SOLGUARD AGENT MODE starting...\n")

#     for c in range(1, cycles + 1):
#         if not quiet:
#             print(f"===== Cycle {c}/{cycles} =====")

#         start_ts = time.time()

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

#         # Trend BEFORE scoring (adaptive scoring uses it)
#         trend_before = mem.risk_trend()

#         transactions = load_transactions(demo=demo, input_path=input_path)
#         cycle_alerts: List[Dict[str, Any]] = []

#         for tx in transactions:
#             # 🔥 Adaptive scoring driven by memory trend
#             result = score_transaction(tx, context={"trend": trend_before})
#             txid = _tx_id(tx)

#             alert = generate_alert(tx, result.score, result.reasons)
#             if "transaction_id" not in alert or not alert.get("transaction_id"):
#                 alert["transaction_id"] = txid

#             cycle_alerts.append(alert)
#             _print_alert(alert, quiet=quiet)

#             write_jsonl(alert, output_path)

#         # =========================
#         # 🧠 LLM DECISION PHASE
#         # =========================
#         try:
#             decision = llm_decide_next_step(
#                 cycle=c,
#                 txs=transactions,
#                 alerts=cycle_alerts,
#             )

#             write_jsonl(
#                 {
#                     "type": "agent_llm_decision",
#                     "cycle": c,
#                     "timestamp": time.time(),
#                     "decision": decision,
#                 },
#                 log_path,
#             )

#             if not quiet:
#                 print("\n🧠 LLM Decision:")
#                 print("Summary:", decision.get("agent_summary"))
#                 print("Next Action:", decision.get("next_action"))
#                 print("Suggested Checks:", decision.get("suggested_checks"))
#                 print("-" * 50)

#             # Update memory AFTER decision
#             mem.update(cycle_alerts, decision)
#             trend_after = mem.risk_trend()

#             # Snapshot memory in logs (useful for demo + judging)
#             write_jsonl(
#                 {
#                     "type": "agent_memory_snapshot",
#                     "cycle": c,
#                     "timestamp": time.time(),
#                     "trend_before": trend_before,
#                     "trend_after": trend_after,
#                     "total_cycles": mem.total_cycles,
#                     "total_alerts": mem.total_alerts,
#                     "total_high": mem.total_high,
#                     "total_medium": mem.total_medium,
#                     "total_escalations": mem.total_escalations,
#                     "last_decision": decision.get("next_action"),
#                 },
#                 log_path,
#             )

#             if not quiet:
#                 print("📊 Agent Memory Trend:", trend_after)
#                 print("Total Escalations:", mem.total_escalations)

#             action = str(decision.get("next_action", "continue_monitoring"))

#             # 🔥 Agent ACTS based on LLM
#             if action == "raise_attention":
#                 if not quiet:
#                     print("🚨 AGENT ESCALATION: High risk cluster detected.")

#                 write_jsonl(
#                     {
#                         "type": "agent_action",
#                         "cycle": c,
#                         "timestamp": time.time(),
#                         "action": "raise_attention",
#                         "details": {
#                             "reason": "LLM raised attention based on alert cluster",
#                             "alerts_in_cycle": len(cycle_alerts),
#                             "trend_after": trend_after,
#                         },
#                     },
#                     log_path,
#                 )

#             elif action == "stop":
#                 if not quiet:
#                     print("🛑 AGENT STOPPING based on LLM recommendation.")

#                 write_jsonl(
#                     {
#                         "type": "agent_action",
#                         "cycle": c,
#                         "timestamp": time.time(),
#                         "action": "stop",
#                         "details": {"reason": "LLM recommended stop"},
#                     },
#                     log_path,
#                 )
#                 break

#             else:
#                 # continue_monitoring
#                 write_jsonl(
#                     {
#                         "type": "agent_action",
#                         "cycle": c,
#                         "timestamp": time.time(),
#                         "action": "continue_monitoring",
#                         "details": {"trend_after": trend_after},
#                     },
#                     log_path,
#                 )

#         except Exception as e:
#             write_jsonl(
#                 {
#                     "type": "agent_llm_error",
#                     "cycle": c,
#                     "timestamp": time.time(),
#                     "error": str(e),
#                 },
#                 log_path,
#             )

#         # =========================

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

This module provides:
- run_once(): run the pipeline once (batch mode)
- agent_main(): run the pipeline in cycles (autonomous mode)
"""

from __future__ import annotations

import time
from typing import Dict, Any, Optional, List

from solguard.ingestion import load_transactions
from solguard.scoring import score_transaction
from solguard.alerts import generate_alert
from solguard.writer import write_jsonl
from solguard.llm import llm_decide_next_step
from solguard.memory import AgentMemory


def _tx_id(tx: Dict[str, Any]) -> str:
    """Best-effort transaction identifier."""
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
    Run SOLGUARD pipeline once:
    - load transactions
    - score each
    - generate alert
    - write alerts JSONL
    - print summary
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
    memory: Optional[AgentMemory] = None,
    escalation_cooldown_cycles: int = 2,
) -> int:
    """
    Autonomous loop:
    - repeats run_once-like logic for N cycles
    - appends alerts to output_path
    - appends agent events to log_path
    - uses AgentMemory to adapt scoring (trend-aware)
    - asks LLM to decide next action after each cycle

    escalation_cooldown_cycles:
      Prevents "raise_attention" every cycle (more agent-like).
      Example: 2 => if last cycle escalated, next cycle will be downgraded to continue_monitoring.
    """
    mem = memory or AgentMemory()

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
                "demo": demo,
                "input_path": input_path,
                "output_path": output_path,
            },
            log_path,
        )

        # Trend BEFORE scoring (adaptive scoring uses it)
        trend_before = mem.risk_trend()

        transactions = load_transactions(demo=demo, input_path=input_path)
        cycle_alerts: List[Dict[str, Any]] = []

        for tx in transactions:
            # Adaptive scoring driven by memory trend
            # (fallback if your scoring.py doesn't support 'context')
            try:
                result = score_transaction(tx, context={"trend": trend_before})
            except TypeError:
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

            # Update memory AFTER decision
            trend_before_mem = mem.risk_trend()
            mem.update(cycle_alerts, decision)
            trend_after = mem.risk_trend()

            # Full snapshot (clean for demo + future dashboard)
            snapshot = mem.snapshot()

            write_jsonl(
                {
                    "type": "agent_memory_snapshot",
                    "cycle": c,
                    "timestamp": time.time(),
                    "trend_before": trend_before_mem,
                    "trend_after": trend_after,
                    "snapshot": snapshot,
                },
                log_path,
            )

            if not quiet:
                print("📊 Agent Memory Trend:", trend_after)
                print("Total Escalations:", snapshot["totals"]["escalations"])

            action = str(decision.get("next_action") or "continue_monitoring")

            # =========================
            # Cooldown logic: avoid escalating every cycle
            # =========================
            if action == "raise_attention":
                recent_escalations = mem.recent_escalations(window=escalation_cooldown_cycles)
                # If we already escalated in the last N cycles, downgrade
                if escalation_cooldown_cycles >= 1 and recent_escalations >= 2:
                    action = "continue_monitoring"
                    if not quiet:
                        print("⏳ Escalation cooldown: downgrading to continue_monitoring for this cycle.")

            # =========================
            # 🔥 Agent ACTS based on decision
            # =========================
            if action == "raise_attention":
                if not quiet:
                    print("🚨 AGENT ESCALATION: High risk cluster detected.")

                write_jsonl(
                    {
                        "type": "agent_action",
                        "cycle": c,
                        "timestamp": time.time(),
                        "action": "raise_attention",
                        "details": {
                            "reason": "LLM raised attention based on alert cluster",
                            "alerts_in_cycle": len(cycle_alerts),
                            "trend_after": trend_after,
                        },
                    },
                    log_path,
                )

            elif action == "stop":
                if not quiet:
                    print("🛑 AGENT STOPPING based on LLM recommendation.")

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
                break

            else:
                write_jsonl(
                    {
                        "type": "agent_action",
                        "cycle": c,
                        "timestamp": time.time(),
                        "action": "continue_monitoring",
                        "details": {"trend_after": trend_after},
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
