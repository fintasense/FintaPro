# scripts/store/log_qc_results.py

import json
import pandas as pd
from pathlib import Path

from config.settings import MAPPING_PATH, PROCESSED_DIR


def report_missing(df_all: pd.DataFrame, mapping_path: str, cik: str) -> None:
    """
    Generate a QC report of missing periods per standard term.

    - df_all: DataFrame returned by TagMatchEngine.match_all(), must include:
        ['standard_term', 'value', 'filed']
    - mapping_path: path to the JSON mapping file
    - cik: the company identifier used for naming the report file

    This writes `data/processed/{cik}_qc_report.csv` listing:
      standard_term, section, total_periods, matched_periods, missing_periods
    """
    # Load mapping to know each term's section
    mapping_file = Path(mapping_path)
    with mapping_file.open('r') as f:
        mapping_data = json.load(f)

    term_to_section = {}
    for section, terms in mapping_data.items():
        for term in terms.keys():
            term_to_section[term] = section

    # Ensure 'filed_date' column exists, derived from 'filed'
    if 'filed_date' not in df_all.columns:
        df_all['filed_date'] = pd.to_datetime(
            df_all['filed'], errors='coerce'
        ).dt.strftime('%b %d %Y')

    records = []
    for term, section in term_to_section.items():
        df_term = df_all[df_all['standard_term'] == term]
        # All unique filing dates
        unique_dates = df_term['filed_date'].dropna().unique()
        # Sort dates descending
        all_periods = sorted(
            unique_dates,
            key=lambda x: pd.to_datetime(x, format='%b %d %Y'),
            reverse=True
        )
        # Periods where value != 0
        matched = df_term[df_term['value'] != 0]['filed_date'].dropna().unique()
        matched_periods = sorted(
            matched,
            key=lambda x: pd.to_datetime(x, format='%b %d %Y'),
            reverse=True
        )
        # Missing periods
        missing = [d for d in all_periods if d not in matched_periods]

        records.append({
            'standard_term': term,
            'section': section,
            'total_periods': len(all_periods),
            'matched_periods': len(matched_periods),
            'missing_periods': ";".join(missing)
        })
    df_report = pd.DataFrame(records)
        # Create a separate QC reports directory
    qc_dir = Path(PROCESSED_DIR).parent / "qc_reports"
    qc_dir.mkdir(parents=True, exist_ok=True)
    report_path = qc_dir / f"{cik}_qc_report.csv"
    df_report.to_csv(report_path, index=False)
    print(f"QC report written to {report_path}")
