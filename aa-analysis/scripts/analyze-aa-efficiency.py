#!/usr/bin/env python3
# ponytail: stdlib-only, no pandas. Computes efficiency columns on the 164-model
# agentic-index CSV, prints top-20-per-metric rankings, and emits a cross-reference
# view that enriches coding-agents rows with the underlying LLM's raw speed/cost
# from the agentic dataset (matched by display name suffix).
#
# Inputs (all paths relative to ~/CodingProjects/ unless --agentic/--coding given):
#   aa-agentic-index-full.csv        -- 164-model agentic index (from parse-aa-rsc-chunk27.py)
#   aa-coding-agents-table2-all44.csv -- 44 agent-harness combos (from scrape-aa-coding-agents.py)
#
# Output: writes enriched CSVs next to inputs, prints rankings to stdout.
#
# Usage:
#   python3 analyze-aa-efficiency.py
#   python3 analyze-aa-efficiency.py --agentic path/to.csv --coding path/to.csv --top 30

import argparse
import csv
import os
import re
import sys
from pathlib import Path

DEFAULT_AGENTIC = Path.home() / "CodingProjects" / "aa-agentic-index-full.csv"
DEFAULT_CODING  = Path.home() / "CodingProjects" / "aa-coding-agents-table2-all44.csv"

# --- ponytail: load once, derive in-place, no intermediate dataframes ---

def to_float(v, default=0.0):
    if v is None or v == "":
        return default
    try:
        return float(v)
    except (ValueError, TypeError):
        return default


def load_agentic(path):
    """Return list[dict] with original + derived columns.
    Missing cost/time are None (not 0) -> excluded from per-cost / per-second
    rankings rather than producing misleading +inf."""
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            idx   = to_float(r.get("headlineValue"))
            tps   = to_float(r.get("medianTPS"))
            ttft  = to_float(r.get("medianTTFT"))
            secs  = to_float(r.get("timePerTaskSeconds"))
            # missing cost -> None; numeric 0 stays 0 (genuinely free)
            cost_raw = (r.get("costPerTask") or "").strip()
            cost = float(cost_raw) if cost_raw else None
            intel = to_float(r.get("intelligenceIndex"))

            r["cost_known"]        = "true" if cost is not None else "false"
            r["time_known"]        = "true" if secs > 0 else "false"
            # derived: None when denom missing, +inf when denom is genuinely 0 (free / instant)
            r["idx_per_cost"]      = (idx / cost) if cost is not None and cost > 0 else (float("inf") if cost == 0 else "")
            r["idx_per_second"]    = (idx / secs) if secs > 0 else ""
            r["intelligence_per_task_second"] = r["idx_per_second"]
            r["combined_efficiency"] = (idx * idx / (cost * secs)) if (cost is not None and cost > 0 and secs > 0) else (float("inf") if cost == 0 and secs > 0 else "")
            r["ttft_sec"] = ttft / 1000.0 if ttft else 0.0
            rows.append(r)
    return rows


def load_coding(path):
    """Return list[dict] preserving original columns."""
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


# --- name-matching for cross-ref ---
# coding-agents uses "<Harness> - <LLM display>" e.g. "Codex - GPT-5.6 Sol (max)"
# agentic uses "<name>" e.g. "GPT-5.6 Sol (max)" — exact suffix match.

def build_agentic_name_index(agentic_rows):
    """Map lowercase exact name -> agentic row (first wins on dup).
    Also indexes alias-normalized keys so '(none)' matches '(Non-reasoning)'."""
    idx = {}
    for r in agentic_rows:
        key = (r.get("name") or "").strip().lower()
        if key and key not in idx:
            idx[key] = r
            # alias-variant key
        m = VARIANT_RE.search(r.get("name") or "")
        if m:
            base = (r.get("name") or "")[:m.start()].strip().lower()
            var = _norm(m.group(1))
            akey = f"{base} ({var})"
            if akey not in idx:
                idx[akey] = r
    return idx


# Reasoning variant normalization: AA agentic uses parenthetical qualifiers like
# "(max)", "(xhigh)", "(low)", "(medium)", "(high)". Coding-agents names usually
# carry the SAME qualifier suffix. So exact-suffix (agentic full name) match
# should hit most rows. Fall back: strip qualifier, try base-name match.

VARIANT_RE = re.compile(r"\s*\(([^()]*)\)\s*$")  # only outermost paren

# ponytail: variant alias map for naming mismatches between AA datasets.
# Coding-agents uses '(none)' where agentic uses '(Non-reasoning)';
# 'Opus 4.8' base without qualifier matches Fable-5's "(Adaptive ...)" entry divergent.
ALIASES = {
    "none": "non-reasoning",
}

def _norm(s):
    return ALIASES.get(s.strip().lower(), s.strip().lower())

def base_name(name):
    m = VARIANT_RE.search(name or "")
    return (name[:m.start()] if m else name or "").strip().lower()


def build_base_name_index(agentic_rows):
    idx = {}
    for r in agentic_rows:
        b = base_name(r.get("name"))
        if b and b not in idx:
            idx[b] = r
    return idx


def cross_ref(coding_row, agentic_rows, exact_idx, base_idx):
    """Extract LLM display from 'Agent - Model', match to agentic row.
    Normalizes '(none)' <-> '(Non-reasoning)' via alias map."""
    raw = coding_row.get("Agent - Model") or ""
    if " - " in raw:
        harness, model = raw.split(" - ", 1)
    else:
        harness, model = "?", raw
    model = model.strip()
    # direct exact
    key = model.lower()
    if key in exact_idx:
        return harness, model, exact_idx[key]
    # alias-normalized key: rewrite outermost paren if present
    m = VARIANT_RE.search(model)
    if m:
        base = model[:m.start()].strip().lower()
        var = _norm(m.group(1))
        akey = f"{base} ({var})"
        if akey in exact_idx:
            return harness, model, exact_idx[akey]
    # base-name fallback
    b = base_name(model)
    if b in base_idx:
        return harness, model, base_idx[b]
    return harness, model, None


# --- output writers ---

def write_enriched_agentic(rows, out_path, top_n):
    """Write enriched agentic CSV with derived columns appended."""
    fields = list(rows[0].keys()) if rows else []
    # ensure derived cols present in field order
    for c in ("idx_per_cost", "idx_per_second", "intelligence_per_task_second", "combined_efficiency", "ttft_sec"):
        if c not in fields:
            fields.append(c)
    rows_sorted = sorted(rows, key=lambda r: to_float(r.get("headlineValue"), -1), reverse=True)
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows_sorted:
            w.writerow({k: r.get(k, "") for k in fields})
    return rows_sorted


def print_ranking(rows, title, key, n=20, reverse=True, fmt="{:.4f}", skip_missing=True, skip_inf=False):
    print(f"\n## {title} (top {n})")
    print(f"{'rank':<5}{'name':<55}{'idx':<8}{key:<22}{'tps':<10}{'cost':<12}")
    def val(r):
        v = r.get(key)
        if v == "" or v is None:
            return None
        if isinstance(v, str):
            try:
                return float(v)
            except ValueError:
                # 'inf' string from float() repr
                if v == "inf":
                    return float("inf")
                return None
        return v
    # filter + sort
    cand = []
    for r in rows:
        v = val(r)
        if v is None and skip_missing:
            continue
        if skip_inf and v == float("inf"):
            continue
        cand.append((v, r))
    cand.sort(key=lambda t: t[0] if t[0] is not None else (-1e18 if reverse else 1e18), reverse=reverse)
    for i, (v, r) in enumerate(cand[:n], 1):
        if v is None:
            vs = ""
        elif v == float("inf"):
            vs = "inf"
        else:
            try:
                vs = fmt.format(v)
            except (ValueError, TypeError):
                vs = str(v)
        name = (r.get('name') or '')[:54]
        print(f"{i:<5}{name:<55}{(r.get('headlineValue') or '')[:7]:<8}"
              f"{vs:<22}{(r.get('medianTPS') or '')[:9]:<10}{(r.get('costPerTask') or '')[:11]:<12}")


def write_cross_ref_csv(coding_rows, agentic_rows, out_path):
    exact = build_agentic_name_index(agentic_rows)
    base  = build_base_name_index(agentic_rows)
    # build field list from first row + our injected columns
    base_fields = list(coding_rows[0].keys()) if coding_rows else []
    injected = ["agent", "llm_match", "match_status"]
    agentic_fields = ["agentic_idx", "agentic_tps", "agentic_ttft_ms",
                      "agentic_cost_per_task", "agentic_time_sec",
                      "idx_per_cost", "idx_per_second", "combined_efficiency"]
    # original coding cols first, then injected + agentic enrichments
    fields = base_fields + injected + agentic_fields
    matched, missed = 0, 0
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for cr in coding_rows:
            harness, model, ag = cross_ref(cr, agentic_rows, exact, base)
            row = dict(cr)  # original fields
            row["agent"] = harness
            row["llm_match"] = model
            row["match_status"] = "EXACT" if (ag and (ag.get("name") or "").lower() == model.strip().lower()) else ("BASE" if ag else "MISS")
            if ag:
                matched += 1
                row["agentic_idx"]            = ag.get("headlineValue", "")
                row["agentic_tps"]            = ag.get("medianTPS", "")
                row["agentic_ttft_ms"]        = ag.get("medianTTFT", "")
                row["agentic_cost_per_task"]  = ag.get("costPerTask", "")
                row["agentic_time_sec"]       = ag.get("timePerTaskSeconds", "")
                row["idx_per_cost"]           = ag.get("idx_per_cost", "")
                row["idx_per_second"]         = ag.get("idx_per_second", "")
                row["combined_efficiency"]    = ag.get("combined_efficiency", "")
            else:
                missed += 1
                for k in agentic_fields:
                    row[k] = ""
            w.writerow(row)
    print(f"\n## Cross-reference: {matched}/{len(coding_rows)} coding rows matched, {missed} missed.")
    print(f"   written: {out_path}")
    return matched, missed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agentic", default=str(DEFAULT_AGENTIC))
    ap.add_argument("--coding",  default=str(DEFAULT_CODING))
    ap.add_argument("--top", type=int, default=20)
    ap.add_argument("--outdir", default="", help="output dir (default: alongside inputs)")
    args = ap.parse_args()

    agentic_path = Path(args.agentic)
    coding_path  = Path(args.coding)
    if not agentic_path.exists():
        sys.exit(f"missing agentic CSV: {agentic_path}")
    if not coding_path.exists():
        sys.exit(f"missing coding CSV:  {coding_path}")

    outdir = Path(args.outdir) if args.outdir else agentic_path.parent
    outdir.mkdir(parents=True, exist_ok=True)

    print(f"# AA Agentic efficiency analysis (lib=stdlib, n0={0})")
    print(f"agentic: {agentic_path}")
    print(f"coding:  {coding_path}")

    agentic = load_agentic(agentic_path)
    coding  = load_coding(coding_path)
    print(f"loaded: agentic={len(agentic)} rows, coding={len(coding)} rows")

    # write enriched CSV (sorted by headlineValue desc)
    enriched_out = outdir / "aa-agentic-efficiency-enriched.csv"
    write_enriched_agentic(agentic, enriched_out, args.top)
    print(f"wrote enriched: {enriched_out}")

    # 4 rankings — per-cost skips missing cost ( incompetence == empty in CSV)
    print_ranking(agentic, "Agentic Index (raw)", "headlineValue",
                 n=args.top, reverse=True, fmt="{:.2f}")
    print_ranking(agentic, "Intelligence per Cost (idx/$, requires known cost)", "idx_per_cost",
                 n=args.top, reverse=True, fmt="{:.2f}", skip_inf=False)
    print_ranking(agentic, "Intelligence per Second (idx/sec, requires known time)", "idx_per_second",
                 n=args.top, reverse=True, fmt="{:.4f}")
    print_ranking(agentic, "Combined Efficiency idx^2/($*sec, requires cost+time)", "combined_efficiency",
                 n=args.top, reverse=True, fmt="{:.4f}", skip_inf=False)
    # inverse: cheapest tasks
    print_ranking(agentic, "Cheapest per Task (known cost asc)", "costPerTask",
                 n=args.top, reverse=False, fmt="{:.4f}")
    # inverse: TTFT (lower better)
    print_ranking(agentic, "Fastest TTFT (ms asc)", "medianTTFT",
                 n=args.top, reverse=False, fmt="{:.0f}")
    # free-tier claimed + known time -> best of both worlds
    free_with_time = [r for r in agentic if r.get("costPerTask","").strip() == "0" and to_float(r.get("timePerTaskSeconds")) > 0]
    if free_with_time:
        # manually sort by idx desc
        free_with_time.sort(key=lambda r: to_float(r.get("headlineValue"), -1), reverse=True)
        print(f"\n## Free-tier models with measured time (idx desc, top {min(args.top, len(free_with_time))})")
        print(f"{'rank':<5}{'name':<55}{'idx':<8}{'tps':<10}{'time_sec':<12}")
        for i, r in enumerate(free_with_time[:args.top], 1):
            name = (r.get('name') or '')[:54]
            print(f"{i:<5}{name:<55}{(r.get('headlineValue') or '')[:7]:<8}{(r.get('medianTPS') or '')[:9]:<10}{(r.get('timePerTaskSeconds') or '')[:11]:<12}")

    # cross-reference CSV
    xref_out = outdir / "aa-coding-agents-xref.csv"
    matched, missed = write_cross_ref_csv(coding, agentic, xref_out)

    # demo self-check
    assert len(agentic) > 0 and len(coding) > 0, "empty inputs"
    top0 = to_float(agentic[0].get("headlineValue"))
    assert top0 > 0, "top agentic index should be > 0"
    print("\n[ok] self-check: agentic rows loaded, top idx positive, no exceptions")

if __name__ == "__main__":
    main()
