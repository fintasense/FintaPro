# scripts/clean/preprocess_terms.py

import pandas as pd
import re


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the DataFrame by generating normalized 'tag_clean' and 'label_clean' columns,
    while preserving all original columns (including 'end', 'fy', 'fp', 'form', 'filed', 'value').

    - tag_clean: lowercase alphanumeric only version of 'tag'
    - label_clean: lowercase alphanumeric only version of 'label'

    Returns a cleaned DataFrame.
    """
    df_clean = df.copy()

    # Normalize 'tag'
    df_clean['tag_clean'] = (
        df_clean['tag']
        .astype(str)
        .str.replace(r"[^A-Za-z0-9]", " ", regex=True)
        .str.lower()
        .str.strip()
    )

    # Normalize 'label'
    df_clean['label_clean'] = (
        df_clean['label']
        .astype(str)
        .str.replace(r"[^A-Za-z0-9]", " ", regex=True)
        .str.lower()
        .str.strip()
    )

    # Ensure 'end' column is present
    if 'end' not in df_clean.columns and 'period_end' in df_clean.columns:
        df_clean['end'] = df_clean['period_end']

    return df_clean
