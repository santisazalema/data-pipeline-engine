# High-Throughput Data Pipeline ETL & Profiler

A modular, production-ready ETL (Extract, Transform, Load) pipeline engine written in Python. It ingests large-scale public dataset streams, applies strict data sanitation/typing, persists records into relational storage via optimized batch upserts, and generates aggregated profiler metrics directly from SQL.

---

## Architecture Overview

```text
[ External API / Stream ]
         │
         ▼
[ GitHubExtractor ]     ──> Network retries, rate-limit awareness & pagination
         │
         ▼
[ DataTransformer ]     ──> Type coercion, schema validation & string sanitation
         │
         ▼
[ DatabaseManager ]     ──> Bulk UPSERT (executemany) & indexing (SQLite / PostgreSQL)
         │
         ▼
[ CLI Profiler ]        ──> Terminal analytics and latency benchmarks (Rich)
```

---

## Engineering Highlights

* **Optimized Batch Ingestion:** Uses bulk upsert (`executemany` with `ON CONFLICT DO UPDATE`) to handle high-frequency updates without row-by-row locking overhead.
* **Relational Indexing:** Built with dedicated B-Tree indexes on query-heavy attributes (`language`, `stars DESC`) for rapid analytical slicing.
* **Resilient Extraction:** Implements timeout protections, safe error propagation, and HTTP 403 rate-limit backoffs.
* **Strict Data Sanitation:** Enforces integer coercion for numeric columns, handles null representations, and trims corrupted string payloads before database entry.

---

## Setup & Execution

### Environment Initialization

```bash
git clone https://github.com/santisazalema/data-pipeline-engine.git
cd data-pipeline-engine
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Run Pipeline

Ingest top repositories with custom queries and pagination:

```bash
python main.py --query "stars:>10000" --pages 2 --per-page 25
```

### Run Test Suite

```bash
pytest -v
```
