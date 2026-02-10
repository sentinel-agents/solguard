
from __future__ import annotations
from typing import Dict, Any, List

import json


def write_jsonl(path, item):
    """
    Append one alert as JSON line (machine-readable).
    """
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(item) + "\n")



def _severity(score: int) -> str:
    if score >= 80:
        return "HIGH"
    if score >= 40:
        return "MEDIUM"
    return "LOW"


def generate_alert(tx: Dict[str, Any], score: int, reasons: List[str]) -> Dict[str, Any]:
    """
    Returns a structured alert object for console output + later JSON export.
    """
    sev = _severity(score)

    return {
        "transaction_id": tx.get("id", "unknown"),
        "severity": f"{sev} RISK",
        "score": score,
        "reasons": reasons,
    }





