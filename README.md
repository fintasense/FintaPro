# MetaSense Financial Term Extraction System
🗂️ Project Summary: Financial Data Extraction & Standardization
🎯 Goal
To extract accurate financial values (like "Net Income", "Operating Expenses", etc.) from company-specific financial data (JSON/Excel formats) and match them with a standard list of terms across thousands of companies, despite variations in term.

✅ What You Have Done So Far
1. Raw Data Sources Used
Downloaded JSON files from SEC EDGAR filings (XBRL companyfacts format).

Worked with raw unfiltered Excel sheets for companies.

Used both structured (XBRL) and unstructured (manual/Excel) data formats.

2. Standard Terms Reference
Created a list of standard financial terms to map to (e.g., “Net Income”, “Cost of Goods Sold”).

Used this as the target dictionary for all mappings.

3. Models & Techniques Tried
a. Basic Matching
Manual and direct string match from raw sheets.

b. Fuzzy Matching
Applied fuzzywuzzy and rapidfuzz to find close matches to standard terms.

Problem: Fails with abbreviations, synonyms, or drastically different naming (e.g., "PP&E" vs "Property, Plant and Equipment").

c. SBERT (Sentence-BERT) Model
Trained a fine-tuned semantic model on Excel data.

Used it to get similarity scores for term mapping.

Still not robust across 9k companies due to company-specific terminologies.

d. Semantic Search + F1 Score
Used similarity metrics and scoring to try best match.

Issue: Scores are not consistent, still not giving perfect mappings.

e. US-GAAP Tag Matching
Explored us-gaap taxonomy tags.

Tried using arelle and XBRL standards to extract canonical concept names.

Result: Even with correct tags, company-specific variations lead to inconsistent matches or missing values.

f. Arelle-Based Parsing
Extracted facts using arelle engine from XBRL files.

Even using tags like us-gaap:NetIncomeLoss, values were either missing or wrong due to inconsistent usage by companies.

g. Used SEC JSON Fact Dictionary
Parsed companyfacts/*.json and checked units, labels, concepts.

Still faced mismatch in names and units, and not always aligned with your standard terms.

❌ Key Issues and Challenges
1. Terminology Mismatch
Every company uses different variations like:

"Net income attributable to controlling interest"

"Income (Loss) before Income Taxes"

"Operating Profit" instead of "Operating Income"

Even after SBERT, semantic similarity doesn’t guarantee exact numeric matches.

2. Inconsistent XBRL/GAAP Tag Usage
Even when using tags like us-gaap:NetIncomeLoss, the values are not always filled correctly or differ based on company filing style.

3. Semantic Model Limitations
Your fine-tuned SBERT model struggles with:

Abbreviations ("PPE")

Grouped terms ("Operating expenses: R&D + SG&A")

Composite fields ("Total Other Income/Expense, net")

4. Lack of a Global Dictionary
No universal SEC/GAAP dictionary that says:

"These 10 variants = Net Income"

So even semantic models need to be manually verified and curated

5. Scalability Problem
With 9,000+ companies, it is impractical to manually cross-check each match.

Can't ensure accuracy without a human-in-the-loop or rule-based fallback system.

6. No Visual Feedback or QA Loop
No system to visually confirm matches or detect anomalies, so incorrect values go undetected unless checked manually.

📌 Next Suggestions (for reference, not part of submission)
You asked not to include solutions here, but as you proceed later, options might include:

Hybrid Rule + Model pipeline

External vendor dataset (like Compustat, CapitalIQ)

Feedback loop via Streamlit interface to manually approve/flag predictions
