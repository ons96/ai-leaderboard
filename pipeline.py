#!/usr/bin/env python3
"""Full pipeline: scrape data then build static site."""
import subprocess, sys
from pathlib import Path

scripts = Path(__file__).parent

print("=== Step 1: Scraping ===")
r = subprocess.run([sys.executable, scripts / "scrape_artificial_analysis.py"], check=False)
if r.returncode != 0:
    print(f"Scraper failed with code {r.returncode}")
    sys.exit(1)

print("=== Step 2: Building site ===")
r = subprocess.run([sys.executable, scripts / "build_site.py"], check=False)
if r.returncode != 0:
    print(f"Site builder failed with code {r.returncode}")
    sys.exit(1)

print("=== Done ===")

