# # # def load_transactions():
# # #     return [
# # #         {"id": "tx1", "amount": 1200, "program": "unknown"},
# # #         {"id": "tx2", "amount": 5, "program": "trusted"},
# # #         {"id": "tx3", "amount": 9000, "program": "suspicious"},
# # #     ]
# # def load_transactions(demo: bool = False):
# #     """
# #     Load transactions.

# #     If demo=True, returns built-in demo transactions.
# #     Otherwise, this is where real Solana ingestion would happen later.
# #     """

# #     if demo:
# #         # Demo transactions (MVP / hackathon mode)
# #         return [
# #             {
# #                 "transaction_id": "tx1",
# #                 "amount": 1200,
# #                 "token": "SOL",
# #                 "from": "wallet_A",
# #                 "to": "wallet_B",
# #             },
# #             {
# #                 "transaction_id": "tx2",
# #                 "amount": 45,
# #                 "token": "SOL",
# #                 "from": "wallet_C",
# #                 "to": "wallet_D",
# #             },
# #             {
# #                 "transaction_id": "tx3",
# #                 "amount": 980,
# #                 "token": "SOL",
# #                 "from": "wallet_A",
# #                 "to": "wallet_E",
# #             },
# #         ]

# #     # Placeholder for future real ingestion
# #     # (RPC Solana, streaming, indexer, etc.)
# #     return []


# import json
# from typing import List, Dict, Any, Optional


# def load_transactions(demo: bool = False, input_path: Optional[str] = None) -> List[Dict[str, Any]]:
#     """
#     If demo=True, returns built-in demo transactions.
#     If demo=False, loads transactions from a JSONL file (one JSON object per line).

#     Important: we skip non-transaction lines (e.g., {"type": "session_summary", ...}).
#     """
#     if demo:
#         return [
#             {"transaction_id": "tx1", "sender": "wallet_A", "receiver": "wallet_B", "amount": 12.0, "token": "SOL"},
#             {"transaction_id": "tx2", "sender": "wallet_C", "receiver": "wallet_D", "amount": 0.5, "token": "SOL"},
#             {"transaction_id": "tx3", "sender": "wallet_A", "receiver": "wallet_E", "amount": 8.0, "token": "SOL"},
#         ]

#     if not input_path:
#         input_path = "alerts.jsonl"

#     txs: List[Dict[str, Any]] = []
#     with open(input_path, "r", encoding="utf-8") as f:
#         for line in f:
#             line = line.strip()
#             if not line:
#                 continue

#             obj = json.loads(line)

#             # Skip meta lines (example: session summaries)
#             if isinstance(obj, dict) and obj.get("type") == "session_summary":
#                 continue

#             txs.append(obj)

#     return txs


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
