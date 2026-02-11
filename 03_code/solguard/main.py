
# # # from solguard.ingestion import load_transactions
# # # from solguard.scoring import score_transaction
# # # from solguard.alerts import generate_alert, write_jsonl  # make sure write_jsonl exists here


# # # OUTPUT_PATH = "alerts.jsonl"


# # # def main():
# # #     print("🛡️ SOLGUARD starting...\n")

# # #     transactions = load_transactions()

# # #     # Optional: reset file each run (comment if you want append forever)
# # #     open(OUTPUT_PATH, "w", encoding="utf-8").close()

# # #     for tx in transactions:
# # #         result = score_transaction(tx)  # expects result.score + result.reasons
# # #         alert = generate_alert(tx, result.score, result.reasons)

# # #         # Console output (human-readable)
# # #         print(f"Transaction ID: {tx.get('id')}")
# # #         print(f"Risk score: {result.score}")
# # #         print(f"Alert: {alert.get('severity')}")
# # #         reasons = alert.get("reasons") or result.reasons or []
# # #         print(f"Reason: {', '.join(reasons) if reasons else 'N/A'}")
# # #         print("-" * 40)

# # #         # Persist output (machine-readable)
# # #         write_jsonl(OUTPUT_PATH, alert)


# # # if __name__ == "__main__":
# # #     main()
    
# # from solguard.ingestion import load_transactions
# # from solguard.scoring import score_transaction
# # from solguard.alerts import generate_alert, write_jsonl

# # OUTPUT_PATH = "alerts.jsonl"


# # def _decide_posture(high_count: int, medium_count: int, low_count: int) -> str:
# #     """
# #     Simple session-level decision (agent posture).
# #     Kept deterministic and explainable for MVP.
# #     """
# #     if high_count >= 1:
# #         return "CRITICAL"
# #     if medium_count >= 2:
# #         return "ELEVATED"
# #     if medium_count == 1:
# #         return "GUARDED"
# #     return "NORMAL"


# # def _recommendations(posture: str) -> list:
# #     """
# #     Human-friendly recommendations based on posture.
# #     """
# #     if posture == "CRITICAL":
# #         return [
# #             "Flag HIGH risk transactions for immediate manual review",
# #             "Monitor sender wallet activity closely (burst / new destinations)",
# #             "Consider blocking or limiting interactions if this is a controlled environment",
# #         ]
# #     if posture == "ELEVATED":
# #         return [
# #             "Review MEDIUM risk transactions",
# #             "Monitor for repeated patterns and follow-up transactions",
# #         ]
# #     if posture == "GUARDED":
# #         return [
# #             "Keep monitoring; review the flagged transaction reasons",
# #             "Escalate if similar patterns repeat",
# #         ]
# #     return [
# #         "No strong signals detected in this run",
# #         "Continue standard monitoring",
# #     ]


# # def main():
# #     print("🛡️ SOLGUARD starting...\n")

# #     transactions = load_transactions()

# #     # Reset output each run (simple + demo-friendly)
# #     open(OUTPUT_PATH, "w", encoding="utf-8").close()

# #     high_count = 0
# #     medium_count = 0
# #     low_count = 0

# #     for tx in transactions:
# #         result = score_transaction(tx)  # expects result.score + result.reasons
# #         alert = generate_alert(tx, result.score, result.reasons)

# #         # Count severities
# #         severity = (alert.get("severity") or "").upper()
# #         if "HIGH" in severity:
# #             high_count += 1
# #         elif "MEDIUM" in severity:
# #             medium_count += 1
# #         else:
# #             low_count += 1

# #         # Console output (human-readable)
# #         print(f"Transaction ID: {tx.get('id')}")
# #         print(f"Risk score: {result.score}")
# #         print(f"Alert: {alert.get('severity')}")

# #         reasons = alert.get("reasons") or result.reasons or []
# #         print(f"Reason: {', '.join(reasons) if reasons else 'N/A'}")
# #         print("-" * 40)

# #         # Persist output (machine-readable)
# #         write_jsonl(OUTPUT_PATH, alert)

# #     # --- Session-level agent decision (visible improvement) ---
# #     total = len(transactions)
# #     posture = _decide_posture(high_count, medium_count, low_count)
# #     recs = _recommendations(posture)

# #     print("\n🛡️ SOLGUARD SESSION SUMMARY")
# #     print(f"- Total transactions analyzed: {total}")
# #     print(f"- High risk alerts: {high_count}")
# #     print(f"- Medium risk alerts: {medium_count}")
# #     print(f"- Low risk alerts: {low_count}")

# #     print("\nAGENT POSTURE:")
# #     if posture == "CRITICAL":
# #         print("🚨 CRITICAL — high risk detected")
# #     elif posture == "ELEVATED":
# #         print("⚠️ ELEVATED — multiple medium risks detected")
# #     elif posture == "GUARDED":
# #         print("🟠 GUARDED — some risk signals detected")
# #     else:
# #         print("🟢 NORMAL — no strong signals detected")

# #     print("\nRECOMMENDATIONS:")
# #     for r in recs:
# #         print(f"- {r}")

# #     # Also write the session summary as a final JSONL record (optional but useful)
# #     summary_record = {
# #         "type": "session_summary",
# #         "total_transactions": total,
# #         "high": high_count,
# #         "medium": medium_count,
# #         "low": low_count,
# #         "posture": posture,
# #         "recommendations": recs,
# #     }
# #     write_jsonl(OUTPUT_PATH, summary_record)


# # if __name__ == "__main__":
# #     main()
# # solguard/main.py














# from typing import Optional

# from solguard.ingestion import load_transactions
# from solguard.scoring import score_transaction
# from solguard.alerts import generate_alert, write_jsonl


# def main(demo: bool = False, output_path: str = "alerts.jsonl", quiet: bool = False) -> int:
#     """
#     Orchestrates SOLGUARD pipeline:
#     - loads transactions
#     - scores each
#     - generates alert with reasons
#     - prints a human-readable summary
#     - writes JSONL alerts to disk
#     """
#     if not quiet:
#         print("🛡️ SOLGUARD starting...\n")

#     transactions = load_transactions(demo=demo)

#     alerts = []
#     for tx in transactions:
#         result = score_transaction(tx)           # expected to return an object/dict with score + reasons
#         #alert = generate_alert(tx, result)       # expected to return dict with severity + reasons, etc.
#         alert = generate_alert(tx, result.score, result.reasons)

#         alerts.append(alert)

#         if not quiet:
#             print(f"Transaction ID: {alert.get('transaction_id')}")
#             print(f"Risk score: {alert.get('score')}")
#             print(f"Alert: {alert.get('severity')}")
#             reasons = alert.get("reasons") or []
#             print(f"Reason: {', '.join(reasons) if reasons else 'N/A'}")
#             print("-" * 40)

#         # Persist each alert as JSONL line (machine-readable)
#         write_jsonl(output_path, alert)

#     # Session summary (small visible “product” touch)
#     if not quiet:
#         high = sum(1 for a in alerts if a.get("severity") == "HIGH RISK")
#         med = sum(1 for a in alerts if a.get("severity") == "MEDIUM RISK")
#         low = sum(1 for a in alerts if a.get("severity") == "LOW RISK")

#         print("\n🛡️ SOLGUARD SESSION SUMMARY")
#         print(f"- Total transactions analyzed: {len(alerts)}")
#         print(f"- High risk alerts: {high}")
#         print(f"- Medium risk alerts: {med}")
#         print(f"- Low risk alerts: {low}")
#         print("\nRECOMMENDATIONS:")
#         if high > 0:
#             print("- Investigate HIGH RISK transactions immediately")
#         if med > 0:
#             print("- Review MEDIUM RISK transactions")
#         if low == len(alerts):
#             print("- No suspicious activity detected in this run")
#         else:
#             print("- Monitor for repeated patterns and follow-up transactions")

#     return 0


from typing import Optional

from solguard.ingestion import load_transactions
from solguard.scoring import score_transaction
from solguard.alerts import generate_alert, write_jsonl


def main(
    demo: bool = False,
    input_path: Optional[str] = None,
    output_path: str = "alerts.jsonl",
    quiet: bool = False,
) -> int:
    if not quiet:
        print("🛡 SOLGUARD starting...\n")

    # ✅ critical: input_path is forwarded to ingestion when not in demo
    transactions = load_transactions(demo=demo, input_path=input_path)

    alerts = []
    for tx in transactions:
        result = score_transaction(tx)
        alert = generate_alert(tx, result.score, result.reasons)

        alerts.append(alert)

        if not quiet:
            txid = (
                alert.get("transaction_id")
                or tx.get("transaction_id")
                or tx.get("id")
                or tx.get("signature")
                or "unknown"
            )
            print(f"Transaction ID: {txid}")
            print(f"Risk score: {alert.get('score')}")
            print(f"Alert: {alert.get('severity')}")
            reasons = alert.get("reasons") or []
            print(f"Reason: {', '.join(reasons) if reasons else 'N/A'}")
            print("-" * 40)

        write_jsonl(output_path, alert)

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
        if len(alerts) == 0:
            print("- No transactions found (check input file or demo mode).")
        elif high > 0:
            print("- Investigate HIGH RISK transactions immediately")
        elif med > 0:
            print("- Review MEDIUM RISK transactions")
        else:
            print("- No suspicious activity detected in this run")

    return 0


