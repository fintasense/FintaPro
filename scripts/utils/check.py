# scripts/utils/check.py

import sys
import json
from pathlib import Path


def check_value(cik: str, tag: str, date: str):
    """
    Lookup in data/raw/{cik}.json under facts → us-gaap → tag → units → USD for the given date.
    - If tag=='*', searches across ALL US-GAAP tags and prints any matches for that date.
    - If a specific tag is provided and not found, lists available tags for guidance.
    - Handles both list and dict structures under USD.
    """
    path = Path("data") / "raw" / f"{cik}.json"
    if not path.exists():
        print(f"❌ Cannot find raw JSON at {path}")
        sys.exit(1)

    data = json.loads(path.read_text())
    facts = data.get("facts", {}).get("us-gaap", {})

    # Special search across all tags
    if tag == '*':
        print(f"🔍 Searching all tags for date '{date}'...\n")
        found = False
        for t, fact in facts.items():
            usd = fact.get("units", {}).get("USD")
            if isinstance(usd, list):
                for entry in usd:
                    if entry.get('end') == date:
                        val = entry.get('val')
                        print(f"Tag: {t}  Value: {val}")
                        found = True
            elif isinstance(usd, dict):
                if date in usd:
                    print(f"Tag: {t}  Value: {usd[date]}")
                    found = True
        if not found:
            print(f"❌ No tag contains date '{date}'")
        sys.exit(0)

    # Validate specific tag
    if tag not in facts:
        print(f"❌ Tag '{tag}' not found under facts → us-gaap.")
        print("Available tags:")
        for t in sorted(facts.keys()):
            print(f"  - {t}")
        sys.exit(1)

    usd = facts[tag].get("units", {}).get("USD")
    val = None

    # If USD is a list of entries, find the matching 'end'
    if isinstance(usd, list):
        for entry in usd:
            if entry.get('end') == date:
                val = entry.get('val')
                break
    # If USD is a dict mapping dates to values
    elif isinstance(usd, dict):
        val = usd.get(date)

    if val is None:
        print(f"❌ No entry for date '{date}' under tag '{tag}'.")
        print("Check available dates for this tag:")
        dates = []
        if isinstance(usd, list):
            dates = [e.get('end') for e in usd if 'end' in e]
        elif isinstance(usd, dict):
            dates = list(usd.keys())
        for d in sorted(dates):
            print(f"  - {d}")
        sys.exit(1)

    print(f"Raw value for {tag} on {date}: {val}")
    print(f"→ In millions: {val/1e6:.2f} M")
    print(f"→ In billions: {val/1e9:.2f} B")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python scripts/utils/check.py <CIK> <US-GAAP-tag|'*'> <YYYY-MM-DD>")
        sys.exit(1)

    _, cik, tag, date = sys.argv
    check_value(cik, tag, date)
