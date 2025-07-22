#!/usr/bin/env python3
# scripts/utils/compute_q4.py

import json, sys
from pathlib import Path
from datetime import datetime

def compute_q4(cik: str):
    # 1) load mapping + JSON
    mapping = json.loads(Path("config/standard_to_usgaap_mapping.json").read_text())
    tags    = mapping["income_statement"]["Net sales"]

    raw   = json.loads(Path(f"data/raw/{cik}.json").read_text())
    facts = raw.get("facts", {}).get("us-gaap", {})

    # 2) gather all 10-K entries, grouped by fy→latest end + its value
    k_recs = []
    for tag in tags:
        fact = facts.get(tag) or facts.get(tag.split(":",1)[-1])
        if not fact: continue
        for e in fact.get("units", {}).get("USD", []):
            if e.get("form") == "10-K":
                fy  = e.get("fy")
                end = e.get("end")
                val = e.get("val")
                if fy and end and val is not None:
                    k_recs.append((int(fy), end, val))

    # build a map fy → (latest_end, val)
    fy_map = {}
    for fy, end, val in k_recs:
        # pick the latest end for each fy
        if fy not in fy_map or end > fy_map[fy][0]:
            fy_map[fy] = (end, val)

    years = sorted(fy_map)
    if len(years) < 2:
        print(f"❌ need ≥2 distinct FY 10-Ks for {cik}, found {years}")
        return

    prev_fy, this_fy = years[-2], years[-1]
    prev_end, _   = fy_map[prev_fy]
    this_end, this_val = fy_map[this_fy]

    # 3) collect all 10-Q entries between those two ends, bucketed by fp
    q_buckets = {"Q1": [], "Q2": [], "Q3": []}
    for tag in tags:
        fact = facts.get(tag) or facts.get(tag.split(":",1)[-1])
        if not fact: continue
        for e in fact.get("units", {}).get("USD", []):
            if e.get("form") == "10-Q" and e.get("fp") in q_buckets:
                end = e.get("end")
                val = e.get("val")
                if end and val is not None and prev_end < end < this_end:
                    q_buckets[e["fp"]].append((end, val))

    # 4) for each quarter, pick the minimum val across its dates
    q_vals = {}
    for q in ("Q1","Q2","Q3"):
        if not q_buckets[q]:
            q_vals[q] = None
        else:
            # find the smallest val (true quarter-only)
            _, minval = min(q_buckets[q], key=lambda x: x[1])
            q_vals[q] = minval

    # 5) compute Q4
    q1 = q_vals["Q1"] or 0
    q2 = q_vals["Q2"] or 0
    q3 = q_vals["Q3"] or 0
    q4 = this_val - (q1 + q2 + q3)

    # 6) print
    def fmt(x):
        m = x/1e6
        b = x/1e9
        return f"{x:,}  |  {m:.2f} M  |  {b:.2f} B"

    print(f"\nCIK {cik} — Net sales for FY {this_fy}\n")
    for label in ("Q1","Q2","Q3","Q4"):
        val = {"Q1":q1,"Q2":q2,"Q3":q3,"Q4":q4}[label]
        if label != "Q4" and q_vals[label] is None:
            print(f"  {label}: NOT FOUND")
        else:
            print(f"  {label}: {fmt(val)}")
    print()

if __name__=="__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/utils/compute_q4.py <CIK>")
        sys.exit(1)
    compute_q4(sys.argv[1])