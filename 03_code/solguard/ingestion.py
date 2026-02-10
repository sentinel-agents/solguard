# def load_transactions():
#     return [
#         {"id": "tx1", "amount": 1200, "program": "unknown"},
#         {"id": "tx2", "amount": 5, "program": "trusted"},
#         {"id": "tx3", "amount": 9000, "program": "suspicious"},
#     ]
def load_transactions(demo: bool = False):
    """
    Load transactions.

    If demo=True, returns built-in demo transactions.
    Otherwise, this is where real Solana ingestion would happen later.
    """

    if demo:
        # Demo transactions (MVP / hackathon mode)
        return [
            {
                "transaction_id": "tx1",
                "amount": 1200,
                "token": "SOL",
                "from": "wallet_A",
                "to": "wallet_B",
            },
            {
                "transaction_id": "tx2",
                "amount": 45,
                "token": "SOL",
                "from": "wallet_C",
                "to": "wallet_D",
            },
            {
                "transaction_id": "tx3",
                "amount": 980,
                "token": "SOL",
                "from": "wallet_A",
                "to": "wallet_E",
            },
        ]

    # Placeholder for future real ingestion
    # (RPC Solana, streaming, indexer, etc.)
    return []
