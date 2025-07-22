# config/settings.py

from pathlib import Path

# Base project directory (one level above this file)
BASE_DIR = Path(__file__).resolve().parent.parent

# Data directories
RAW_DIR          = BASE_DIR / "data" / "raw"
INTERMEDIATE_DIR = BASE_DIR / "data" / "intermediate"
PROCESSED_DIR    = BASE_DIR / "data" / "processed"

# Mapping file
MAPPING_PATH     = BASE_DIR / "config" / "standard_to_usgaap_mapping.json"
