# 03_code/solguard/memory.py
from __future__ import annotations
from typing import Dict, Any


class AgentMemory:
    def __init__(self):
        self.total_cycles = 0
        self.total_alerts = 0
        self.total_high = 0
        self.total_medium = 0
        self.total_escalations = 0
        self.history = []

    def update(self, alerts, decision):
        self.total_cycles += 1
        self.total_alerts += len(alerts)

        high = sum(1 for a in alerts if a.get("severity") == "HIGH RISK")
        medium = sum(1 for a in alerts if a.get("severity") == "MEDIUM RISK")

        self.total_high += high
        self.total_medium += medium

        if decision.get("next_action") == "raise_attention":
            self.total_escalations += 1

        self.history.append({
            "cycle": self.total_cycles,
            "high": high,
            "medium": medium,
            "decision": decision.get("next_action")
        })

    def risk_trend(self) -> str:
        if self.total_high > 5:
            return "critical"
        if self.total_escalations > 3:
            return "escalating"
        if self.total_high == 0 and self.total_medium == 0:
            return "stable"
        return "monitoring"
