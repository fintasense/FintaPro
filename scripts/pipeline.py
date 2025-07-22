# scripts/pipeline.py

"""
MetaSense Financial Pro ETL Pipeline

This script orchestrates the full end-to-end flow:

1. Extraction:   scripts/extract/parse_sec_json.py
2. Cleaning:     scripts/clean/preprocess_terms.py
3. Matching:     scripts/model/tag_match_engine.py
4. Saving:       scripts/store/save_results.py
"""

# scripts/pipeline.py

import sys
from pathlib import Path

# 1) Ensure project root is on sys.path so `scripts.*` imports resolve
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# 2) Now you can safely import anything from scripts/
from scripts.store.log_qc_results import report_missing

import argparse

from config.settings import RAW_DIR, INTERMEDIATE_DIR, PROCESSED_DIR, MAPPING_PATH
from scripts.extract.parse_sec_json import load_sec_json, extract_usd_facts
from scripts.clean.preprocess_terms import clean_dataframe
from scripts.model.tag_match_engine import TagMatchEngine
from scripts.store.save_results_estimated import save_results_estimated as save_results


def run_pipeline(cik: str) -> None:
    """
    Execute the full ETL pipeline for a given company CIK code.

    Steps:
    1. Extract JSON → DataFrame
    2. Save intermediate CSV
    3. Clean text fields
    4. Match to standard terms
    5. Save final Excel results
    """
    # Build paths from config
    raw_file = RAW_DIR / f"{cik}.json"
    INTERMEDIATE_DIR.mkdir(parents=True, exist_ok=True)
    intermediate_csv = INTERMEDIATE_DIR / f"{cik}_flat.csv"
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    output_path = PROCESSED_DIR / f"{cik}_results.xlsx"

    # Step 1: Extract
    print(f"[{cik}] Extracting facts from JSON...")
    sec_data = load_sec_json(str(raw_file))
    df_extracted = extract_usd_facts(sec_data)
    df_extracted.to_csv(intermediate_csv, index=False)
    print("[DEBUG] After extract_usd_facts:")
    print("  columns:", df_extracted.columns.tolist())
    print("[DEBUG] Sample `end` values from extractor:")
    print(df_extracted['end'].dropna().unique()[:10])

    # Step 2: Clean
    print(f"[{cik}] Cleaning extracted data...")
    df_clean = clean_dataframe(df_extracted)
    


    # Step 3: Match
    print(f"[{cik}] Matching tags to standard terms...")
    engine = TagMatchEngine(str(MAPPING_PATH))
    df_matched = engine.match_all(df_clean)
    report_missing(df_matched, str(MAPPING_PATH), cik)


    
    # Step 4: Save
    print(f"[{cik}] Saving results to Excel...")
    save_results(df_matched, str(MAPPING_PATH), str(output_path))
    print(f"[{cik}] Pipeline complete. Results at {output_path}")
    



def main() -> None:
    parser = argparse.ArgumentParser(description="Run ETL pipeline for a given CIK code.")
    parser.add_argument(
        "--cik",
        required=True,
        help="CIK code without .json extension"
    )
    args = parser.parse_args()

    run_pipeline(args.cik)


if __name__ == "__main__":
    main()
