import json
from datetime import datetime
from pathlib import Path


def write_jsonl(record: dict, path: str = "alerts.jsonl") -> None:
    """
    Append a single JSON record as one line (JSONL).
    Safe for demo: easy to parse, grep, and ingest later.
    """
    # Ensure we don't crash if someone runs from different working dirs.
    out_path = Path(path)

    # Add a timestamp if not provided
    record = dict(record)
    record.setdefault("timestamp", datetime.utcnow().isoformat() + "Z")

    with out_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
