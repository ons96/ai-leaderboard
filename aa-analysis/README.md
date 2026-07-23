# Artificial Analysis efficiency data

Snapshot data plus stdlib-only scrapers for two Artificial Analysis views:

- `data/aa-agentic-efficiency-enriched.csv`: 164 LLMs, including `intelligence_per_task_second` (Agentic Index divided by `timePerTaskSeconds`).
- `data/aa-coding-agents-xref.csv`: 44 coding-agent/harness rows cross-referenced to the underlying LLM when names match.

Regenerate the derived files from this directory:

```bash
python3 scripts/analyze-aa-efficiency.py \
  --agentic data/aa-agentic-index-full.csv \
  --coding data/aa-coding-agents-table2-all44.csv \
  --outdir data
```

`costPerTask` left blank by the source stays unknown; it is never treated as free.
