from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple, Any
import time


@dataclass
class ScoreResult:
    score: int
    reasons: List[str]


# --- Simple in-memory state (hackathon-friendly) ---
# Tracks last seen destinations and tx timestamps per sender.
_state: Dict[str, Dict[str, Any]] = {
    "seen_destinations": {},  # sender -> set(destinations)
    "tx_times": {},           # sender -> list[timestamps]
}


def _now_ts(tx: Dict[str, Any]) -> float:
    # Prefer tx timestamp if present, else current time.
    return float(tx.get("timestamp", time.time()))


def score_transaction(tx: Dict[str, Any]) -> ScoreResult:
    """
    Input tx example (flexible):
    {
      "id": "tx1",
      "sender": "walletA",
      "receiver": "walletB",
      "amount": 12.3,
      "token": "SOL",
      "program_id": "....",         # optional
      "timestamp": 1730000000.0,    # optional
      "is_new_destination": True,   # optional
    }
    """
    score = 0
    reasons: List[str] = []

    sender = str(tx.get("sender", "unknown_sender"))
    receiver = str(tx.get("receiver", "unknown_receiver"))
    amount = float(tx.get("amount", 0.0))
    token = str(tx.get("token", "UNKNOWN")).upper()
    program_id = tx.get("program_id")

    ts = _now_ts(tx)

    # --- Rule 1: High value transfer (simple threshold) ---
    # Tune thresholds later; keep simple for MVP.
    if token == "SOL" and amount >= 10:
        score += 40
        reasons.append("high_value_transfer_sol>=10")
    elif token != "SOL" and amount >= 1000:
        score += 35
        reasons.append("high_value_transfer_token>=1000")

    # --- Rule 2: New destination (per sender) ---
    seen = _state["seen_destinations"].setdefault(sender, set())
    if receiver not in seen and receiver != "unknown_receiver":
        score += 25
        reasons.append("new_destination_for_sender")
        seen.add(receiver)

    # If tx explicitly flags new destination, honor it too (won't duplicate reason).
    if tx.get("is_new_destination") is True and "new_destination_for_sender" not in reasons:
        score += 25
        reasons.append("new_destination_flagged")

    # --- Rule 3: High frequency (burst) ---
    # Count txs in last 60 seconds per sender.
    times = _state["tx_times"].setdefault(sender, [])
    times.append(ts)
    # Keep only last 60s
    cutoff = ts - 60
    times = [t for t in times if t >= cutoff]
    _state["tx_times"][sender] = times
    if len(times) >= 5:
        score += 30
        reasons.append("high_tx_frequency_5_in_60s")

    # --- Rule 4: Risky program interaction (placeholder list) ---
    # In Solana, program_id can hint at behavior. For MVP, allow a small denylist.
    risky_programs = {
        "MIXER_PROGRAM",
        "UNKNOWN_BRIDGE",
        "SUSPICIOUS_ROUTER",
    }
    if program_id and str(program_id) in risky_programs:
        score += 35
        reasons.append("interaction_with_risky_program_id")

    # --- Rule 5: Rounded amount pattern (very common in scam automation) ---
    # Not definitive, but helpful as a weak signal.
    if amount != 0 and abs(amount - round(amount)) < 1e-9:
        score += 10
        reasons.append("rounded_amount_pattern")

    # Cap score to 0-100
    score = max(0, min(100, score))

    # If nothing triggered, add a benign reason to avoid N/A
    if not reasons:
        reasons.append("no_strong_signals_detected")

    return ScoreResult(score=score, reasons=reasons)
