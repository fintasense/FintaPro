# scripts/utils/extend_mapping.py

import sys
from pathlib import Path
# Ensure project root is on sys.path so we can import our modules
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import json
from rapidfuzz import fuzz
import pandas as pd

from scripts.extract.parse_sec_json import load_sec_json, extract_usd_facts
from scripts.clean.preprocess_terms import clean_dataframe
from scripts.model.sbert_embedder import SBERTEmbedder
from config.settings import MAPPING_PATH

def auto_extend_mapping(cik: str,
                        mapping_path: str = None,
                        fuzzy_thresh: int = 80,
                        semantic_thresh: float = 0.75) -> None:
    """
    Automatically discover and append new US GAAP tag variants to your mapping JSON
    using fuzzy and semantic matching. Generates a report of additions with scores.

    - cik: Company identifier (uses data/raw/{cik}.json)
    - mapping_path: Path to standard_to_usgaap_mapping.json (defaults to config)
    - fuzzy_thresh: threshold for fuzzy tag matching (0-100)
    - semantic_thresh: SBERT cosine threshold for semantic label matching (0-1)
    """
    # Determine mapping file
    mapping_file = Path(mapping_path or MAPPING_PATH)
    if not mapping_file.exists():
        raise FileNotFoundError(f"Mapping JSON not found: {mapping_file}")
    mapping_data = json.loads(mapping_file.read_text())

    # Load and clean company data
    raw_path = Path("data") / "raw" / f"{cik}.json"
    if not raw_path.exists():
        raise FileNotFoundError(f"Raw JSON not found: {raw_path}")
    sec_data = load_sec_json(str(raw_path))
    df_extracted = extract_usd_facts(sec_data)
    df = clean_dataframe(df_extracted)

    # Unique tags and labels
    unique_tags = df[["tag", "tag_clean", "label_clean"]].drop_duplicates()

    # Build standard term → section map
    std_to_section = {}
    for section, terms in mapping_data.items():
        for std in terms:
            std_to_section[std] = section
    std_terms = list(std_to_section.keys())

    # Prepare SBERT for semantic matching
    sbert = SBERTEmbedder(model_dir=None)
    std_embeds = sbert.encode_terms(std_terms)

    additions = []

    # Iterate through each unique raw tag
    for _, row in unique_tags.iterrows():
        raw_tag     = row["tag"]
        tag_clean   = row["tag_clean"]
        label_clean = row["label_clean"]

        # Skip tags already in mapping
        if any(raw_tag in tags for tags in mapping_data.values()):
            continue

        # 1) Fuzzy-tag matching
        best_score = 0
        best_std   = None
        for std in std_terms:
            score = fuzz.ratio(tag_clean, std.lower())
            if score > best_score:
                best_score, best_std = score, std

        if best_score >= fuzzy_thresh:
            sect = std_to_section[best_std]
            mapping_data[sect][best_std].append(raw_tag)
            additions.append({
                "standard_term": best_std,
                "raw_tag":       raw_tag,
                "method":        "fuzzy_tag",
                "fuzzy_score":   best_score,
                "semantic_score": None
            })
            continue

        # 2) Semantic fallback on label_clean
        if label_clean:
            std_match, sem_score = sbert.semantic_match(label_clean, std_embeds, std_terms)
            if sem_score >= semantic_thresh:
                sect = std_to_section[std_match]
                mapping_data[sect][std_match].append(raw_tag)
                additions.append({
                    "standard_term":  std_match,
                    "raw_tag":        raw_tag,
                    "method":         "semantic",
                    "fuzzy_score":    None,
                    "semantic_score": sem_score
                })

    # Save the updated mapping JSON
    mapping_file.write_text(json.dumps(mapping_data, indent=4))
    print(f"Mapping extended and saved to {mapping_file}")

    # Write a CSV report of all additions
    report_dir = Path("data") / "qc_reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"{cik}_mapping_extensions.csv"
    pd.DataFrame(additions).to_csv(report_path, index=False)
    print(f"Extension report written to {report_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/utils/extend_mapping.py <CIK> [fuzzy_thresh] [semantic_thresh]")
        sys.exit(1)

    cik = sys.argv[1]
    fuzzy = int(sys.argv[2]) if len(sys.argv) > 2 else 80
    sem   = float(sys.argv[3]) if len(sys.argv) > 3 else 0.75
    auto_extend_mapping(cik, None, fuzzy_thresh=fuzzy, semantic_thresh=sem)
