# MetaSense Financial Term Extraction System

## Overview

**MetaSense** is an intelligent financial data extraction and standardization system designed to process unstructured and semi-structured financial data from thousands of companies. The system parses JSON/XBRL filings (e.g., from SEC EDGAR), Excel files, and other formats to extract key financial metrics such as Net Income, Operating Expenses, and Cash Flow, despite inconsistent terminology and reporting styles.

## 🎯 Objective

To **extract and standardize financial values** across thousands of company filings by mapping raw terms (e.g., "Operating Profit", "Net income attributable to controlling interest") to a consistent reference of **standard financial terms** like:

- Net Income  
- Operating Income  
- Cost of Goods Sold  
- Property, Plant & Equipment (PP&E)

---

## 📂 Project Structure

MetaSense/
│
├── data/ # Raw and processed data files
│ ├── raw_json/ # JSON files from SEC EDGAR
│ ├── raw_excel/ # Excel-based financials
│ └── processed/ # Cleaned & joined outputs
│
├── notebooks/ # Jupyter notebooks for experiments
│
├── scripts/ # Modular Python scripts
│ ├── extract_from_json.py
│ ├── fuzzy_match.py
│ ├── sbert_match.py
│ └── evaluate_mappings.py
│
├── models/ # SBERT or fine-tuned models
│
├── utils/ # Utility functions (logging, metrics, etc.)
│
├── standard_terms.txt # Reference dictionary of financial terms
├── requirements.txt
└── README.md




---

## ✅ What Has Been Implemented

### 1. **Raw Data Handling**
- Downloaded and parsed SEC EDGAR XBRL `companyfacts/*.json` files.
- Handled Excel sheets from companies with non-standard formats.

### 2. **Standardization Dictionary**
- Created a master list of ~50 standard financial terms.
- Used as a fixed vocabulary to map all variants encountered.

### 3. **Matching Techniques**

| Method             | Description                                                                 |
|--------------------|-----------------------------------------------------------------------------|
| **Exact Match**     | Direct string comparison of terms.                                          |
| **Fuzzy Matching**  | Used `fuzzywuzzy` and `rapidfuzz` for partial and token-based matching.     |
| **SBERT Model**     | Sentence-BERT used to semantically embed raw terms for similarity scoring. |
| **GAAP Tag Parsing**| Extracted `us-gaap:*` fields using `arelle` and SEC JSON fact dictionary.   |

### 4. **Challenges Encountered**
- Mismatches due to inconsistent term naming across companies.
- Limited GAAP tag usage or incorrect filings.
- Composite terms (e.g., grouped R&D + SG&A).
- Model struggling with abbreviations and nested line items.
- No central mapping or verification source.

---

## ❌ Known Limitations

- **Semantic mismatch**: SBERT similarity does not always correlate with the numeric relevance.
- **Inconsistent tag usage**: Even standard tags (e.g., `us-gaap:NetIncomeLoss`) are unreliable across companies.
- **Manual intervention**: No feedback UI for error correction or quality checks.
- **Scaling QA**: Human-in-the-loop is not feasible for 9,000+ companies without interface support.

---

## 🔍 Sample Use Case

```python
from scripts.sbert_match import SemanticTermMatcher
from scripts.extract_from_json import extract_facts_from_sec_json

# Load standard terms
matcher = SemanticTermMatcher("models/sbert_model/", "standard_terms.txt")

# Load raw company facts
facts = extract_facts_from_sec_json("data/raw_json/AAPL.json")

# Perform matching
mapped_terms = matcher.match(facts.keys())

# Output result
print(mapped_terms["Net Income"])  # → 57400000000.0 (example)


📈 Future Improvements (Not Yet Implemented)
Build a Streamlit interface for human verification and QA.

Create a rule-based + ML hybrid system for fallback logic.

Connect to external sources like Compustat or CapitalIQ for validation.

Enhance abbreviation handling and composite field decomposition.

Introduce anomaly detection for numeric mismatches (e.g., unit or scale errors).


# Clone the repository
git clone https://github.com/yourusername/MetaSense.git
cd MetaSense

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt


📜 License
This project is licensed under the MIT License. See the LICENSE file for details.
