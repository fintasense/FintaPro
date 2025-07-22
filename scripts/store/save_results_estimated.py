import json
from pathlib import Path
import pandas as pd

def _collect_fy_map(mapping: dict, raw_facts: dict):
    fy_map = {}
    # 1) real 10-Ks
    for section in mapping.values():
        for tags in section.values():
            for tag in tags:
                fact = raw_facts.get(tag) or raw_facts.get(tag.split(":",1)[-1])
                if not fact: continue
                for e in fact.get("units", {}).get("USD", []):
                    if e.get("form") == "10-K" and e.get("fy") and e.get("end"):
                        fy, end = int(e["fy"]), e["end"]
                        if fy not in fy_map or end > fy_map[fy]:
                            fy_map[fy] = end
    # 2) latest 10-Qs
    latest_10q = {}
    for section in mapping.values():
        for tags in section.values():
            for tag in tags:
                fact = raw_facts.get(tag) or raw_facts.get(tag.split(":",1)[-1])
                if not fact: continue
                for e in fact.get("units", {}).get("USD", []):
                    if (
                        e.get("form") == "10-Q" 
                        and e.get("fy") and e.get("end") and e.get("val") is not None
                    ):
                        fy, end = int(e["fy"]), e["end"]
                        if fy not in latest_10q or end > latest_10q[fy][0]:
                            latest_10q[fy] = (end, e["val"])
    # inject in-progress FY
    if latest_10q:
        max_q_fy = max(latest_10q)
        if max_q_fy not in fy_map:
            fy_map[max_q_fy] = latest_10q[max_q_fy][0]
    return fy_map

def save_results_estimated(df_matched: pd.DataFrame, mapping_path: str, out_path: str):
    """
    Wraps your existing save_results to include the latest 10-Q as pseudo-10-K.
    """
    # infer CIK
    cik = Path(out_path).stem.split("_")[0]

    # load mapping & raw JSON
    mapping = json.load(Path(mapping_path).open())
    raw = json.loads(Path(f"data/raw/{cik}.json").read_text())
    raw_facts = raw.get("facts", {}).get("us-gaap", {})

    # build the augmented fy_map
    fy_map = _collect_fy_map(mapping, raw_facts)

    # now call your original save_results, passing the **override** map as kwarg
    from scripts.store.save_results import save_results
    save_results(df_matched, mapping_path, out_path, fy_map_override=fy_map)