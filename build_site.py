#!/usr/bin/env python3
"""Build static GitHub Pages site from scraped Artificial Analysis data."""

import csv
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data" / "artificial_analysis"
SITE_DIR = Path(__file__).parent / "docs"

DISPLAY_COLUMNS = [
    "host_name", "model_name", "model_name_appendage", "model_creator_name",
    "price_1m_input_tokens", "price_1m_output_tokens", "price_1m_blended_3_to_1",
    "price_m_tokens_blended_3_to_1_per_dollar",
    "derived_agentic_coding_score",
    "derived_intel_per_coding_speed", "derived_intel_per_chatbot_speed",
    "derived_agentic_coding_per_speed",
    "derived_price_per_intel", "derived_intel_per_price",
    "derived_price_per_agentic_coding", "derived_agentic_coding_per_price",
    "model_intelligence_index", "model_estimated_intelligence_index",
    "model_agentic_index", "model_coding_index", "model_math_index",
    "model_mmlu_pro", "model_gpqa", "model_aime25",
    "model_livecodebench", "model_hle", "model_scicode",
    "model_ifbench", "model_tau2", "model_terminalbench_hard",
    "model_omniscience", "model_gdpval", "model_gdpval_normalized",
    "median_output_speed", "median_ttft", "median_est_total_100_tokens",
    "e2e_total_time",
    "perf_medium_coding_median_output_speed", "perf_medium_coding_median_ttft",
    "perf_medium_coding_median_est_total_100_tokens", "perf_medium_coding_median_e2e",
    "model_parameters", "model_context_window_tokens", "model_output_tokens",
    "model_reasoning_model", "model_is_open_weights", "model_license_name",
    "model_release_date", "model_size_class", "model_lcr",
]

COLUMN_LABELS = {
    "host_name": "Provider", "model_name": "Model",
    "model_name_appendage": "Variant", "model_creator_name": "Creator",
    "price_1m_input_tokens": "Input $/1M", "price_1m_output_tokens": "Output $/1M",
    "price_1m_blended_3_to_1": "Blended $/1M (3:1)",
    "price_m_tokens_blended_3_to_1_per_dollar": "M tok/$",
    "derived_agentic_coding_score": "Agentic Coding",
    "derived_intel_per_coding_speed": "Intel/CodingSpd",
    "derived_intel_per_chatbot_speed": "Intel/ChatSpd",
    "derived_agentic_coding_per_speed": "Agentic/Spd",
    "derived_price_per_intel": "$/Intel", "derived_intel_per_price": "Intel/$",
    "derived_price_per_agentic_coding": "$/Agentic", "derived_agentic_coding_per_price": "Agentic/$",
    "model_intelligence_index": "Intelligence",
    "model_estimated_intelligence_index": "Est.Intel",
    "model_agentic_index": "Agentic Idx", "model_coding_index": "Coding Idx",
    "model_math_index": "Math Idx", "model_mmlu_pro": "MMLU-Pro",
    "model_gpqa": "GPQA", "model_aime25": "AIME25",
    "model_livecodebench": "LiveCodeBench", "model_hle": "HLE",
    "model_scicode": "SciCode", "model_ifbench": "IFEval",
    "model_tau2": "tau2", "model_terminalbench_hard": "TermBench",
    "model_omniscience": "Omniscience",
    "model_gdpval": "GDPval", "model_gdpval_normalized": "GDPval-AA",
    "median_output_speed": "Speed(tok/s)", "median_ttft": "TTFT(s)",
    "median_est_total_100_tokens": "Est100tok(s)", "e2e_total_time": "E2E(s)",
    "perf_medium_coding_median_output_speed": "CodeSpd",
    "perf_medium_coding_median_ttft": "CodeTTFT",
    "perf_medium_coding_median_est_total_100_tokens": "Code100tok",
    "perf_medium_coding_median_e2e": "CodeE2E",
    "model_parameters": "Params(B)", "model_context_window_tokens": "Context",
    "model_output_tokens": "MaxOut", "model_reasoning_model": "Reason",
    "model_is_open_weights": "OpenWt", "model_license_name": "License",
    "model_release_date": "Released", "model_size_class": "Size", "model_lcr": "LCR",
}

HIGHLIGHT_COLS = {
    "derived_agentic_coding_score": "higher",
    "derived_intel_per_coding_speed": "higher",
    "derived_intel_per_chatbot_speed": "higher",
    "derived_agentic_coding_per_speed": "higher",
    "derived_price_per_intel": "lower", "derived_intel_per_price": "higher",
    "derived_price_per_agentic_coding": "lower", "derived_agentic_coding_per_price": "higher",
    "model_intelligence_index": "higher", "model_gdpval_normalized": "higher",
    "model_tau2": "higher", "median_output_speed": "higher",
    "price_1m_blended_3_to_1": "lower",
}

COL_GROUPS = {
    "identity": ["host_name", "model_name", "model_name_appendage", "model_creator_name"],
    "pricing": ["price_1m_input_tokens", "price_1m_output_tokens", "price_1m_blended_3_to_1", "price_m_tokens_blended_3_to_1_per_dollar"],
    "derived": ["derived_agentic_coding_score", "derived_intel_per_coding_speed", "derived_intel_per_chatbot_speed", "derived_agentic_coding_per_speed", "derived_price_per_intel", "derived_intel_per_price", "derived_price_per_agentic_coding", "derived_agentic_coding_per_price"],
    "quality": ["model_intelligence_index", "model_estimated_intelligence_index", "model_agentic_index", "model_coding_index", "model_math_index", "model_mmlu_pro", "model_gpqa", "model_aime25", "model_livecodebench", "model_hle", "model_scicode", "model_ifbench", "model_tau2", "model_terminalbench_hard", "model_omniscience", "model_gdpval", "model_gdpval_normalized"],
    "speed": ["median_output_speed", "median_ttft", "median_est_total_100_tokens", "e2e_total_time"],
    "coding_speed": ["perf_medium_coding_median_output_speed", "perf_medium_coding_median_ttft", "perf_medium_coding_median_est_total_100_tokens", "perf_medium_coding_median_e2e"],
    "model_meta": ["model_parameters", "model_context_window_tokens", "model_output_tokens", "model_reasoning_model", "model_is_open_weights", "model_license_name", "model_release_date", "model_size_class", "model_lcr"],
}

GROUP_ORDER = ["identity", "pricing", "derived", "quality", "speed", "coding_speed", "model_meta"]
GROUP_LABELS = {"identity": "Identity", "pricing": "Pricing", "derived": "Derived",
    "quality": "Quality", "speed": "Speed", "coding_speed": "Coding Speed", "model_meta": "Meta"}


def build_site():
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    with open(DATA_DIR / "providers_leaderboard.csv") as f:
        rows = list(csv.DictReader(f))
    with open(DATA_DIR / "scrape_meta.json") as f:
        meta = json.load(f)
    cols = [c for c in DISPLAY_COLUMNS if c in (rows[0].keys() if rows else [])]
    table_data = []
    for row in rows:
        item = {}
        for col in cols:
            val = row.get(col, "")
            if val == "":
                item[col] = None
            elif val.lower() == "true":
                item[col] = True
            elif val.lower() == "false":
                item[col] = False
            else:
                try:
                    item[col] = float(val) if "." in val else int(val)
                except ValueError:
                    item[col] = val
        table_data.append(item)
    lines = [
        "const TABLE_DATA=" + json.dumps(table_data) + ";",
        "const COLUMNS=" + json.dumps(cols) + ";",
        "const LABELS=" + json.dumps(COLUMN_LABELS) + ";",
        "const HIGHLIGHTS=" + json.dumps(HIGHLIGHT_COLS) + ";",
        "const META=" + json.dumps(meta) + ";",
        "const COL_GROUPS=" + json.dumps(COL_GROUPS) + ";",
        "const GROUP_ORDER=" + json.dumps(GROUP_ORDER) + ";",
        "const GROUP_LABELS=" + json.dumps(GROUP_LABELS) + ";",
    ]
    data_js = "\n".join(lines) + "\n"
    with open(SITE_DIR / "data.js", "w") as f:
        f.write(data_js)
    print(f"data.js: {len(data_js)/1e3:.0f} KB")
    html = (Path(__file__).parent / "site_template.html").read_text()
    with open(SITE_DIR / "index.html", "w") as f:
        f.write(html)
    print("index.html written")


if __name__ == "__main__":
    build_site()
