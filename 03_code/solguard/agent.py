# from __future__ import annotations

# import time
# from typing import Optional, Dict, Any, List

# from solguard.ingestion import load_transactions
# from solguard.scoring import score_transaction
# from solguard.alerts import generate_alert
# from solguard.writer import write_jsonl  # keep using your existing writer


# def _pick_action(score: int, reasons: List[str]) -> Dict[str, Any]:
#     """
#     Agent decision policy (simple + demo-friendly).
#     This is where "agentic" behavior shows up.
#     """
#     if score >= 80:
#         return {
#             "action": "ESCALATE",
#             "priority": "P1",
#             "explanation": "High risk score. Escalate to human immediately.",
#             "next_steps": ["Open incident", "Collect evidence", "Notify on-call"],
#         }
#     if score >= 50:
#         return {
#             "action": "INVESTIGATE",
#             "priority": "P2",
#             "explanation": "Elevated risk. Investigate and correlate with other signals.",
#             "next_steps": ["Check source reputation", "Review recent activity", "Add to watchlist"],
#         }
#     if any("high_tx_frequency" in r for r in reasons):
#         return {
#             "action": "WATCH",
#             "priority": "P3",
#             "explanation": "Suspicious burst pattern. Monitor for repetition.",
#             "next_steps": ["Increase sampling", "Track sender/receiver patterns"],
#         }
#     return {
#         "action": "IGNORE",
#         "priority": "P4",
#         "explanation": "No strong signals detected.",
#         "next_steps": ["Continue monitoring"],
#     }


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
#     Autonomous agent loop:
#       perceive -> reason -> decide -> act (simulated) -> log -> sleep -> repeat
#     """
#     if not quiet:
#         print("🤖 SOLGUARD AGENT MODE starting...\n")

#     for cycle in range(1, cycles + 1):
#         cycle_start = time.time()

#         if not quiet:
#             print(f"===== Cycle {cycle}/{cycles} =====")

#         txs = load_transactions(demo=demo, input_path=input_path)
#         if not txs:
#             # Still log an agent heartbeat (agentic signal)
#             event = {
#                 "type": "agent_heartbeat",
#                 "cycle": cycle,
#                 "message": "No transactions available. Agent continues monitoring.",
#                 "timestamp": cycle_start,
#             }
#             write_jsonl(log_path, event)

#             if not quiet:
#                 print("No transactions found. Heartbeat logged.\n")

#             time.sleep(interval)
#             continue

#         for tx in txs:
#             result = score_transaction(tx)

#             alert = generate_alert(tx, result.score, result.reasons)
#             write_jsonl(alert, output_path)

#             decision = _pick_action(result.score, result.reasons)

#             # Agent log (this is what makes it “agentic” to reviewers)
#             agent_event = {
#                 "type": "agent_decision",
#                 "cycle": cycle,
#                 "timestamp": cycle_start,
#                 "tx_ref": (
#                     tx.get("transaction_id")
#                     or tx.get("id")
#                     or tx.get("signature")
#                     or "unknown"
#                 ),
#                 "perception": {
#                     "raw_tx_keys": sorted(list(tx.keys())),
#                 },
#                 "reasoning": {
#                     "score": result.score,
#                     "reasons": result.reasons,
#                 },
#                 "decision": decision,
#             }
#             write_jsonl(log_path, agent_event)

#             if not quiet:
#                 tx_ref = agent_event["tx_ref"]
#                 print(f"TX: {tx_ref}")
#                 print(f"Score: {result.score}")
#                 print(f"Reasons: {', '.join(result.reasons) if result.reasons else 'N/A'}")
#                 print(f"Decision: {decision['action']} ({decision['priority']})")
#                 print("-" * 40)

#         if not quiet:
#             elapsed = time.time() - cycle_start
#             print(f"Cycle complete in {elapsed:.2f}s. Sleeping {interval:.1f}s...\n")

#         time.sleep(interval)

#     if not quiet:
#         print("✅ SOLGUARD AGENT MODE finished.")
#         print(f"- Alerts written to: {output_path}")
#         print(f"- Agent logs written to: {log_path}")

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


def _tx_id(tx: Dict[str, Any]) -> str:
    """Best-effort transaction identifier (no drama if missing)."""
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

        # Ensure alert has a tx id
        txid = _tx_id(tx)
        alert = generate_alert(tx, result.score, result.reasons)
        if "transaction_id" not in alert or not alert.get("transaction_id"):
            alert["transaction_id"] = txid

        alerts.append(alert)
        _print_alert(alert, quiet=quiet)

        # IMPORTANT: writer.py expects (record, path)
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
    """
    Autonomous loop:
    - repeats run_once-like logic for N cycles
    - appends alerts to output_path
    - appends agent events to log_path
    """
    if not quiet:
        print("🤖 SOLGUARD AGENT MODE starting...\n")

    for c in range(1, cycles + 1):
        if not quiet:
            print(f"===== Cycle {c}/{cycles} =====")

        start_ts = time.time()
        event: Dict[str, Any] = {
            "type": "agent_cycle_start",
            "cycle": c,
            "timestamp": start_ts,
            "demo": demo,
            "input_path": input_path,
            "output_path": output_path,
        }
        write_jsonl(event, log_path)

        # Run one cycle
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

            # IMPORTANT: writer.py expects (record, path)
            write_jsonl(alert, output_path)

        end_ts = time.time()
        summary = {
            "type": "agent_cycle_end",
            "cycle": c,
            "timestamp": end_ts,
            "duration_sec": round(end_ts - start_ts, 3),
            "alerts_emitted": len(cycle_alerts),
        }
        write_jsonl(summary, log_path)

        if c < cycles:
            time.sleep(interval)

    if not quiet:
        print("\n🤖 AGENT MODE finished.\n")

    return 0
