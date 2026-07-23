#!/usr/bin/env python3
"""Scrape Artificial Analysis Agentic Index leaderboard.

Extracts model names and Agentic Index scores from the scatter-plot chart.
All 27 top models are rendered as SVG card groups + score text elements.

Usage:
    python3 scrape-aa-agentic-index.py [--output FILE] [--format text|json|csv]

Dependencies: playwright (pip install playwright), chromium browsers installed
"""
import json, re, sys, os, argparse
from playwright.sync_api import sync_playwright

URL = "https://artificialanalysis.ai/models/capabilities/agentic"


def scrape_agentic_index() -> list[dict]:
    """Return sorted list of {model, score} dicts."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})
        page.goto(URL, wait_until='networkidle', timeout=90000)
        page.wait_for_timeout(5000)

        data = page.evaluate('''
        () => {
            const items = [];
            const walker = document.createTreeWalker(
                document.body, NodeFilter.SHOW_TEXT, null, false
            );
            let node;
            while (node = walker.nextNode()) {
                const text = node.textContent.trim();
                if (!text) continue;
                const parent = node.parentElement;
                const rect = parent.getBoundingClientRect();
                if (rect.top > 700 && rect.top < 1300 && rect.width > 0 && rect.height > 0) {
                    items.push({
                        text: text,
                        x: Math.round(rect.left + rect.width / 2),
                        y: Math.round(rect.top + rect.height / 2),
                    });
                }
            }
            return items;
        }
        ''')

        # Filter model names (anchor text containing known LLM patterns)
        MODEL_PATTERN = re.compile(
            r'GPT-|Claude|Kimi|K3|Grok|GLM|Gemini|Muse|DeepSeek|MiniMax'
            r'|Inkling|Qwen|MiMo|Nemotron|Mistral|Haiku|Gemma|gpt-oss'
            r'|Command|K2'
        )
        models = []
        for item in data:
            if MODEL_PATTERN.search(item['text']):
                models.append(item)

        # Filter scores (1-2 digit numbers with len ≤ 3)
        scores = []
        for item in data:
            t = item['text']
            if re.match(r'^\d{1,2}$', t):
                scores.append(item)

        # Pair: match model -> score by x-position proximity (same card column)
        # Both lists are naturally sorted left-to-right by x
        models_sorted = sorted(models, key=lambda m: m['x'])
        scores_sorted = sorted(scores, key=lambda s: s['x'])

        if len(models_sorted) != len(scores_sorted):
            return {'error': f'count mismatch: {len(models_sorted)} models vs {len(scores_sorted)} scores',
                    'models': [m['text'] for m in models_sorted],
                    'scores': [s['text'] for s in scores_sorted]}

        pairs = []
        for m, s in zip(models_sorted, scores_sorted):
            pairs.append({
                'model': m['text'],
                'score': int(s['text']),
                'x': m['x'],
            })
        return pairs


def main():
    parser = argparse.ArgumentParser(description='Scrape AA Agentic Index')
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--format', '-f', choices=['text', 'json', 'csv'], default='text')
    args = parser.parse_args()

    entries = scrape_agentic_index()

    if isinstance(entries, dict) and 'error' in entries:
        print(f'ERROR: {entries["error"]}', file=sys.stderr)
        print('Models:', entries.get('models', []), file=sys.stderr)
        print('Scores:', entries.get('scores', []), file=sys.stderr)
        sys.exit(1)

    # Sort by score descending, then name
    entries.sort(key=lambda e: (-e['score'], e['model']))

    print(f'Found {len(entries)} model entries', file=sys.stderr)

    if args.format == 'json':
        output = json.dumps(entries, indent=2)
    elif args.format == 'csv':
        lines = ['model,score']
        for e in entries:
            lines.append(f'{e["model"]},{e["score"]}')
        output = '\n'.join(lines) + '\n'
    else:
        max_name = max(len(e['model']) for e in entries)
        lines = [f'{"#":>3} {"Model":<{max_name}}  Score']
        lines.append('-' * (4 + max_name + 7))
        for i, e in enumerate(entries):
            lines.append(f'{i+1:>3} {e["model"]:<{max_name}}  {e["score"]:>3}')
        output = '\n'.join(lines) + '\n'

    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f'Written to {args.output}', file=sys.stderr)
    else:
        print(output)


if __name__ == '__main__':
    main()