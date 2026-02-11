import json
from typing import List, Dict, Any, Optional


def load_transactions(demo: bool = False, input_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    demo=True  -> returns built-in demo transactions (with transaction_id)
    demo=False -> loads JSONL file (one JSON object per line)
                 and ensures each tx has a stable transaction_id (no 'unknown').
    """
    if demo:
        return [
            {"transaction_id": "tx1", "amount": 1200, "token": "SOL", "sender": "wallet_A", "receiver": "wallet_B"},
            {"transaction_id": "tx2", "amount": 45, "token": "SOL", "sender": "wallet_C", "receiver": "wallet_D"},
            {"transaction_id": "tx3", "amount": 980, "token": "SOL", "sender": "wallet_A", "receiver": "wallet_E"},
        ]

    if not input_path:
        input_path = "alerts.jsonl"

    txs: List[Dict[str, Any]] = []
    with open(input_path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)

            # Skip non-transaction lines (ex: summaries)
            if obj.get("type") == "session_summary":
                continue

            # Ensure an ID exists (no more 'unknown')
            obj.setdefault("transaction_id", obj.get("id") or obj.get("signature") or f"seed_line_{idx:04d}")

            txs.append(obj)

    return txs
