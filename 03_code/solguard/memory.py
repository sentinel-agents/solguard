# # # 03_code/solguard/memory.py
# # from __future__ import annotations
# # from typing import Dict, Any


# # class AgentMemory:
# #     def __init__(self):
# #         self.total_cycles = 0
# #         self.total_alerts = 0
# #         self.total_high = 0
# #         self.total_medium = 0
# #         self.total_escalations = 0
# #         self.history = []

# #     def update(self, alerts, decision):
# #         self.total_cycles += 1
# #         self.total_alerts += len(alerts)

# #         high = sum(1 for a in alerts if a.get("severity") == "HIGH RISK")
# #         medium = sum(1 for a in alerts if a.get("severity") == "MEDIUM RISK")

# #         self.total_high += high
# #         self.total_medium += medium

# #         if decision.get("next_action") == "raise_attention":
# #             self.total_escalations += 1

# #         self.history.append({
# #             "cycle": self.total_cycles,
# #             "high": high,
# #             "medium": medium,
# #             "decision": decision.get("next_action")
# #         })

# #     def risk_trend(self) -> str:
# #         if self.total_high > 5:
# #             return "critical"
# #         if self.total_escalations > 3:
# #             return "escalating"
# #         if self.total_high == 0 and self.total_medium == 0:
# #             return "stable"
# #         return "monitoring"


# # 03_code/solguard/memory.py
# from __future__ import annotations

# from dataclasses import dataclass, asdict
# from typing import Any, Dict, List, Optional


# @dataclass
# class CycleRecord:
#     cycle: int
#     high: int
#     medium: int
#     low: int
#     decision: str
#     alerts_count: int


# class AgentMemory:
#     """
#     Lightweight in-process memory (hackathon-friendly).
#     Keeps aggregate counters + bounded cycle history.
#     Exposes trend + snapshot for logs / dashboards.
#     """

#     def __init__(self, *, max_history: int = 50) -> None:
#         self.max_history = max_history

#         self.total_cycles: int = 0
#         self.total_alerts: int = 0
#         self.total_high: int = 0
#         self.total_medium: int = 0
#         self.total_low: int = 0
#         self.total_escalations: int = 0

#         self.history: List[CycleRecord] = []

#     def update(self, alerts: List[Dict[str, Any]], decision: Dict[str, Any]) -> CycleRecord:
#         """
#         Update counters for a completed cycle. Returns the created record.
#         """
#         self.total_cycles += 1
#         self.total_alerts += len(alerts)

#         high = sum(1 for a in alerts if a.get("severity") == "HIGH RISK")
#         medium = sum(1 for a in alerts if a.get("severity") == "MEDIUM RISK")
#         low = sum(1 for a in alerts if a.get("severity") == "LOW RISK")

#         self.total_high += high
#         self.total_medium += medium
#         self.total_low += low

#         next_action = str(decision.get("next_action") or "continue_monitoring")
#         if next_action == "raise_attention":
#             self.total_escalations += 1

#         rec = CycleRecord(
#             cycle=self.total_cycles,
#             high=high,
#             medium=medium,
#             low=low,
#             decision=next_action,
#             alerts_count=len(alerts),
#         )
#         self.history.append(rec)

#         # keep bounded history
#         if len(self.history) > self.max_history:
#             self.history = self.history[-self.max_history :]

#         return rec

#     def recent_escalations(self, window: int = 5) -> int:
#         """
#         Escalations in last N cycles (windowed signal).
#         """
#         w = max(1, int(window))
#         recent = self.history[-w:]
#         return sum(1 for r in recent if r.decision == "raise_attention")

#     def recent_high(self, window: int = 5) -> int:
#         w = max(1, int(window))
#         recent = self.history[-w:]
#         return sum(r.high for r in recent)

#     def risk_trend(self) -> str:
#         """
#         Very small heuristic trend label.
#         (Used by scoring to adapt thresholds/bias.)
#         """
#         # strong global signals
#         if self.total_high >= 8:
#             return "critical"

#         # recent tempo matters more than totals
#         if self.recent_escalations(window=5) >= 3:
#             return "escalating"

#         if self.total_cycles > 0 and self.total_high == 0 and self.total_medium == 0:
#             return "stable"

#         return "monitoring"

#     def snapshot(self) -> Dict[str, Any]:
#         """
#         Safe dict for logs / LLM context (small + useful).
#         """
#         trend = self.risk_trend()
#         last: Optional[CycleRecord] = self.history[-1] if self.history else None
#         return {
#             "trend": trend,
#             "totals": {
#                 "cycles": self.total_cycles,
#                 "alerts": self.total_alerts,
#                 "high": self.total_high,
#                 "medium": self.total_medium,
#                 "low": self.total_low,
#                 "escalations": self.total_escalations,
#             },
#             "recent": {
#                 "last_cycle": asdict(last) if last else None,
#                 "escalations_last_5": self.recent_escalations(5),
#                 "high_last_5": self.recent_high(5),
#             },
#         }


# 03_code/solguard/memory.py
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class CycleRecord:
    cycle: int
    high: int
    medium: int
    low: int
    decision: str
    alerts_count: int
    trend_before: str = "monitoring"
    trend_after: str = "monitoring"


class AgentMemory:
    """
    Lightweight in-process memory (hackathon-friendly).
    Keeps aggregate counters + bounded cycle history.
    Exposes trend + snapshot for logs / dashboards.

    Philosophy:
    - Recent behavior matters more than lifetime totals
    - Trend should be stable enough to use as a signal (scoring bias / LLM context)
    """

    def __init__(self, *, max_history: int = 50, window: int = 5) -> None:
        self.max_history = int(max_history)
        self.window = max(1, int(window))

        self.total_cycles: int = 0
        self.total_alerts: int = 0
        self.total_high: int = 0
        self.total_medium: int = 0
        self.total_low: int = 0
        self.total_escalations: int = 0

        self.history: List[CycleRecord] = []

    # -------------------------
    # Core update
    # -------------------------

    def update(self, alerts: List[Dict[str, Any]], decision: Dict[str, Any]) -> CycleRecord:
        """
        Update counters for a completed cycle. Returns the created record.
        Adds trend_before/trend_after so agent.py can log cleanly.
        """
        trend_before = self.risk_trend()

        self.total_cycles += 1
        self.total_alerts += len(alerts)

        high = sum(1 for a in alerts if a.get("severity") == "HIGH RISK")
        medium = sum(1 for a in alerts if a.get("severity") == "MEDIUM RISK")
        low = sum(1 for a in alerts if a.get("severity") == "LOW RISK")

        self.total_high += high
        self.total_medium += medium
        self.total_low += low

        next_action = str(decision.get("next_action") or "continue_monitoring")
        if next_action == "raise_attention":
            self.total_escalations += 1

        # Build record (trend_after computed after we append it)
        rec = CycleRecord(
            cycle=self.total_cycles,
            high=high,
            medium=medium,
            low=low,
            decision=next_action,
            alerts_count=len(alerts),
            trend_before=trend_before,
            trend_after=trend_before,  # placeholder
        )

        self.history.append(rec)

        # keep bounded history
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history :]

        # Now compute trend_after using the updated history/totals
        rec.trend_after = self.risk_trend()

        return rec

    # -------------------------
    # Window helpers
    # -------------------------

    def _recent(self, window: Optional[int] = None) -> List[CycleRecord]:
        w = self.window if window is None else max(1, int(window))
        return self.history[-w:]

    def recent_escalations(self, window: Optional[int] = None) -> int:
        recent = self._recent(window)
        return sum(1 for r in recent if r.decision == "raise_attention")

    def recent_high(self, window: Optional[int] = None) -> int:
        recent = self._recent(window)
        return sum(r.high for r in recent)

    def recent_medium(self, window: Optional[int] = None) -> int:
        recent = self._recent(window)
        return sum(r.medium for r in recent)

    def recent_risk_points(self, window: Optional[int] = None) -> int:
        """
        Weighted recent risk (simple, interpretable):
        - high counts more than medium, medium more than low
        """
        recent = self._recent(window)
        points = 0
        for r in recent:
            points += (r.high * 3) + (r.medium * 1)
        return points

    # -------------------------
    # Trend heuristic
    # -------------------------

    def risk_trend(self) -> str:
        """
        Trend label driven primarily by recent window.
        Returns: stable | monitoring | escalating | critical
        """
        if self.total_cycles == 0:
            return "monitoring"

        # Recent signals
        esc = self.recent_escalations()
        hi = self.recent_high()
        med = self.recent_medium()
        pts = self.recent_risk_points()

        # CRITICAL:
        # - lots of high risk recently
        # - or persistent escalations + high risk weight
        if hi >= 6 or (esc >= 3 and hi >= 3) or pts >= 18:
            return "critical"

        # ESCALATING:
        # - escalations keep happening
        # - or repeated high/medium clusters
        if esc >= 2 or hi >= 3 or (hi >= 1 and med >= 6) or pts >= 10:
            return "escalating"

        # STABLE:
        # - no high/medium recently and overall empty
        if self.total_high == 0 and self.total_medium == 0:
            return "stable"

        return "monitoring"

    # -------------------------
    # Optional “agent acts” helpers
    # -------------------------

    def should_stop(self) -> bool:
        """
        A conservative stop gate (optional).
        Useful if you want the agent to halt automatically in extreme conditions,
        or to prevent spending tokens forever.
        """
        # Example: too many critical cycles in a row (window-based)
        if self.risk_trend() == "critical" and self.recent_escalations() >= 3:
            return True
        return False

    def recommended_cooldown(self) -> float:
        """
        Suggest an interval multiplier based on trend (optional).
        You can use: time.sleep(interval * recommended_cooldown()).
        """
        t = self.risk_trend()
        if t == "stable":
            return 1.5
        if t == "monitoring":
            return 1.0
        if t == "escalating":
            return 0.75
        if t == "critical":
            return 0.5
        return 1.0

    # -------------------------
    # Snapshots
    # -------------------------

    def snapshot(self) -> Dict[str, Any]:
        """
        Safe dict for logs / dashboards (small + useful).
        """
        trend = self.risk_trend()
        last: Optional[CycleRecord] = self.history[-1] if self.history else None
        return {
            "trend": trend,
            "window": self.window,
            "totals": {
                "cycles": self.total_cycles,
                "alerts": self.total_alerts,
                "high": self.total_high,
                "medium": self.total_medium,
                "low": self.total_low,
                "escalations": self.total_escalations,
            },
            "recent": {
                "last_cycle": asdict(last) if last else None,
                "escalations_last_window": self.recent_escalations(),
                "high_last_window": self.recent_high(),
                "medium_last_window": self.recent_medium(),
                "risk_points_last_window": self.recent_risk_points(),
            },
        }

    def llm_context(self) -> Dict[str, Any]:
        """
        Even smaller snapshot to feed the LLM (optional).
        Keeps tokens low but still gives “memory”.
        """
        s = self.snapshot()
        return {
            "trend": s["trend"],
            "recent": {
                "high_last_window": s["recent"]["high_last_window"],
                "medium_last_window": s["recent"]["medium_last_window"],
                "escalations_last_window": s["recent"]["escalations_last_window"],
            },
            "totals": {
                "cycles": s["totals"]["cycles"],
                "escalations": s["totals"]["escalations"],
            },
        }
