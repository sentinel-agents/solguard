# # from __future__ import annotations
# # from dataclasses import dataclass
# # from typing import Dict, List, Tuple, Any
# # import time


# # @dataclass
# # class ScoreResult:
# #     score: int
# #     reasons: List[str]


# # # --- Simple in-memory state (hackathon-friendly) ---
# # # Tracks last seen destinations and tx timestamps per sender.
# # _state: Dict[str, Dict[str, Any]] = {
# #     "seen_destinations": {},  # sender -> set(destinations)
# #     "tx_times": {},           # sender -> list[timestamps]
# # }


# # def _now_ts(tx: Dict[str, Any]) -> float:
# #     # Prefer tx timestamp if present, else current time.
# #     return float(tx.get("timestamp", time.time()))


# # def score_transaction(tx: Dict[str, Any]) -> ScoreResult:
# #     """
# #     Input tx example (flexible):
# #     {
# #       "id": "tx1",
# #       "sender": "walletA",
# #       "receiver": "walletB",
# #       "amount": 12.3,
# #       "token": "SOL",
# #       "program_id": "....",         # optional
# #       "timestamp": 1730000000.0,    # optional
# #       "is_new_destination": True,   # optional
# #     }
# #     """
# #     score = 0
# #     reasons: List[str] = []

# #     sender = str(tx.get("sender", "unknown_sender"))
# #     receiver = str(tx.get("receiver", "unknown_receiver"))
# #     amount = float(tx.get("amount", 0.0))
# #     token = str(tx.get("token", "UNKNOWN")).upper()
# #     program_id = tx.get("program_id")

# #     ts = _now_ts(tx)

# #     # --- Rule 1: High value transfer (simple threshold) ---
# #     # Tune thresholds later; keep simple for MVP.
# #     if token == "SOL" and amount >= 10:
# #         score += 40
# #         reasons.append("high_value_transfer_sol>=10")
# #     elif token != "SOL" and amount >= 1000:
# #         score += 35
# #         reasons.append("high_value_transfer_token>=1000")

# #     # --- Rule 2: New destination (per sender) ---
# #     seen = _state["seen_destinations"].setdefault(sender, set())
# #     if receiver not in seen and receiver != "unknown_receiver":
# #         score += 25
# #         reasons.append("new_destination_for_sender")
# #         seen.add(receiver)

# #     # If tx explicitly flags new destination, honor it too (won't duplicate reason).
# #     if tx.get("is_new_destination") is True and "new_destination_for_sender" not in reasons:
# #         score += 25
# #         reasons.append("new_destination_flagged")

# #     # --- Rule 3: High frequency (burst) ---
# #     # Count txs in last 60 seconds per sender.
# #     times = _state["tx_times"].setdefault(sender, [])
# #     times.append(ts)
# #     # Keep only last 60s
# #     cutoff = ts - 60
# #     times = [t for t in times if t >= cutoff]
# #     _state["tx_times"][sender] = times
# #     if len(times) >= 5:
# #         score += 30
# #         reasons.append("high_tx_frequency_5_in_60s")

# #     # --- Rule 4: Risky program interaction (placeholder list) ---
# #     # In Solana, program_id can hint at behavior. For MVP, allow a small denylist.
# #     risky_programs = {
# #         "MIXER_PROGRAM",
# #         "UNKNOWN_BRIDGE",
# #         "SUSPICIOUS_ROUTER",
# #     }
# #     if program_id and str(program_id) in risky_programs:
# #         score += 35
# #         reasons.append("interaction_with_risky_program_id")

# #     # --- Rule 5: Rounded amount pattern (very common in scam automation) ---
# #     # Not definitive, but helpful as a weak signal.
# #     if amount != 0 and abs(amount - round(amount)) < 1e-9:
# #         score += 10
# #         reasons.append("rounded_amount_pattern")

# #     # Cap score to 0-100
# #     score = max(0, min(100, score))

# #     # If nothing triggered, add a benign reason to avoid N/A
# #     if not reasons:
# #         reasons.append("no_strong_signals_detected")

# #     return ScoreResult(score=score, reasons=reasons)



# from __future__ import annotations

# from dataclasses import dataclass
# from typing import Dict, List, Any
# import time
# from datetime import datetime, timezone


# @dataclass
# class ScoreResult:
#     score: int
#     reasons: List[str]


# # --- Simple in-memory state (hackathon-friendly) ---
# # Tracks last seen destinations and tx timestamps per sender.
# _state: Dict[str, Dict[str, Any]] = {
#     "seen_destinations": {},  # sender -> set(destinations)
#     "tx_times": {},           # sender -> list[timestamps]
# }


# def _parse_ts(value: Any) -> float:
#     """
#     Accepts:
#     - float/int epoch seconds
#     - numeric strings (e.g., "1730000000", "1730000000.5")
#     - ISO 8601 strings like "2026-02-10T19:50:00Z"
#     Returns epoch seconds as float.
#     """
#     if value is None:
#         return time.time()

#     # Already numeric
#     if isinstance(value, (int, float)):
#         return float(value)

#     # String cases
#     if isinstance(value, str):
#         s = value.strip()
#         if not s:
#             return time.time()

#         # Numeric string
#         try:
#             return float(s)
#         except ValueError:
#             pass

#         # ISO 8601 (common: endswith 'Z')
#         try:
#             if s.endswith("Z"):
#                 dt = datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
#             else:
#                 # Python's fromisoformat supports "+00:00" but not "Z"
#                 dt = datetime.fromisoformat(s)
#                 if dt.tzinfo is None:
#                     dt = dt.replace(tzinfo=timezone.utc)
#             return dt.timestamp()
#         except Exception:
#             return time.time()

#     # Fallback
#     return time.time()


# def _now_ts(tx: Dict[str, Any]) -> float:
#     return _parse_ts(tx.get("timestamp"))


# def score_transaction(tx: Dict[str, Any]) -> ScoreResult:
#     """
#     Input tx example (flexible):
#     {
#       "transaction_id": "tx1" OR "id" OR "signature",
#       "sender": "walletA",          # optional
#       "receiver": "walletB",        # optional
#       "from": "walletA",            # optional alt key
#       "to": "walletB",              # optional alt key
#       "amount": 12.3,
#       "token": "SOL",
#       "program_id": "....",         # optional
#       "timestamp": 1730000000.0 OR "2026-02-10T19:50:00Z",
#       "is_new_destination": True,   # optional
#     }
#     """
#     score = 0
#     reasons: List[str] = []

#     # Support both {sender/receiver} and {from/to}
#     sender = str(tx.get("sender") or tx.get("from") or "unknown_sender")
#     receiver = str(tx.get("receiver") or tx.get("to") or "unknown_receiver")

#     # Amount may be missing or non-numeric in some logs; keep safe.
#     try:
#         amount = float(tx.get("amount", 0.0))
#     except Exception:
#         amount = 0.0

#     token = str(tx.get("token", "UNKNOWN")).upper()
#     program_id = tx.get("program_id")

#     ts = _now_ts(tx)

#     # --- Rule 1: High value transfer (simple threshold) ---
#     if token == "SOL" and amount >= 10:
#         score += 40
#         reasons.append("high_value_transfer_sol>=10")
#     elif token != "SOL" and amount >= 1000:
#         score += 35
#         reasons.append("high_value_transfer_token>=1000")

#     # --- Rule 2: New destination (per sender) ---
#     seen = _state["seen_destinations"].setdefault(sender, set())
#     if receiver not in seen and receiver != "unknown_receiver":
#         score += 25
#         reasons.append("new_destination_for_sender")
#         seen.add(receiver)

#     if tx.get("is_new_destination") is True and "new_destination_for_sender" not in reasons:
#         score += 25
#         reasons.append("new_destination_flagged")

#     # --- Rule 3: High frequency (burst) ---
#     times = _state["tx_times"].setdefault(sender, [])
#     times.append(ts)
#     cutoff = ts - 60
#     times = [t for t in times if t >= cutoff]
#     _state["tx_times"][sender] = times
#     if len(times) >= 5:
#         score += 30
#         reasons.append("high_tx_frequency_5_in_60s")

#     # --- Rule 4: Risky program interaction (placeholder list) ---
#     risky_programs = {"MIXER_PROGRAM", "UNKNOWN_BRIDGE", "SUSPICIOUS_ROUTER"}
#     if program_id and str(program_id) in risky_programs:
#         score += 35
#         reasons.append("interaction_with_risky_program_id")

#     # --- Rule 5: Rounded amount pattern ---
#     if amount != 0 and abs(amount - round(amount)) < 1e-9:
#         score += 10
#         reasons.append("rounded_amount_pattern")

#     score = max(0, min(100, score))

#     if not reasons:
#         reasons.append("no_strong_signals_detected")

#     return ScoreResult(score=score, reasons=reasons)


from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Any
import time
from datetime import datetime


@dataclass
class ScoreResult:
    score: int
    reasons: List[str]


# --- Simple in-memory state (hackathon-friendly) ---
_state: Dict[str, Dict[str, Any]] = {
    "seen_destinations": {},  # sender -> set(destinations)
    "tx_times": {},           # sender -> list[timestamps]
    "pair_times": {},         # (sender->receiver) -> list[timestamps]
}


def _parse_timestamp(value: Any) -> float:
    """
    Accepts:
    - float/int epoch seconds
    - ISO 8601 string like "2026-02-10T19:50:00Z"
    - fallback to now
    """
    if value is None:
        return time.time()

    # epoch number
    if isinstance(value, (int, float)):
        return float(value)

    # ISO string
    if isinstance(value, str):
        s = value.strip()
        try:
            # "Z" -> UTC
            if s.endswith("Z"):
                s = s[:-1] + "+00:00"
            return datetime.fromisoformat(s).timestamp()
        except Exception:
            return time.time()

    return time.time()


def _get_txid(tx: Dict[str, Any]) -> str:
    # robust id extraction
    return str(
        tx.get("transaction_id")
        or tx.get("id")
        or tx.get("signature")
        or tx.get("txid")
        or "unknown"
    )


def _get_sender(tx: Dict[str, Any]) -> str:
    return str(
        tx.get("sender")
        or tx.get("from")
        or tx.get("source")
        or tx.get("src")
        or "unknown_sender"
    )


def _get_receiver(tx: Dict[str, Any]) -> str:
    return str(
        tx.get("receiver")
        or tx.get("to")
        or tx.get("destination")
        or tx.get("dst")
        or "unknown_receiver"
    )


def _get_amount(tx: Dict[str, Any]) -> float:
    # supports amount/value/lamports
    if "amount" in tx:
        return float(tx.get("amount") or 0.0)
    if "value" in tx:
        return float(tx.get("value") or 0.0)
    if "lamports" in tx:
        # if lamports exist, convert to SOL-ish signal for demo
        return float(tx.get("lamports") or 0.0) / 1_000_000_000
    return 0.0


def _get_token(tx: Dict[str, Any]) -> str:
    # supports token/mint/symbol
    token = tx.get("token") or tx.get("symbol") or tx.get("mint") or "UNKNOWN"
    return str(token).upper()


def _now_ts(tx: Dict[str, Any]) -> float:
    return _parse_timestamp(tx.get("timestamp"))


def score_transaction(tx: Dict[str, Any]) -> ScoreResult:
    score = 0
    reasons: List[str] = []

    txid = _get_txid(tx)
    sender = _get_sender(tx)
    receiver = _get_receiver(tx)
    amount = _get_amount(tx)
    token = _get_token(tx)
    program_id = tx.get("program_id")
    ts = _now_ts(tx)

    # --- Hard sanity signals (make demo more “agent-like”) ---
    if sender == "unknown_sender":
        reasons.append("missing_sender_field")
    if receiver == "unknown_receiver":
        reasons.append("missing_receiver_field")

    # --- Rule 1: High value transfer ---
    # Make it pop in demo:
    if token == "SOL" and amount >= 10:
        score += 45
        reasons.append("high_value_transfer_sol>=10")
    elif token != "SOL" and amount >= 1000:
        score += 40
        reasons.append("high_value_transfer_token>=1000")

    # --- Rule 2: New destination (per sender) ---
    seen = _state["seen_destinations"].setdefault(sender, set())
    if receiver not in seen and receiver != "unknown_receiver":
        score += 25
        reasons.append("new_destination_for_sender")
        seen.add(receiver)

    # --- Rule 3: High frequency (burst) per sender ---
    times = _state["tx_times"].setdefault(sender, [])
    times.append(ts)
    cutoff = ts - 60
    times = [t for t in times if t >= cutoff]
    _state["tx_times"][sender] = times

    if len(times) >= 5:
        score += 35
        reasons.append("high_tx_frequency_5_in_60s")

    # --- Rule 4: Rapid repeated transfers to same receiver (pair burst) ---
    pair_key = f"{sender}->{receiver}"
    pair_times = _state["pair_times"].setdefault(pair_key, [])
    pair_times.append(ts)
    pair_times = [t for t in pair_times if t >= cutoff]
    _state["pair_times"][pair_key] = pair_times

    if len(pair_times) >= 3:
        score += 25
        reasons.append("repeated_transfers_same_pair_3_in_60s")

    # --- Rule 5: Risky program interaction (placeholder denylist) ---
    risky_programs = {"MIXER_PROGRAM", "UNKNOWN_BRIDGE", "SUSPICIOUS_ROUTER"}
    if program_id and str(program_id) in risky_programs:
        score += 40
        reasons.append("interaction_with_risky_program_id")

    # --- Rule 6: Rounded amount pattern (weak) ---
    if amount != 0 and abs(amount - round(amount)) < 1e-9:
        score += 10
        reasons.append("rounded_amount_pattern")

    # --- Rule 7: Self transfer (often automation / wash) ---
    if sender != "unknown_sender" and sender == receiver:
        score += 30
        reasons.append("self_transfer_pattern")

    # Cap score
    score = max(0, min(100, score))

    # If no meaningful reason triggered
    if not reasons:
        reasons.append("no_strong_signals_detected")

    # Keep txid accessible downstream if needed
    tx["transaction_id"] = tx.get("transaction_id") or tx.get("id") or tx.get("signature") or txid

    return ScoreResult(score=score, reasons=reasons)
