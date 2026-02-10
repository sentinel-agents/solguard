# SOLGUARD

SOLGUARD is an AI-assisted risk detection agent prototype for Solana-style transaction activity (MVP).

## What SOLGUARD does (MVP)
SOLGUARD analyzes a list of transactions, assigns a **risk score**, generates an **alert severity** (LOW / MEDIUM / HIGH),
and explains **why** an alert was triggered using clear detection reasons (rules-based reasoning).

✅ Output is produced in two ways:
- **Console output** (human-readable) for quick demo
- **alerts.jsonl** (machine-readable JSON Lines) for future automation, dashboards, or agent workflows

## Why it matters
On-chain activity can include suspicious behaviors (high-value transfers, unusual patterns, etc.).
SOLGUARD helps quickly highlight risky transactions and provides explainable reasons to support triage.

## Project structure
- `03_code/solguard/ingestion.py` → loads transactions (MVP data source)
- `03_code/solguard/scoring.py` → risk scoring logic
- `03_code/solguard/alerts.py` → alert generation + reasons + JSONL writing
- `03_code/solguard/main.py` → runs the pipeline end-to-end

## How to run
Open a terminal and go to the code folder:

```bash
cd 03_code
python3 -m solguard.main
