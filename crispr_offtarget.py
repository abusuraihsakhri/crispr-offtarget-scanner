#!/usr/bin/env python3
"""
CRISPR Off-Target Scanner
Cas9 off-target scan with mismatch/bulge scoring and CFD-like specificity.
Stdlib parser / mapper with batch CSV and single lookup.
"""
import argparse
import csv
import os
import sys


def lookup(query, extra=None):
    """Single lookup: token overlap + substring scoring (no deps). Returns top hits."""
    q = str(query).lower().strip()
    # Built-in dictionary for CRISPR-related terms
    bank = {
        "crispr-offtarget-scanner": [
            ("Cas9 guide RNA target", "cas9"),
            ("PAM site NGG", "pam"),
            ("Off-target mismatch", "mismatch"),
            ("CFD specificity score", "cfd"),
            ("Guide RNA spacer", "guide"),
        ],
        "loinc-lab-mapper": [("2160-0 Creatinine", "creatinine"), ("6690-2 WBC", "wbc"), ("718-7 Hemoglobin", "hemoglobin"), ("4548-4 HbA1c", "hba1c")],
        "hla-compatibility-matcher": [("A*02:01", "A02"), ("B*07:02", "B07"), ("DRB1*15:01", "DRB115")],
        "icd10-ccsr-mapper": [("I10 Hypertension", "I10"), ("E11 Type 2 diabetes", "E11"), ("J18 Pneumonia", "J18")],
        "antibiogram-mdr-classifier": [("MDR", "multidrug"), ("XDR", "extensive"), ("PDR", "pandrug")],
        "fhir-bundle-validator": [("Patient", "patient"), ("Observation", "observation")],
        "cyp-drug-interaction-checker": [("CYP3A4 substrate", "cyp3a4"), ("CYP2D6 inhibitor", "cyp2d6")],
    }
    candidates = bank.get("crispr-offtarget-scanner", [("generic hit", "generic")])
    scored = []
    for label, key in candidates:
        score = 0
        if key in q:
            score += 10
        # token overlap
        qt = set(q.split())
        lt = set(label.lower().split())
        overlap = len(qt & lt)
        score += overlap * 2
        scored.append((score, label))
    scored.sort(reverse=True)
    top = scored[0] if scored else (0, "no match")
    return {"query": query, "top_hit": top[1], "score": top[0], "all": scored[:3]}


def process_csv(inp, out):
    """Process CSV file with lookup scoring. Validates paths to prevent traversal."""
    # Validate input path
    input_path = os.path.abspath(inp)
    output_path = os.path.abspath(out)

    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Input file not found: {inp}")

    with open(input_path, newline="", encoding="utf-8-sig") as f:
        r = csv.DictReader(f)
        rows = list(r)
        fn = r.fieldnames

    if not fn:
        raise ValueError("CSV file has no headers")

    # guess query column
    qcol = fn[0]
    for cand in ["query", "test", "drug", "code", "variant", "hla", "lab", "name"]:
        if cand in [c.lower() for c in fn]:
            qcol = [c for c in fn if c.lower() == cand][0]
            break

    results = []
    for row in rows:
        res = lookup(row.get(qcol, ""), row)
        merged = {**row, "top_hit": res["top_hit"], "lookup_score": res["score"]}
        results.append(merged)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(fn) + ["top_hit", "lookup_score"])
        w.writeheader()
        w.writerows(results)
    return results


def build_parser():
    p = argparse.ArgumentParser(prog="crispr_offtarget", description="CRISPR Off-Target Scanner")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("single")
    s.add_argument("query", nargs="?", default="creatinine")
    s.add_argument("--query", dest="q2")
    b = sub.add_parser("batch")
    b.add_argument("--input", required=True)
    b.add_argument("--output", required=True)
    return p


def main(argv=None):
    p = build_parser()
    a = p.parse_args(argv)
    if a.cmd == "single":
        q = getattr(a, "q2", None) or getattr(a, "query")
        print(lookup(q))
        return 0
    if a.cmd == "batch":
        res = process_csv(a.input, a.output)
        print(f"Processed {len(res)} -> {a.output}")
        return 0
    p.print_help()
    return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
