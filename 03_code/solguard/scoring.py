# # from __future__ import annotations

# # from dataclasses import dataclass
# # from typing import Dict, List, Any
# # import time
# # from datetime import datetime



# # @dataclass
# # class ScoreResult:
# #     score: int
# #     reasons: List[str]


# # # --- Simple in-memory state (hackathon-friendly) ---
# # _state: Dict[str, Dict[str, Any]] = {
# #     "seen_destinations": {},  # sender -> set(destinations)
# #     "tx_times": {},           # sender -> list[timestamps]
# #     "pair_times": {},         # (sender->receiver) -> list[timestamps]
# # }


# # def _parse_timestamp(value: Any) -> float:
# #     """
# #     Accepts:
# #     - float/int epoch seconds
# #     - ISO 8601 string like "2026-02-10T19:50:00Z"
# #     - fallback to now
# #     """
# #     if value is None:
# #         return time.time()

# #     # epoch number
# #     if isinstance(value, (int, float)):
# #         return float(value)

# #     # ISO string
# #     if isinstance(value, str):
# #         s = value.strip()
# #         try:
# #             # "Z" -> UTC
# #             if s.endswith("Z"):
# #                 s = s[:-1] + "+00:00"
# #             return datetime.fromisoformat(s).timestamp()
# #         except Exception:
# #             return time.time()

# #     return time.time()


# # def _get_txid(tx: Dict[str, Any]) -> str:
# #     # robust id extraction
# #     return str(
# #         tx.get("transaction_id")
# #         or tx.get("id")
# #         or tx.get("signature")
# #         or tx.get("txid")
# #         or "unknown"
# #     )


# # def _get_sender(tx: Dict[str, Any]) -> str:
# #     return str(
# #         tx.get("sender")
# #         or tx.get("from")
# #         or tx.get("source")
# #         or tx.get("src")
# #         or "unknown_sender"
# #     )


# # def _get_receiver(tx: Dict[str, Any]) -> str:
# #     return str(
# #         tx.get("receiver")
# #         or tx.get("to")
# #         or tx.get("destination")
# #         or tx.get("dst")
# #         or "unknown_receiver"
# #     )


# # def _get_amount(tx: Dict[str, Any]) -> float:
# #     # supports amount/value/lamports
# #     if "amount" in tx:
# #         return float(tx.get("amount") or 0.0)
# #     if "value" in tx:
# #         return float(tx.get("value") or 0.0)
# #     if "lamports" in tx:
# #         # if lamports exist, convert to SOL-ish signal for demo
# #         return float(tx.get("lamports") or 0.0) / 1_000_000_000
# #     return 0.0


# # def _get_token(tx: Dict[str, Any]) -> str:
# #     # supports token/mint/symbol
# #     token = tx.get("token") or tx.get("symbol") or tx.get("mint") or "UNKNOWN"
# #     return str(token).upper()


# # def _now_ts(tx: Dict[str, Any]) -> float:
# #     return _parse_timestamp(tx.get("timestamp"))


# # def score_transaction(tx: Dict[str, Any]) -> ScoreResult:
# #     score = 0
# #     reasons: List[str] = []

# #     txid = _get_txid(tx)
# #     sender = _get_sender(tx)
# #     receiver = _get_receiver(tx)
# #     amount = _get_amount(tx)
# #     token = _get_token(tx)
# #     program_id = tx.get("program_id")
# #     ts = _now_ts(tx)

# #     # --- Hard sanity signals (make demo more “agent-like”) ---
# #     if sender == "unknown_sender":
# #         reasons.append("missing_sender_field")
# #     if receiver == "unknown_receiver":
# #         reasons.append("missing_receiver_field")

# #     # --- Rule 1: High value transfer ---
# #     # Make it pop in demo:
# #     if token == "SOL" and amount >= 10:
# #         score += 45
# #         reasons.append("high_value_transfer_sol>=10")
# #     elif token != "SOL" and amount >= 1000:
# #         score += 40
# #         reasons.append("high_value_transfer_token>=1000")

# #     # --- Rule 2: New destination (per sender) ---
# #     seen = _state["seen_destinations"].setdefault(sender, set())
# #     if receiver not in seen and receiver != "unknown_receiver":
# #         score += 25
# #         reasons.append("new_destination_for_sender")
# #         seen.add(receiver)

# #     # --- Rule 3: High frequency (burst) per sender ---
# #     times = _state["tx_times"].setdefault(sender, [])
# #     times.append(ts)
# #     cutoff = ts - 60
# #     times = [t for t in times if t >= cutoff]
# #     _state["tx_times"][sender] = times

# #     if len(times) >= 5:
# #         score += 35
# #         reasons.append("high_tx_frequency_5_in_60s")

# #     # --- Rule 4: Rapid repeated transfers to same receiver (pair burst) ---
# #     pair_key = f"{sender}->{receiver}"
# #     pair_times = _state["pair_times"].setdefault(pair_key, [])
# #     pair_times.append(ts)
# #     pair_times = [t for t in pair_times if t >= cutoff]
# #     _state["pair_times"][pair_key] = pair_times

# #     if len(pair_times) >= 3:
# #         score += 25
# #         reasons.append("repeated_transfers_same_pair_3_in_60s")

# #     # --- Rule 5: Risky program interaction (placeholder denylist) ---
# #     risky_programs = {"MIXER_PROGRAM", "UNKNOWN_BRIDGE", "SUSPICIOUS_ROUTER"}
# #     if program_id and str(program_id) in risky_programs:
# #         score += 40
# #         reasons.append("interaction_with_risky_program_id")

# #     # --- Rule 6: Rounded amount pattern (weak) ---
# #     if amount != 0 and abs(amount - round(amount)) < 1e-9:
# #         score += 10
# #         reasons.append("rounded_amount_pattern")

# #     # --- Rule 7: Self transfer (often automation / wash) ---
# #     if sender != "unknown_sender" and sender == receiver:
# #         score += 30
# #         reasons.append("self_transfer_pattern")

# #     # Cap score
# #     score = max(0, min(100, score))

# #     # If no meaningful reason triggered
# #     if not reasons:
# #         reasons.append("no_strong_signals_detected")

# #     # Keep txid accessible downstream if needed
# #     tx["transaction_id"] = tx.get("transaction_id") or tx.get("id") or tx.get("signature") or txid

# #     return ScoreResult(score=score, reasons=reasons)




# from __future__ import annotations

# from dataclasses import dataclass, field
# from datetime import datetime
# from typing import Any, Dict, List, Optional, Set, Tuple
# import time


# # =========================
# # Public API
# # =========================

# @dataclass
# class ScoreResult:
#     score: int
#     reasons: List[str]


# @dataclass
# class ScoringConfig:
#     """
#     Tunables (no magic numbers).
#     Keep hackathon-friendly defaults.
#     """

#     # Time window for burst checks
#     window_seconds: int = 60

#     # Value thresholds
#     sol_high_value_threshold: float = 10.0
#     token_high_value_threshold: float = 1000.0

#     # Burst thresholds
#     sender_burst_count: int = 5
#     pair_burst_count: int = 3

#     # Points
#     points_high_value_sol: int = 45
#     points_high_value_token: int = 40
#     points_new_destination: int = 25
#     points_sender_burst: int = 35
#     points_pair_burst: int = 25
#     points_risky_program: int = 40
#     points_rounded_amount: int = 10
#     points_self_transfer: int = 30

#     # Program denylist (placeholder)
#     risky_program_ids: Set[str] = field(
#         default_factory=lambda: {"MIXER_PROGRAM", "UNKNOWN_BRIDGE", "SUSPICIOUS_ROUTER"}
#     )

#     # Score clamp
#     score_min: int = 0
#     score_max: int = 100

#     # Behaviors
#     ignore_unknown_receiver_for_new_destination: bool = True


# # --- Simple in-memory state (hackathon-friendly) ---
# # Sender -> set(destinations)
# _seen_destinations: Dict[str, Set[str]] = {}
# # Sender -> list[timestamps]
# _sender_times: Dict[str, List[float]] = {}
# # (sender, receiver) -> list[timestamps]
# _pair_times: Dict[Tuple[str, str], List[float]] = {}


# def reset_scoring_state() -> None:
#     """Optional: useful for tests / demo resets."""
#     _seen_destinations.clear()
#     _sender_times.clear()
#     _pair_times.clear()


# def score_transaction(tx: Dict[str, Any], config: Optional[ScoringConfig] = None) -> ScoreResult:
#     cfg = config or ScoringConfig()

#     score = 0
#     reasons: List[str] = []

#     txid = _get_txid(tx)
#     sender = _get_sender(tx)
#     receiver = _get_receiver(tx)
#     amount = _get_amount(tx)
#     token = _get_token(tx)
#     program_id = tx.get("program_id")
#     ts = _now_ts(tx)

#     # --- Hard sanity signals ---
#     if sender == "unknown_sender":
#         reasons.append("missing_sender_field")
#     if receiver == "unknown_receiver":
#         reasons.append("missing_receiver_field")

#     # --- Rule 1: High value transfer ---
#     if token == "SOL" and amount >= cfg.sol_high_value_threshold:
#         score += cfg.points_high_value_sol
#         reasons.append(f"high_value_transfer_sol>={_fmt(cfg.sol_high_value_threshold)}")
#     elif token != "SOL" and amount >= cfg.token_high_value_threshold:
#         score += cfg.points_high_value_token
#         reasons.append(f"high_value_transfer_token>={_fmt(cfg.token_high_value_threshold)}")

#     # --- Rule 2: New destination per sender ---
#     seen = _seen_destinations.setdefault(sender, set())
#     receiver_is_unknown = receiver == "unknown_receiver"
#     if not receiver_is_unknown or not cfg.ignore_unknown_receiver_for_new_destination:
#         if receiver not in seen and receiver != "unknown_receiver":
#             score += cfg.points_new_destination
#             reasons.append("new_destination_for_sender")
#             seen.add(receiver)

#     # --- Rule 3: High frequency burst per sender ---
#     sender_list = _sender_times.setdefault(sender, [])
#     sender_list.append(ts)
#     sender_list = _prune_times(sender_list, ts, cfg.window_seconds)
#     _sender_times[sender] = sender_list

#     if len(sender_list) >= cfg.sender_burst_count:
#         score += cfg.points_sender_burst
#         reasons.append(f"high_tx_frequency_{cfg.sender_burst_count}_in_{cfg.window_seconds}s")

#     # --- Rule 4: Repeated transfers same pair in window ---
#     pair_key = (sender, receiver)
#     pair_list = _pair_times.setdefault(pair_key, [])
#     pair_list.append(ts)
#     pair_list = _prune_times(pair_list, ts, cfg.window_seconds)
#     _pair_times[pair_key] = pair_list

#     if len(pair_list) >= cfg.pair_burst_count:
#         score += cfg.points_pair_burst
#         reasons.append(f"repeated_transfers_same_pair_{cfg.pair_burst_count}_in_{cfg.window_seconds}s")

#     # --- Rule 5: Risky program interaction (denylist) ---
#     if program_id and str(program_id) in cfg.risky_program_ids:
#         score += cfg.points_risky_program
#         reasons.append("interaction_with_risky_program_id")

#     # --- Rule 6: Rounded amount pattern ---
#     if amount != 0.0 and _is_rounded(amount):
#         score += cfg.points_rounded_amount
#         reasons.append("rounded_amount_pattern")

#     # --- Rule 7: Self transfer pattern ---
#     if sender != "unknown_sender" and sender == receiver:
#         score += cfg.points_self_transfer
#         reasons.append("self_transfer_pattern")

#     # Clamp score
#     score = max(cfg.score_min, min(cfg.score_max, score))

#     if not reasons:
#         reasons.append("no_strong_signals_detected")

#     # Keep txid accessible downstream if needed
#     tx["transaction_id"] = tx.get("transaction_id") or tx.get("id") or tx.get("signature") or txid

#     return ScoreResult(score=score, reasons=reasons)


# # =========================
# # Helpers
# # =========================

# def _prune_times(times: List[float], now_ts: float, window_seconds: int) -> List[float]:
#     cutoff = now_ts - float(window_seconds)
#     return [t for t in times if t >= cutoff]


# def _is_rounded(amount: float, eps: float = 1e-9) -> bool:
#     return abs(amount - round(amount)) < eps


# def _parse_timestamp(value: Any) -> float:
#     """
#     Accepts:
#     - float/int epoch seconds
#     - ISO 8601 string like "2026-02-10T19:50:00Z"
#     - fallback to now
#     """
#     if value is None:
#         return time.time()

#     if isinstance(value, (int, float)):
#         return float(value)

#     if isinstance(value, str):
#         s = value.strip()
#         try:
#             if s.endswith("Z"):
#                 s = s[:-1] + "+00:00"
#             return datetime.fromisoformat(s).timestamp()
#         except Exception:
#             return time.time()

#     return time.time()


# def _now_ts(tx: Dict[str, Any]) -> float:
#     return _parse_timestamp(tx.get("timestamp"))


# def _get_txid(tx: Dict[str, Any]) -> str:
#     return str(
#         tx.get("transaction_id")
#         or tx.get("id")
#         or tx.get("signature")
#         or tx.get("txid")
#         or "unknown"
#     )


# def _get_sender(tx: Dict[str, Any]) -> str:
#     return str(
#         tx.get("sender")
#         or tx.get("from")
#         or tx.get("source")
#         or tx.get("src")
#         or "unknown_sender"
#     )


# def _get_receiver(tx: Dict[str, Any]) -> str:
#     return str(
#         tx.get("receiver")
#         or tx.get("to")
#         or tx.get("destination")
#         or tx.get("dst")
#         or "unknown_receiver"
#     )


# def _get_amount(tx: Dict[str, Any]) -> float:
#     if "amount" in tx:
#         return float(tx.get("amount") or 0.0)
#     if "value" in tx:
#         return float(tx.get("value") or 0.0)
#     if "lamports" in tx:
#         return float(tx.get("lamports") or 0.0) / 1_000_000_000
#     return 0.0


# def _get_token(tx: Dict[str, Any]) -> str:
#     token = tx.get("token") or tx.get("symbol") or tx.get("mint") or "UNKNOWN"
#     return str(token).upper()


# def _fmt(x: float) -> str:
#     # pretty threshold formatting for reasons
#     if float(x).is_integer():
#         return str(int(x))
#     return str(x)

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple
import time


# =========================
# Public API
# =========================

@dataclass
class ScoreResult:
    score: int
    reasons: List[str]


@dataclass
class ScoringConfig:
    """
    Tunables (no magic numbers).
    Keep hackathon-friendly defaults.
    """

    # Time window for burst checks
    window_seconds: int = 60

    # Value thresholds
    sol_high_value_threshold: float = 10.0
    token_high_value_threshold: float = 1000.0

    # Burst thresholds
    sender_burst_count: int = 5
    pair_burst_count: int = 3

    # Points
    points_high_value_sol: int = 45
    points_high_value_token: int = 40
    points_new_destination: int = 25
    points_sender_burst: int = 35
    points_pair_burst: int = 25
    points_risky_program: int = 40
    points_rounded_amount: int = 10
    points_self_transfer: int = 30

    # Program denylist (placeholder)
    risky_program_ids: Set[str] = field(
        default_factory=lambda: {"MIXER_PROGRAM", "UNKNOWN_BRIDGE", "SUSPICIOUS_ROUTER"}
    )

    # Score clamp
    score_min: int = 0
    score_max: int = 100

    # Behaviors
    ignore_unknown_receiver_for_new_destination: bool = True

    # Adaptive knobs (used when context["trend"] escalates)
    adaptive_enabled: bool = True
    adaptive_max_bonus_points: int = 15  # cap for added sensitivity (keeps it stable)
    adaptive_sol_threshold_floor: float = 5.0  # never go lower than this
    adaptive_token_threshold_floor: float = 500.0  # never go lower than this


# =========================
# Simple in-memory state (hackathon-friendly)
# =========================
_seen_destinations: Dict[str, Set[str]] = {}                 # sender -> set(destinations)
_sender_times: Dict[str, List[float]] = {}                  # sender -> list[timestamps]
_pair_times: Dict[Tuple[str, str], List[float]] = {}        # (sender, receiver) -> list[timestamps]


def reset_scoring_state() -> None:
    """Optional: useful for tests / demo resets."""
    _seen_destinations.clear()
    _sender_times.clear()
    _pair_times.clear()


def score_transaction(
    tx: Dict[str, Any],
    config: Optional[ScoringConfig] = None,
    context: Optional[Dict[str, Any]] = None,
) -> ScoreResult:
    """
    Deterministic scoring with optional adaptive layer driven by agent memory.
    context example:
      {"trend": "monitoring"|"stable"|"escalating"|"critical"}
    """
    cfg = config or ScoringConfig()
    ctx = context or {}
    trend = str(ctx.get("trend", "monitoring")).lower().strip()

    score = 0
    reasons: List[str] = []

    txid = _get_txid(tx)
    sender = _get_sender(tx)
    receiver = _get_receiver(tx)
    amount = _get_amount(tx)
    token = _get_token(tx)
    program_id = tx.get("program_id")
    ts = _now_ts(tx)

    # =========================
    # Adaptive policy (lightweight)
    # =========================
    # We do *small* shifts only:
    # - slightly lower high-value thresholds when trend escalates
    # - slightly boost some points, capped
    sol_thr = cfg.sol_high_value_threshold
    tok_thr = cfg.token_high_value_threshold

    bonus = 0
    if cfg.adaptive_enabled:
        if trend == "stable":
            bonus = 0
        elif trend == "monitoring":
            bonus = 2
        elif trend == "escalating":
            bonus = 8
        elif trend == "critical":
            bonus = 12
        else:
            bonus = 2  # unknown trend -> mild

        bonus = min(cfg.adaptive_max_bonus_points, max(0, bonus))

        # lower thresholds gently when escalating/critical
        if trend in {"escalating", "critical"}:
            sol_thr = max(cfg.adaptive_sol_threshold_floor, sol_thr * 0.8)   # 10 -> 8
            tok_thr = max(cfg.adaptive_token_threshold_floor, tok_thr * 0.8) # 1000 -> 800

    # =========================
    # Hard sanity signals
    # =========================
    if sender == "unknown_sender":
        reasons.append("missing_sender_field")
    if receiver == "unknown_receiver":
        reasons.append("missing_receiver_field")

    # =========================
    # Rule 1: High value transfer
    # =========================
    if token == "SOL" and amount >= sol_thr:
        score += (cfg.points_high_value_sol + (bonus if trend in {"escalating", "critical"} else 0))
        reasons.append(f"high_value_transfer_sol>={_fmt(sol_thr)}")
        if sol_thr != cfg.sol_high_value_threshold:
            reasons.append("adaptive_threshold_lowered")
    elif token != "SOL" and amount >= tok_thr:
        score += (cfg.points_high_value_token + (bonus if trend in {"escalating", "critical"} else 0))
        reasons.append(f"high_value_transfer_token>={_fmt(tok_thr)}")
        if tok_thr != cfg.token_high_value_threshold:
            reasons.append("adaptive_threshold_lowered")

    # =========================
    # Rule 2: New destination per sender
    # =========================
    seen = _seen_destinations.setdefault(sender, set())
    receiver_is_unknown = receiver == "unknown_receiver"

    if not receiver_is_unknown or not cfg.ignore_unknown_receiver_for_new_destination:
        if receiver not in seen and receiver != "unknown_receiver":
            # In escalating/critical mode, slightly boost new-destination sensitivity
            add = cfg.points_new_destination + (bonus // 2 if trend in {"escalating", "critical"} else 0)
            score += add
            reasons.append("new_destination_for_sender")
            seen.add(receiver)

    # =========================
    # Rule 3: High frequency burst per sender
    # =========================
    sender_list = _sender_times.setdefault(sender, [])
    sender_list.append(ts)
    sender_list = _prune_times(sender_list, ts, cfg.window_seconds)
    _sender_times[sender] = sender_list

    if len(sender_list) >= cfg.sender_burst_count:
        # Mild boost if escalating/critical, but keep bounded
        add = cfg.points_sender_burst + (bonus // 2 if trend in {"escalating", "critical"} else 0)
        score += add
        reasons.append(f"high_tx_frequency_{cfg.sender_burst_count}_in_{cfg.window_seconds}s")

    # =========================
    # Rule 4: Repeated transfers same pair in window
    # =========================
    pair_key = (sender, receiver)
    pair_list = _pair_times.setdefault(pair_key, [])
    pair_list.append(ts)
    pair_list = _prune_times(pair_list, ts, cfg.window_seconds)
    _pair_times[pair_key] = pair_list

    if len(pair_list) >= cfg.pair_burst_count:
        add = cfg.points_pair_burst + (bonus // 2 if trend in {"escalating", "critical"} else 0)
        score += add
        reasons.append(f"repeated_transfers_same_pair_{cfg.pair_burst_count}_in_{cfg.window_seconds}s")

    # =========================
    # Rule 5: Risky program interaction (denylist)
    # =========================
    if program_id and str(program_id) in cfg.risky_program_ids:
        add = cfg.points_risky_program + (bonus if trend in {"escalating", "critical"} else 0)
        score += add
        reasons.append("interaction_with_risky_program_id")

    # =========================
    # Rule 6: Rounded amount pattern
    # =========================
    if amount != 0.0 and _is_rounded(amount):
        # Rounded pattern stays weak; tiny boost only in critical
        add = cfg.points_rounded_amount + (2 if trend == "critical" else 0)
        score += add
        reasons.append("rounded_amount_pattern")

    # =========================
    # Rule 7: Self transfer pattern
    # =========================
    if sender != "unknown_sender" and sender == receiver:
        add = cfg.points_self_transfer + (bonus // 2 if trend in {"escalating", "critical"} else 0)
        score += add
        reasons.append("self_transfer_pattern")

    # Clamp score
    score = max(cfg.score_min, min(cfg.score_max, score))

    if not reasons:
        reasons.append("no_strong_signals_detected")

    # Keep txid accessible downstream if needed
    tx["transaction_id"] = tx.get("transaction_id") or tx.get("id") or tx.get("signature") or txid

    # Optional trace (helps show "agentic adaptation" in logs)
    if cfg.adaptive_enabled and trend in {"monitoring", "escalating", "critical"}:
        reasons.append(f"memory_trend={trend}")

    return ScoreResult(score=score, reasons=reasons)


# =========================
# Helpers
# =========================

def _prune_times(times: List[float], now_ts: float, window_seconds: int) -> List[float]:
    cutoff = now_ts - float(window_seconds)
    return [t for t in times if t >= cutoff]


def _is_rounded(amount: float, eps: float = 1e-9) -> bool:
    return abs(amount - round(amount)) < eps


def _parse_timestamp(value: Any) -> float:
    """
    Accepts:
    - float/int epoch seconds
    - ISO 8601 string like "2026-02-10T19:50:00Z"
    - fallback to now
    """
    if value is None:
        return time.time()

    if isinstance(value, (int, float)):
        return float(value)

    if isinstance(value, str):
        s = value.strip()
        try:
            if s.endswith("Z"):
                s = s[:-1] + "+00:00"
            return datetime.fromisoformat(s).timestamp()
        except Exception:
            return time.time()

    return time.time()


def _now_ts(tx: Dict[str, Any]) -> float:
    return _parse_timestamp(tx.get("timestamp"))


def _get_txid(tx: Dict[str, Any]) -> str:
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
    if "amount" in tx:
        return float(tx.get("amount") or 0.0)
    if "value" in tx:
        return float(tx.get("value") or 0.0)
    if "lamports" in tx:
        return float(tx.get("lamports") or 0.0) / 1_000_000_000
    return 0.0


def _get_token(tx: Dict[str, Any]) -> str:
    token = tx.get("token") or tx.get("symbol") or tx.get("mint") or "UNKNOWN"
    return str(token).upper()


def _fmt(x: float) -> str:
    if float(x).is_integer():
        return str(int(x))
    return str(x)

