# scripts/extract/parse_sec_json.py

import json
from pathlib import Path
from typing import Dict
import pandas as pd


def load_sec_json(filepath: str) -> Dict:
    """
    Load the raw SEC JSON file for a given CIK.
    """
    with open(filepath, 'r') as f:
        return json.load(f)


def extract_usd_facts(sec_data: Dict) -> pd.DataFrame:
    """
    Flatten the SEC JSON facts into a DataFrame of USD values per period.

    Returns columns:
      - tag: raw US-GAAP tag (unqualified)
      - label: human-readable label
      - value: numeric value
      - fy: fiscal year
      - fp: fiscal period (e.g., 'Q1')
      - form: filing form (10-Q or 10-K)
      - filed: filing date
      - end: period-end date
    """
    rows = []
    facts = sec_data.get("facts", {}).get("us-gaap", {})

    for tag_full, metrics in facts.items():
        # unqualify tag name (strip namespace)
        tag = tag_full.split(':', 1)[-1]
        label = metrics.get('label', tag)
        unit_data = metrics.get('units', {}).get('USD', {})

        # USD facts may be list of entries or dict mapping dates -> values
        if isinstance(unit_data, list):
            for entry in unit_data:
                val = entry.get('val')
                end = entry.get('end')
                fy = entry.get('fy')
                fp = entry.get('fp')
                form = entry.get('form')
                filed = entry.get('filed')
                rows.append({
                    'tag': tag,
                    'label': label,
                    'value': val,
                    'fy': fy,
                    'fp': fp,
                    'form': form,
                    'filed': filed,
                    'end': end
                })
        elif isinstance(unit_data, dict):
            # dict mapping end-date -> value, but lacks metadata
            for end, val in unit_data.items():
                rows.append({
                    'tag': tag,
                    'label': label,
                    'value': val,
                    'fy': sec_data.get('cik'),  # fallback if missing
                    'fp': None,
                    'form': None,
                    'filed': None,
                    'end': end
                })

    # Construct DataFrame
    df = pd.DataFrame(rows)
    return df
