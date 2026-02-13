# 03_code/solguard/llm.py
from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv



# Lazy import to avoid hard dependency when LLM is not used
def _get_client():
    from openai import OpenAI  # type: ignore
    return OpenAI()

def llm_decide_next_step(
    *,
    cycle: int,
    txs: List[Dict[str, Any]],
    alerts: List[Dict[str, Any]],
    max_chars: int = 1800,
) -> Dict[str, Any]:
    """
    Returns a small decision object:
    {
      "agent_summary": "...",
      "next_action": "continue_monitoring|raise_attention|stop",
      "suggested_checks": ["...","..."]
    }
    """
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-5")

    # If no key, return a deterministic fallback (still works in demo).
    if not api_key:
        return {
            "agent_summary": "LLM disabled (OPENAI_API_KEY missing). Using deterministic monitoring.",
            "next_action": "continue_monitoring",
            "suggested_checks": ["Add OPENAI_API_KEY in .env to enable LLM narration."],
        }

    # Keep the prompt small and safe (don’t dump huge objects)
    compact = {
        "cycle": cycle,
        "tx_count": len(txs),
        "alerts_count": len(alerts),
        "alerts_sample": alerts[:5],  # enough for the demo
    }
    compact_json = json.dumps(compact, ensure_ascii=False)[:max_chars]

    instructions = (
        "You are SOLGUARD, a security agent. "
        "Given alerts produced by a deterministic rules engine, "
        "summarize what happened and decide the next step.\n\n"
        "Return STRICT JSON with keys: agent_summary, next_action, suggested_checks.\n"
        "next_action must be one of: continue_monitoring, raise_attention, stop.\n"
        "suggested_checks must be a short list.\n"
        "Do NOT include markdown, only JSON."
    )

    client = _get_client()

    # Responses API (official)
    response = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": instructions},
            {"role": "user", "content": compact_json},
        ],
        # store=False is optional; keep default if you want
    )

    text = (response.output_text or "").strip()

    # Try parse JSON; fallback if model returns unexpected output
    try:
        obj = json.loads(text)
        if not isinstance(obj, dict):
            raise ValueError("Not a dict")
        return {
            "agent_summary": str(obj.get("agent_summary", ""))[:600],
            "next_action": str(obj.get("next_action", "continue_monitoring")),
            "suggested_checks": obj.get("suggested_checks", []) if isinstance(obj.get("suggested_checks"), list) else [],
        }
    except Exception:
        return {
            "agent_summary": (text[:600] or "LLM produced unparsable output."),
            "next_action": "continue_monitoring",
            "suggested_checks": ["Tighten prompt / enforce JSON format."],
        }
