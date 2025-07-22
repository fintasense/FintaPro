# scripts/model/tag_match_engine.py

import json
from pathlib import Path
import pandas as pd
from rapidfuzz import fuzz

class TagMatchEngine:
    """
    Engine to match cleaned financial data to standard terms
    using direct and fuzzy matching strategies, and to preserve all
    time series entries for reporting periods.
    """

    def __init__(self, mapping_path: str):
        mapping_file = Path(mapping_path)
        if not mapping_file.exists():
            raise FileNotFoundError(f"Mapping file not found: {mapping_path}")

        with mapping_file.open('r') as f:
            mapping_data = json.load(f)

        # Flatten the JSON structure into one dict:
        # standard_term -> list of US GAAP tags
        self.mapping = {}
        for section in mapping_data.values():
            for std_term, tags in section.items():
                self.mapping[std_term] = tags

    def match(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Match cleaned DataFrame rows to each standard term.
        Returns a DataFrame with one row per standard term: the best match.
        """
        results = []

        for std_term, tags in self.mapping.items():
            # 1) Direct tag match
            df_direct = df[df['tag'].isin(tags)]
            if not df_direct.empty:
                df_annual = df_direct[df_direct['form'] == '10-K']
                row = df_annual.sort_values('filed', ascending=False).iloc[0] if not df_annual.empty else df_direct.sort_values('filed', ascending=False).iloc[0]
                results.append({
                    'standard_term': std_term,
                    'value': row['value'],
                    'matched_tag': row['tag'],
                    'matched_label': row['label'],
                    'match_method': 'direct',
                    'confidence': 1.0,
                    'fy': row.get('fy'),
                    'fp': row.get('fp'),
                    'form': row.get('form'),
                    'filed': row.get('filed')
                })
                continue

            # 2) Fuzzy match on 'tag_clean'
            best_score = 0
            best_row = None
            for _, row in df.iterrows():
                for tag in tags:
                    score = fuzz.ratio(row.get('tag_clean', ''), tag.replace(':', ' '))
                    if score > best_score:
                        best_score = score
                        best_row = row

            if best_score >= 80 and best_row is not None:
                results.append({
                    'standard_term': std_term,
                    'value': best_row['value'],
                    'matched_tag': best_row['tag'],
                    'matched_label': best_row['label'],
                    'match_method': 'fuzzy_tag',
                    'confidence': best_score / 100,
                    'fy': best_row.get('fy'),
                    'fp': best_row.get('fp'),
                    'form': best_row.get('form'),
                    'filed': best_row.get('filed')
                })
                continue

            # 3) Fuzzy match on 'label_clean'
            best_score = 0
            best_row = None
            for _, row in df.iterrows():
                score = fuzz.ratio(row.get('label_clean', ''), std_term.lower())
                if score > best_score:
                    best_score = score
                    best_row = row

            if best_score >= 80 and best_row is not None:
                results.append({
                    'standard_term': std_term,
                    'value': best_row['value'],
                    'matched_tag': best_row['tag'],
                    'matched_label': best_row['label'],
                    'match_method': 'fuzzy_label',
                    'confidence': best_score / 100,
                    'fy': best_row.get('fy'),
                    'fp': best_row.get('fp'),
                    'form': best_row.get('form'),
                    'filed': best_row.get('filed')
                })
            else:
                # 4) No match found
                results.append({
                    'standard_term': std_term,
                    'value': None,
                    'matched_tag': None,
                    'matched_label': None,
                    'match_method': 'none',
                    'confidence': 0.0,
                    'fy': None,
                    'fp': None,
                    'form': None,
                    'filed': None
                })

        return pd.DataFrame(results)

    def match_all(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preserve all matched rows for each standard term, emitting one entry per period.
        Returns a DataFrame with original metadata plus 'standard_term'.
        """
        records = []
        for std_term, tags in self.mapping.items():
            # Select rows where the tag matches any of the mapped US GAAP tags
            df_term = df[df['tag'].isin(tags)].copy()
            if df_term.empty:
                continue
            # Assign the standard term to each row
            df_term['standard_term'] = std_term
            records.append(df_term)
        # Combine all records, or return empty DataFrame
        if records:
            return pd.concat(records, ignore_index=True)
        else:
            # Return empty frame with columns including standard_term
            cols = list(df.columns) + ['standard_term']
            return pd.DataFrame(columns=cols)