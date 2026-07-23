#!/usr/bin/env python3
"""Scrape Artificial Analysis coding agents benchmark data using Playwright.

Extracts all model-harness combo entries (Coding Agent Index, time per task,
cost per task, DeepSWE/Terminal-Bench v2/SWE-Atlas-QnA scores) from the
React Server Components (RSC) Flight payload embedded in the page HTML.

Usage:
    python3 scrape-aa-coding-agents.py [--output FILE] [--format text|json]

Dependencies: playwright (pip install playwright), chromium browsers installed
"""
import json, re, sys, os, argparse
from playwright.sync_api import sync_playwright

URL = "https://artificialanalysis.ai/agents/coding-agents"


def parse_benchmark_rows(decoded: str) -> list:
    """Extract benchmark row objects from RSC Flight-encoded JSON."""
    marker = '"benchmarkRows"'
    m_start = decoded.find(marker)
    if m_start < 0:
        return []
    arr_start = decoded.find('[', m_start)
    depth, arr_end = 1, arr_start + 1
    while depth > 0 and arr_end < len(decoded):
        if decoded[arr_end] == '[':
            depth += 1
        elif decoded[arr_end] == ']':
            depth -= 1
        arr_end += 1

    arr_content = decoded[arr_start:arr_end]
    clean = re.sub(r'\$L\d+', '""', arr_content)
    clean = re.sub(r'\$\$', '$', clean)

    rows = []
    idx = 0
    while True:
        obj_start = clean.find('{', idx)
        if obj_start < 0:
            break
        depth, obj_end = 1, obj_start + 1
        while depth > 0 and obj_end < len(clean):
            if clean[obj_end] == '{':
                depth += 1
            elif clean[obj_end] == '}':
                depth -= 1
            obj_end += 1
        try:
            obj = json.loads(clean[obj_start:obj_end])
            if 'hostModelSlug' in obj and 'agentName' in obj:
                rows.append(obj)
        except json.JSONDecodeError:
            pass
        idx = obj_end
    return rows


def extract_rsc_pushes(html: str) -> list:
    """Extract all __next_f.push payloads from HTML."""
    return re.findall(r'self\.__next_f\.push\(\[1,"([\s\S]*?)"\]\)', html)


def find_highlights(decoded: str) -> list:
    """Find highlight section entries by label+score pattern."""
    entries = []
    searches = [
        ('Claude Code - Fable 5', 'anthropic_claude-fable-5', 'Claude Code'),
        ('Grok Build - Grok 4.5', 'xai_grok-4-5', 'Grok Build'),
        ('Kimi Code CLI - Kimi K3', 'moonshot_kimi-k3', 'Kimi Code CLI'),
        ('Opencode - Muse Spark', 'meta_super-nova', 'Opencode'),
        ('Claude Code - GLM-5.2', 'novita_glm-5-2_fp8', 'Claude Code'),
        ('Cursor CLI - Composer 2.5 Fast', 'cursor_composer-2-5-fast', 'Cursor CLI'),
        ('Claude Code - DeepSeek V4', 'deepseek_deepseek-v4-pro-1m', 'Claude Code'),
        ('Gemini CLI - Gemini 3.1', 'google_gemini-3-1-pro_ai-studio', 'Gemini CLI'),
        ('Claude Code - Opus 4.8 (max)', 'anthropic_claude-opus-4-8', 'Claude Code'),
        ('Codex - GPT-5.6 Sol (max)', 'openai_kindle-alpha-api', 'Codex'),
    ]
    for label, slug, agent in searches:
        idx_pos = decoded.find(label)
        if idx_pos < 0:
            continue
        ctx = decoded[idx_pos:idx_pos + 1500]
        score_m = re.search(r'"indexScore":([\d.]+)', ctx)
        time_m = re.search(r'"agentWallTimeSec":([\d.]+)', ctx)
        cost_m = re.search(r'"costUsd":([\d.]+)', ctx)
        entries.append({
            'displayLabel': label,
            'agentName': agent,
            'hostModelSlug': slug,
            'indexScore': float(score_m.group(1)) if score_m else 0,
            'agentWallTimeSec': float(time_m.group(1)) if time_m else 0,
            'costUsd': float(cost_m.group(1)) if cost_m else 0,
        })
    return entries


def normalize_entry(r: dict) -> dict:
    """Convert a raw benchmark row to normalized format."""
    evals = {}
    for e in r.get('evals', []):
        if e.get('mean'):
            evals[e['datasetIndexName']] = e['mean']['reward']
    mean = r.get('mean', {})
    return {
        'displayLabel': r.get('displayLabel', '?'),
        'agentName': r.get('agentName', '?'),
        'hostModelSlug': r.get('hostModelSlug', '?'),
        'indexScore': r.get('indexScore', 0) or 0,
        'agentWallTimeSec': mean.get('agentWallTimeSec', 0) or 0,
        'costUsd': mean.get('costUsd', 0) or 0,
        'totalTokens': mean.get('totalTokens', 0) or 0,
        'inputTokens': mean.get('inputTokens', 0) or 0,
        'outputTokens': mean.get('outputTokens', 0) or 0,
        'cacheTokens': mean.get('cacheTokens', 0) or 0,
        'steps': mean.get('steps', 0) or 0,
        'deepSWE': evals.get('deep-swe', 0),
        'terminalBench': evals.get('terminal-bench-v2', 0),
        'sweAtlasQnA': evals.get('swe-atlas-qna', 0),
    }


def scrape() -> list:
    """Main scrape: return list of normalized entries."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})
        print(f"Fetching {URL}...", file=sys.stderr)
        page.goto(URL, wait_until='networkidle', timeout=90000)
        page.wait_for_timeout(5000)
        html = page.content()

        # Collect all RSC pushes
        all_rsc = ''
        scripts = page.query_selector_all('script')
        for s in scripts:
            content = s.inner_text()
            if 'self.__next_f.push' not in content:
                continue
            for push in extract_rsc_pushes(content):
                decoded = push.replace('\\"', '"').replace('\\n', '\n')
                all_rsc += decoded

        # Parse table rows
        table_entries = [normalize_entry(r) for r in parse_benchmark_rows(all_rsc)]

        # Parse highlights not already in table
        existing_labels = {e['displayLabel'] for e in table_entries}
        for hl in find_highlights(all_rsc):
            if hl['displayLabel'] not in existing_labels:
                table_entries.append(hl)

        browser.close()
        return table_entries


def print_text_table(entries: list):
    """Print a formatted text table."""
    entries_sorted = sorted(entries, key=lambda x: -x['indexScore'])
    print(f"{'#':>3} {'Display Name':<55} {'Idx':>5} {'Time(m)':>7} {'Cost($)':>7} {'DeepSWE':>7} {'TermB':>7} {'SWE-QA':>7}")
    print('-' * 105)
    for i, e in enumerate(entries_sorted):
        idx = e['indexScore'] * 100
        tm = e['agentWallTimeSec'] / 60 if e['agentWallTimeSec'] else 0
        ds = e['deepSWE'] * 100 if e['deepSWE'] else 0
        tb = e['terminalBench'] * 100 if e['terminalBench'] else 0
        sa = e['sweAtlasQnA'] * 100 if e['sweAtlasQnA'] else 0
        print(f"{i+1:>3} {e['displayLabel']:<55} {idx:>4.0f}  {tm:>5.1f}m ${e['costUsd']:>5.2f} {ds:>5.0f}% {tb:>5.0f}% {sa:>5.0f}%")

    # Efficiency tables
    has_time = [e for e in entries if e['agentWallTimeSec'] > 0 and e['indexScore'] > 0]
    print(f"\n\n=== Speed+Intelligence Efficiency (Idx²/Time_hours) ===")
    has_time.sort(key=lambda x: -(x['indexScore'] ** 2 / (x['agentWallTimeSec'] / 3600)))
    print(f"{'#':>3} {'Display Name':<55} {'Idx':>5} {'Time(m)':>7} {'Idx²/h':>8} {'Cost($)':>7}")
    print('-' * 90)
    for i, e in enumerate(has_time[:20]):
        idx = e['indexScore'] * 100
        tm = e['agentWallTimeSec'] / 60
        time_h = e['agentWallTimeSec'] / 3600
        e_score = e['indexScore'] ** 2 / time_h * 100
        print(f"{i+1:>3} {e['displayLabel']:<55} {idx:>4.0f}  {tm:>5.1f}m {e_score:>6.0f}  ${e['costUsd']:>5.2f}")


def main():
    parser = argparse.ArgumentParser(description='Scrape AA coding agents benchmark')
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--format', '-f', choices=['text', 'json'], default='text')
    args = parser.parse_args()

    entries = scrape()
    print(f"Found {len(entries)} entries", file=sys.stderr)

    if args.format == 'json':
        output = json.dumps(entries, indent=2)
    else:
        # Capture text table as string
        import io
        buf = io.StringIO()
        old_out = sys.stdout
        sys.stdout = buf
        print_text_table(entries)
        sys.stdout = old_out
        output = buf.getvalue()

    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == '__main__':
    main()