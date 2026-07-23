#!/usr/bin/env python3
"""Parse AA chunk 27 RSC flight data: extract model_name ↔ agentic_index_score pairs.

Usage:
  python3 parse-aa-rsc-chunk27.py                     # download + extract + print table
  python3 parse-aa-rsc-chunk27.py --csv                # output CSV
  python3 parse-aa-rsc-chunk27.py --json               # output JSON
  python3 parse-aa-rsc-chunk27.py --chunk-url <url>    # override chunk URL
"""

import re, sys, json, gzip, io, argparse
from urllib.request import urlopen, Request

# Chunk 27 URL from the page source
CHUNK_URL = "https://artificialanalysis.ai/_next/static/chunks/27-16ebcbc776ce8a1c.js"

def fetch_chunk(url):
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    resp = urlopen(req, timeout=30)
    data = resp.read()
    # may be gzipped
    if resp.info().get("Content-Encoding") == "gzip":
        data = gzip.decompress(data)
    return data.decode("utf-8", errors="replace")

def extract_agentic_scores(text):
    """Extract model names and their agentic index scores from chunk 27 RSC data.

    Strategy: The RSC flight payload in this chunk has:
    - Model names in array-of-arrays: ["Display Name", "base-name", "provider", ...]
    - Scores in nearby arrays that correspond to the model list
    """
    # Find all model-name-related arrays
    model_entries = []  # (display_name, base_name, provider)
    # Pattern: arrays with model names like "GPT-5.6 Luna (Non-reasoning)", "GPT-5.6 Luna", "OpenAI"
    # These appear in the RSC flight data as array elements

    # Find all string arrays that contain model-like entries
    # Look for patterns like: ["GPT-5.6 Luna (Non-reasoning)","GPT-5.6 Luna","OpenAI"]
    model_triplet_pat = re.compile(r'\["([^"]+)\s*\([^)]*\)"\s*,\s*"([^"]+)"\s*,\s*"([^"]+)"\s*\]')
    for m in model_triplet_pat.finditer(text):
        display = m.group(1).strip()
        base = m.group(2).strip()
        provider = m.group(3).strip()
        model_entries.append((display, base, provider))

    # Also find display-only pairs: ["Display Name","base-name"]
    model_pair_pat = re.compile(r'\["([^"]+)"\s*,\s*"([^"]+)"\s*\]')
    # We'll use the triplets as primary source

    # Find arrays of numeric scores that could be agentic index values
    # Look for ~100+ consecutive numbers in the 0-100 range
    score_arrays = []
    # Pattern: long arrays of numbers: [99.32,96.13,94.62,...]
    # These are usually formatted as [99.32,96.13,94.62,89.51,...] in the JS
    score_array_pat = re.compile(r'\[(?:99\.\d{2}|9[0-8]\.\d{2}|[1-9]\d?\.\d{2}|\d\.\d{2})(?:,(?:99\.\d{2}|9[0-8]\.\d{2}|[1-9]\d?\.\d{2}|\d\.\d{2})){20,}\]')
    for m in score_array_pat.finditer(text):
        scores = [float(x) for x in m.group()[1:-1].split(",")]
        if len(scores) >= 30:
            score_arrays.append(scores)

    # Deduplicate model entries
    seen = set()
    unique_models = []
    for entry in model_entries:
        key = entry[0]
        if key not in seen:
            seen.add(key)
            unique_models.append(entry)

    result = []
    if score_arrays:
        # Use the longest score array (most comprehensive)
        primary_scores = max(score_arrays, key=len)
        # Match scores to models by position
        for i, (display, base, provider) in enumerate(unique_models):
            if i < len(primary_scores):
                result.append({
                    "model": display,
                    "agentic_index": primary_scores[i],
                    "api_name": base,
                    "provider": provider,
                })
            else:
                result.append({
                    "model": display,
                    "agentic_index": None,
                    "api_name": base,
                    "provider": provider,
                })

    return result, score_arrays

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--chunk-url", default=CHUNK_URL)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--csv", action="store_true")
    parser.add_argument("--dump-scores", action="store_true", help="Dump raw score arrays found")
    args = parser.parse_args()

    print(f"Fetching {args.chunk_url} ...", file=sys.stderr)
    text = fetch_chunk(args.chunk_url)
    print(f"Fetched {len(text):,} bytes", file=sys.stderr)

    results, score_arrays = extract_agentic_scores(text)

    if args.dump_scores:
        for i, sa in enumerate(score_arrays):
            print(f"Score array #{i}: {len(sa)} values | first 10: {sa[:10]} | last 5: {sa[-5:]}")
        print(f"Total score arrays found: {len(score_arrays)}")

    if args.json:
        print(json.dumps(results, indent=2))
    elif args.csv:
        print("rank,model,agentic_index,api_name,provider")
        for i, r in enumerate(sorted(results, key=lambda x: x["agentic_index"] or 0, reverse=True), 1):
            idx = f"{r['agentic_index']:.2f}" if r["agentic_index"] is not None else "N/A"
            print(f"{i},{r['model']},{idx},{r['api_name']},{r['provider']}")
    else:
        # Print table
        sorted_results = sorted(results, key=lambda x: x["agentic_index"] or 0, reverse=True)
        print(f"\n{'Rank':>4} {'Agentic Idx':>12} {'Model':<50} {'API Name':<35} {'Provider':<20}")
        print("-" * 125)
        for i, r in enumerate(sorted_results, 1):
            idx = f"{r['agentic_index']:>8.2f}" if r["agentic_index"] is not None else "     N/A"
            print(f"{i:>4} {idx}  {r['model']:<50} {r['api_name']:<35} {r['provider']:<20}")

    if score_arrays:
        print(f"\nraw score-count: {len(score_arrays)} arrays found, largest={max(len(s) for s in score_arrays)}", file=sys.stderr)
    print(f"models extracted: {len(results)}", file=sys.stderr)

if __name__ == "__main__":
    main()