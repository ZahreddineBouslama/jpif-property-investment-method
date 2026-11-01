"""Validate a local, sanitized workbook without exporting respondent-level data."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

OUTCOMES = {
    "RCG": "I2_IP_IOT",
    "RFR": "I3_IP_AFR",
    "RHI": "I4_IP_HAI",
}
PREDICTORS = {
    "BHI": "B2_informherdnum",
    "BHS": "B3_socialherdnum",
    "BO": "B1_Omission_likert",
    "AGE": "D1_age_num",
    "DXP": "D2_XP_RE",
    "DIG": "D3_incomegroupnum",
    "DE": "D4_educationnum",
    "DG": "D5_gendernum",
    "DLOSS": "D6_riskprofile1num",
    "DGAIN": "D7_riskprofile2num",
    "NSEQ": "N1_seq1bin",
    "NLTV": "N3_LTV",
    "NVAL": "N4_Val_fin",
}
REQUIRED = list(OUTCOMES.values()) + list(PREDICTORS.values())
SENSITIVE_NAME_PARTS = ("prolific", "postcode", "postal", "timestamp", "time", "duration")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Sanitized Excel workbook; first worksheet is used")
    args = parser.parse_args()
    if not args.input.is_file():
        parser.error(f"Input workbook not found: {args.input}")

    frame = pd.read_excel(args.input, sheet_name=0, engine="openpyxl")
    frame.columns = [str(c).strip() for c in frame.columns]
    sensitive = [c for c in frame.columns if any(term in c.lower().replace(" ", "_") for term in SENSITIVE_NAME_PARTS)]
    if sensitive:
        print("Input has columns that should be removed before analysis:", ", ".join(sensitive), file=sys.stderr)
        return 2
    missing = [c for c in REQUIRED if c not in frame.columns]
    if missing:
        print("Required analysis columns are missing: " + ", ".join(missing), file=sys.stderr)
        return 2

    print(f"Workbook validated: first worksheet has {len(frame)} rows and {len(frame.columns)} columns.")
    print("Required analysis variables are present. No respondent-level file was written.")
    for label, source in OUTCOMES.items():
        observed = pd.to_numeric(frame[source], errors="coerce").dropna()
        invalid = sorted(set(observed) - {1, 2, 3, 4, 5})
        if invalid:
            print(f"Warning: {label} contains values outside 1–5: {invalid}", file=sys.stderr)
        print(f"{label}: non-missing={len(observed)}, categories={sorted(observed.unique().tolist())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
