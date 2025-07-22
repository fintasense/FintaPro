import json, sys
from pathlib import Path


def inspect_net_sales(cik: str, year: int):
   sec   = json.loads(Path(f"data/raw/{cik}.json").read_text())
   facts = sec.get("facts", {}).get("us-gaap", {})
   mapping = json.loads(Path("config/standard_to_usgaap_mapping.json").read_text())
   tags = mapping["income_statement"]["Net sales"]


   # Header
   print(f"\nInspecting Net sales entries for {cik}, FY {year}\n")
   print(f"{'TAG':<40} {'END':<12} {'FORM':<6} {'FILED':<10} {'VALUE':>15}  {'MILLIONS':>10}  {'BILLIONS':>10}")
   print("-"*100)


   for tag in tags:
       fact = facts.get(tag) or facts.get(tag.split(":",1)[-1])
       if not fact:
           continue
       for e in fact.get("units", {}).get("USD", []):
           if e.get("fy") != year or e.get("val") is None:
               continue
           form  = e.get("form","")
           end   = e.get("end","")
           filed = e.get("filed","")
           val   = e["val"]
           m     = val / 1e6
           b     = val / 1e9
           print(f"{tag:<40} {end:<12} {form:<6} {filed:<10} {val:15,}  {m:10,.2f}  {b:10,.2f}")


if __name__=="__main__":
   if len(sys.argv)!=3:
       print("Usage: python scripts/utils/inspect_net_sales.py <CIK> <YEAR>")
       sys.exit(1)
   inspect_net_sales(sys.argv[1], int(sys.argv[2]))
