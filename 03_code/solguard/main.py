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
