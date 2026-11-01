"""Fit the three prespecified ordered-logit models and save aggregate tables only."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import warnings

import numpy as np
import pandas as pd
from scipy.stats import norm
from statsmodels.miscmodels.ordinal_model import OrderedModel

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
SENSITIVE_NAME_PARTS = ("prolific", "postcode", "postal", "timestamp", "time", "duration")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Sanitized Excel workbook; first worksheet is used")
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/tables"))
    args = parser.parse_args()
    if not args.input.is_file():
        parser.error(f"Input workbook not found: {args.input}")

    raw = pd.read_excel(args.input, sheet_name=0, engine="openpyxl")
    raw.columns = [str(c).strip() for c in raw.columns]
    sensitive = [c for c in raw.columns if any(term in c.lower().replace(" ", "_") for term in SENSITIVE_NAME_PARTS)]
    if sensitive:
        print("Remove identifier/timing columns before running: " + ", ".join(sensitive), file=sys.stderr)
        return 2
    required = list(OUTCOMES.values()) + list(PREDICTORS.values())
    missing = [c for c in required if c not in raw.columns]
    if missing:
        print("Required analysis columns are missing: " + ", ".join(missing), file=sys.stderr)
        return 2

    # Restrict the in-memory frame to the analysis whitelist immediately.
    data = raw.loc[:, required].apply(pd.to_numeric, errors="coerce")
    # Thesis coding: original herding code 3 is the herding group (2); codes 1–2 are comparison (1).
    for col in (PREDICTORS["BHI"], PREDICTORS["BHS"]):
        data[col] = data[col].map(lambda value: 2 if value == 3 else (1 if value in (1, 2) else np.nan))

    args.output_dir.mkdir(parents=True, exist_ok=True)
    model_rows: list[dict] = []
    coefficient_rows: list[dict] = []
    for outcome_label, outcome_col in OUTCOMES.items():
        model_data = data[[outcome_col, *PREDICTORS.values()]].dropna().copy()
        model_data = model_data[model_data[outcome_col].isin([1, 2, 3, 4, 5])]
        if model_data.empty:
            print(f"No complete cases for {outcome_label}; skipping.", file=sys.stderr)
            continue
        y = model_data[outcome_col].astype(int)
        X = model_data[list(PREDICTORS.values())].astype(float)
        # Avoid an explicit constant: OrderedModel estimates cut-points as thresholds.
        if (X.nunique(dropna=True) <= 1).any():
            constant = [PREDICTORS[k] for k in PREDICTORS if X[PREDICTORS[k]].nunique(dropna=True) <= 1]
            print(f"Constant predictor(s) in {outcome_label}: {constant}; remove or investigate.", file=sys.stderr)
            return 2

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            model = OrderedModel(y, X, distr="logit")
            result = model.fit(method="bfgs", maxiter=2000, disp=False)
        params = result.params
        bse = result.bse
        pvalues = result.pvalues
        ci = result.conf_int()
        for label, source in PREDICTORS.items():
            beta = float(params[source])
            se = float(bse[source])
            coefficient_rows.append({
                "outcome": outcome_label,
                "predictor": label,
                "coefficient_log_odds": beta,
                "standard_error": se,
                "z_value": float(beta / se) if se else np.nan,
                "p_value": float(pvalues[source]),
                "odds_ratio": float(np.exp(beta)),
                "or_ci_95_low": float(np.exp(ci.loc[source, 0])),
                "or_ci_95_high": float(np.exp(ci.loc[source, 1])),
                "n": int(result.nobs),
            })
        counts = y.value_counts().reindex([1, 2, 3, 4, 5], fill_value=0)
        model_rows.append({
            "outcome": outcome_label,
            "n": int(result.nobs),
            "category_1_n": int(counts.loc[1]),
            "category_2_n": int(counts.loc[2]),
            "category_3_n": int(counts.loc[3]),
            "category_4_n": int(counts.loc[4]),
            "category_5_n": int(counts.loc[5]),
            "log_likelihood": float(result.llf),
            "aic": float(result.aic),
            "bic": float(result.bic),
            "converged": bool(result.mle_retvals.get("converged", False)),
            "iterations": int(result.mle_retvals.get("iterations", -1)),
            "proportional_odds_tested": False,
        })
        if caught:
            print(f"{outcome_label}: {len(caught)} estimation warning(s); inspect convergence and output.", file=sys.stderr)

    if not model_rows:
        print("No models were estimated.", file=sys.stderr)
        return 2
    pd.DataFrame(model_rows).to_csv(args.output_dir / "model_summary.csv", index=False)
    pd.DataFrame(coefficient_rows).to_csv(args.output_dir / "ordered_logit_coefficients.csv", index=False)
    print(f"Estimated {len(model_rows)} ordered-logit model(s); aggregate tables saved to {args.output_dir}.")
    print("The script does not test the proportional-odds assumption. See docs/analysis_notes.md.")
    print("No row-level analysis file was written.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
