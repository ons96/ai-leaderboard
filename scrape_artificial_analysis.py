#!/usr/bin/env python3
"""Scrape Artificial Analysis leaderboard data from RSC payload.

Extracts hostsModels from Next.js RSC payload, flattens to CSV/JSON,
and computes derived columns (intelligence/speed, agentic coding score, price/perf).
"""

import csv
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

URLS = {
    "default": "https://artificialanalysis.ai/leaderboards/providers?deprecation=all",
    "medium_coding": "https://artificialanalysis.ai/leaderboards/providers/prompt-options/single/medium_coding?deprecation=all",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
    "Accept": "text/x-component, text/html, application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "identity",
}

OUTPUT_DIR = Path(__file__).parent / "data" / "artificial_analysis"


def fetch_rsc(url: str) -> str:
    """Fetch HTML with browser-like headers to bypass anti-bot."""
    req = Request(url, headers=HEADERS)
    with urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8")


def extract_rsc_pushes(html: str) -> list[str]:
    """Extract all self.__next_f.push([...]) content from RSC payload."""
    pattern = re.compile(r'self\.__next_f\.push\(\[.*?,\s*(".*?")\]\s*\)', re.DOTALL)
    pushes = []
    for m in pattern.finditer(html):
        raw = m.group(1)
        try:
            decoded = json.loads(raw)
            pushes.append(decoded)
        except json.JSONDecodeError:
            continue
    return pushes


def parse_rsc_payload(html: str) -> list[dict]:
    """Parse RSC payload to extract hostsModels array with brace-matching."""
    pushes = extract_rsc_pushes(html)
    if not pushes:
        raise ValueError("No RSC push data found in HTML")

    combined = "\n".join(pushes)

    match = re.search(r'"hostsModels"\s*:\s*\[', combined)
    if not match:
        raise ValueError("hostsModels not found in RSC payload")

    start = match.end() - 1
    depth = 0
    i = start
    in_string = False
    escape = False

    while i < len(combined):
        ch = combined[i]
        if escape:
            escape = False
        elif ch == "\\":
            escape = True
        elif ch == '"' and not escape:
            in_string = not in_string
        elif not in_string:
            if ch == "[":
                depth += 1
            elif ch == "]":
                depth -= 1
                if depth == 0:
                    break
        i += 1

    json_str = combined[start : i + 1]
    return json.loads(json_str)


def flatten_host_model(hm: dict) -> dict:
    """Flatten a host_model record into a flat dict."""
    row = {}
    model = hm.get("model") or {}
    host = hm.get("host") or {}
    e2e = hm.get("end_to_end_response_time_metrics") or {}
    ttft = hm.get("time_to_first_answer_token_metrics") or {}
    ts = hm.get("timescaleData") or {}
    perf = hm.get("performanceByPromptLength") or []

    row["id"] = hm.get("id")
    row["slug"] = hm.get("slug")
    row["deleted"] = hm.get("deleted")
    row["host_id"] = hm.get("host_id")
    row["model_id"] = hm.get("model_id")
    row["host_api_id"] = hm.get("host_api_id")
    row["host_model_string"] = hm.get("host_model_string")
    row["model_name_appendage"] = hm.get("model_name_appendage")
    row["short_name"] = hm.get("short_name")
    row["name"] = hm.get("name")
    row["model_label"] = hm.get("model_label")
    row["host_label"] = hm.get("host_label")
    row["host_name"] = host.get("name")
    row["host_slug"] = host.get("slug")
    row["host_short_name"] = host.get("short_name")
    row["host_website_url"] = host.get("website_url")
    row["host_openai_compatible"] = host.get("openai_compatible")
    row["json_mode"] = hm.get("json_mode")
    row["function_calling"] = hm.get("function_calling")

    row["price_1m_input_tokens"] = hm.get("price_1m_input_tokens")
    row["price_1m_output_tokens"] = hm.get("price_1m_output_tokens")
    row["price_1m_blended_3_to_1"] = hm.get("price_1m_blended_3_to_1")
    row["price_m_tokens_blended_3_to_1_per_dollar"] = hm.get(
        "price_m_tokens_blended_3_to_1_per_dollar"
    )
    row["price_per_1k_1mp_images"] = hm.get("price_per_1k_1mp_images")
    row["cache_write_price"] = hm.get("cache_write_price")
    row["cache_hit_discount_percent"] = hm.get("cache_hit_discount_percent")
    row["cache_storage_price_per_hour_per_1m_tokens"] = hm.get(
        "cache_storage_price_per_hour_per_1m_tokens"
    )
    row["price_per_1m_cache_write"] = hm.get("price_per_1m_cache_write")
    row["context_window_if_different_to_model"] = hm.get(
        "context_window_if_different_to_model"
    )

    row["e2e_input_time"] = e2e.get("input_time")
    row["e2e_reasoning_time"] = e2e.get("reasoning_time")
    row["e2e_answer_time"] = e2e.get("answer_time")
    row["e2e_total_time"] = e2e.get("total_time")
    row["e2e_p05_total_time"] = e2e.get("p05_total_time")
    row["e2e_p25_total_time"] = e2e.get("p25_total_time")
    row["e2e_p75_total_time"] = e2e.get("p75_total_time")
    row["e2e_p95_total_time"] = e2e.get("p95_total_time")

    row["ttft_input_time"] = ttft.get("input_time")
    row["ttft_reasoning_time"] = ttft.get("reasoning_time")
    row["ttft_total_time"] = ttft.get("total_time")

    row["median_output_speed"] = ts.get("median_output_speed")
    row["median_ttft"] = ts.get("median_time_to_first_chunk")
    row["median_est_total_100_tokens"] = ts.get(
        "median_estimated_total_seconds_for_100_output_tokens"
    )

    ts_keys = [
        ("percentile_05_output_speed", "p05_output_speed"),
        ("percentile_05_time_to_first_chunk", "p05_ttft"),
        (
            "percentile_05_estimated_total_seconds_for_100_output_tokens",
            "p05_est_total",
        ),
        ("quartile_25_output_speed", "p25_output_speed"),
        ("quartile_25_time_to_first_chunk", "p25_ttft"),
        ("quartile_25_estimated_total_seconds_for_100_output_tokens", "p25_est_total"),
        ("quartile_75_output_speed", "p75_output_speed"),
        ("quartile_75_time_to_first_chunk", "p75_ttft"),
        ("quartile_75_estimated_total_seconds_for_100_output_tokens", "p75_est_total"),
        ("percentile_95_output_speed", "p95_output_speed"),
        ("percentile_95_time_to_first_chunk", "p95_ttft"),
        (
            "percentile_95_estimated_total_seconds_for_100_output_tokens",
            "p95_est_total",
        ),
    ]
    for src_key, dst_key in ts_keys:
        row[dst_key] = ts.get(src_key)

    for p in perf:
        pt = p.get("prompt_length_type", "")
        prefix = f"perf_{pt}"
        row[f"{prefix}_median_output_speed"] = p.get("median_output_speed")
        row[f"{prefix}_median_ttft"] = p.get("median_time_to_first_chunk")
        row[f"{prefix}_median_est_total_100_tokens"] = p.get(
            "median_estimated_total_seconds_for_100_output_tokens"
        )
        row[f"{prefix}_median_e2e"] = p.get("median_end_to_end_response_time")

    row["model_name"] = model.get("name")
    row["model_short_name"] = model.get("short_name")
    row["model_slug"] = model.get("slug")
    row["model_intelligence_index"] = model.get("intelligence_index")
    row["model_estimated_intelligence_index"] = model.get(
        "estimated_intelligence_index"
    )
    row["model_agentic_index"] = model.get("agentic_index")
    row["model_coding_index"] = model.get("coding_index")
    row["model_math_index"] = model.get("math_index")
    row["model_mmlu_pro"] = model.get("mmlu_pro")
    row["model_gpqa"] = model.get("gpqa")
    row["model_aime25"] = model.get("aime25")
    row["model_livecodebench"] = model.get("livecodebench")
    row["model_hle"] = model.get("hle")
    row["model_scicode"] = model.get("scicode")
    row["model_ifbench"] = model.get("ifbench")
    row["model_tau2"] = model.get("tau2")
    row["model_terminalbench_hard"] = model.get("terminalbench_hard")
    row["model_omniscience"] = model.get("omniscience")
    row["model_gdpval"] = model.get("gdpval")
    row["model_gdpval_normalized"] = model.get("gdpval_normalized")
    row["model_lcr"] = model.get("lcr")
    row["model_parameters"] = model.get("parameters")
    row["model_context_window_tokens"] = model.get("context_window_tokens")
    row["model_output_tokens"] = model.get("output_tokens")
    row["model_reasoning_model"] = model.get("reasoning_model")
    row["model_is_open_weights"] = model.get("is_open_weights")
    row["model_license_name"] = model.get("license_name")
    row["model_release_date"] = model.get("release_date")
    row["model_size_class"] = model.get("size_class")
    row["model_creator_name"] = (model.get("model_creators") or {}).get("name")
    row["model_creator_slug"] = (model.get("model_creators") or {}).get("slug")
    row["model_input_modality_text"] = model.get("input_modality_text")
    row["model_input_modality_image"] = model.get("input_modality_image")
    row["model_input_modality_speech"] = model.get("input_modality_speech")
    row["model_input_modality_video"] = model.get("input_modality_video")
    row["model_output_modality_text"] = model.get("output_modality_text")
    row["model_output_modality_image"] = model.get("output_modality_image")
    row["model_output_modality_speech"] = model.get("output_modality_speech")
    row["model_output_modality_video"] = model.get("output_modality_video")

    return row


def compute_derived(row: dict) -> dict:
    """Compute derived columns: intelligence/speed, agentic coding score, price/perf."""
    intel = row.get("model_intelligence_index")
    est_intel = row.get("model_estimated_intelligence_index")
    intel_val = intel if intel is not None else est_intel

    def _float(v):
        try:
            return float(v) if v is not None else None
        except (ValueError, TypeError):
            return None

    gdpval_norm = _float(row.get("model_gdpval_normalized"))
    tau2 = _float(row.get("model_tau2"))
    intel_val = _float(intel_val)

    coding_speed = _float(row.get("perf_medium_coding_median_est_total_100_tokens"))
    chatbot_speed = _float(row.get("median_est_total_100_tokens"))
    blended_price = _float(row.get("price_1m_blended_3_to_1"))

    agentic_parts = []
    if gdpval_norm is not None:
        agentic_parts.append(gdpval_norm)
    if tau2 is not None:
        agentic_parts.append(tau2)
    agentic_coding_score = (
        sum(agentic_parts) / len(agentic_parts) if agentic_parts else None
    )
    row["derived_agentic_coding_score"] = agentic_coding_score

    # Speed columns (total response time in seconds)
    # For coding: use medium_coding est total time for 100 output tokens
    # For chatbot: use default/long est total time for 100 output tokens
    coding_total_time = coding_speed
    chatbot_total_time = chatbot_speed

    # Intelligence / Speed (higher = better)
    if intel_val is not None and coding_total_time and coding_total_time > 0:
        row["derived_intel_per_coding_speed"] = round(intel_val / coding_total_time, 4)
    else:
        row["derived_intel_per_coding_speed"] = None

    if intel_val is not None and chatbot_total_time and chatbot_total_time > 0:
        row["derived_intel_per_chatbot_speed"] = round(
            intel_val / chatbot_total_time, 4
        )
    else:
        row["derived_intel_per_chatbot_speed"] = None

    # Agentic coding score / Speed
    if agentic_coding_score is not None and coding_total_time and coding_total_time > 0:
        row["derived_agentic_coding_per_speed"] = round(
            agentic_coding_score / coding_total_time, 4
        )
    else:
        row["derived_agentic_coding_per_speed"] = None

    # Price / Performance (lower = better): price / intelligence
    if blended_price is not None and intel_val is not None and intel_val > 0:
        row["derived_price_per_intel"] = round(blended_price / intel_val, 6)
    else:
        row["derived_price_per_intel"] = None

    # Performance / Price (higher = better): intelligence / price
    if intel_val is not None and blended_price is not None and blended_price > 0:
        row["derived_intel_per_price"] = round(intel_val / blended_price, 4)
    else:
        row["derived_intel_per_price"] = None

    # Price / Agentic coding score
    if (
        blended_price is not None
        and agentic_coding_score is not None
        and agentic_coding_score > 0
    ):
        row["derived_price_per_agentic_coding"] = round(
            blended_price / agentic_coding_score, 6
        )
    else:
        row["derived_price_per_agentic_coding"] = None

    # Agentic coding / Price
    if (
        agentic_coding_score is not None
        and blended_price is not None
        and blended_price > 0
    ):
        row["derived_agentic_coding_per_price"] = round(
            agentic_coding_score / blended_price, 4
        )
    else:
        row["derived_agentic_coding_per_price"] = None

    return row


def scrape_and_save():
    """Main entry point: scrape, flatten, compute derived, save CSV/JSON."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Fetching {URLS['default']} ...")
    html = fetch_rsc(URLS["default"])
    print(f"  Got {len(html)} bytes")

    print("Parsing RSC payload ...")
    hosts_models = parse_rsc_payload(html)
    print(f"  Found {len(hosts_models)} host models")

    rows = []
    for hm in hosts_models:
        if hm.get("deleted"):
            continue
        row = flatten_host_model(hm)
        row = compute_derived(row)
        rows.append(row)

    print(f"  Flattened {len(rows)} active rows")

    # Save JSON (full nested data for reference)
    json_path = OUTPUT_DIR / "providers_leaderboard.json"
    with open(json_path, "w") as f:
        json.dump(hosts_models, f, indent=2)
    print(f"  Saved JSON: {json_path} ({json_path.stat().st_size / 1e6:.1f} MB)")

    # Save CSV (flattened with derived columns)
    if rows:
        csv_path = OUTPUT_DIR / "providers_leaderboard.csv"
        all_keys: set[str] = set()
        for r in rows:
            all_keys.update(r.keys())
        fieldnames = sorted(all_keys)
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(
            f"  Saved CSV: {csv_path} ({csv_path.stat().st_size / 1e6:.1f} MB, {len(fieldnames)} columns)"
        )

    # Save metadata
    meta = {
        "scrape_date": datetime.now(timezone.utc).isoformat(),
        "source_url": URLS["default"],
        "total_host_models": len(hosts_models),
        "active_host_models": len(rows),
        "columns": len(rows[0].keys()) if rows else 0,
    }
    meta_path = OUTPUT_DIR / "scrape_meta.json"
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"  Saved meta: {meta_path}")

    return rows


if __name__ == "__main__":
    scrape_and_save()
