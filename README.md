# Behavioural Influences on UK Property Investment Decisions

### Python replication materials for a single-authored JPIF practice briefing (in preparation)

This repository documents the analytical method for a survey study of UK residential property investment decision-making. The analysis considers whether behavioural and normative influences are associated with investors' stated rationales for property investment.

**No respondent-level survey data are included.** The data file contains participant and response metadata and is therefore kept local. The scripts accept a locally held workbook and produce aggregate tables only. Do not commit the original workbook, Prolific identifiers, postcodes, timestamps, or any row-level survey file to a public repository.

## Research design

The working dataset contains 150 UK respondents in full-time employment, surveyed in February 2020. The three ordered dependent variables are respondents' agreement with investment rationales:

- `RCG`: capital gain (`I2_IP_IOT`)
- `RFR`: financial return (`I3_IP_AFR`)
- `RHI`: inflation hedging (`I4_IP_HAI`)

Each outcome is coded on an ordered 1–5 response scale. The explanatory variables reproduce the thesis specification: information herding (`BHI`), social herding (`BHS`), omission/regret (`BO`), age, property experience, income, education, gender, loss and gain risk profiles, normative sequence (`NSEQ`), loan-to-value (`NLTV`), and valuation/financial considerations (`NVAL`). The two herding variables are recoded to 1 for source codes 1–2 and 2 for source code 3, following the thesis operationalisation.

## Method

The primary models are separate ordered logistic regressions for RCG, RFR, and RHI. This preserves the ordinal nature of each five-category outcome. The proportional-odds assumption must be assessed and reported for each outcome. The financial-return model was previously flagged as failing that assumption in the thesis analysis; treat its conventional ordered-logit estimates as provisional unless a suitable alternative or sensitivity analysis is reported. Do not infer causal effects from these cross-sectional associations.

The script reports analytic sample size, outcome-category counts, coefficients, standard errors, p-values, odds ratios, fit statistics, and convergence status. It writes only aggregate outputs. See `docs/analysis_notes.md` for caveats and the variable map.

## Run the pipeline

Use Python 3.10 or later. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Prepare a **local, sanitized copy** of the final first worksheet. It must retain the analysis columns named below, but remove Prolific ID, postcode, timestamp, and other direct identifiers. Keep the workbook outside the repository or under the ignored `data/raw/` directory.

```bash
python src/01_validate_input.py --input data/raw/final_sanitized.xlsx
python src/02_run_ordered_models.py --input data/raw/final_sanitized.xlsx
```

The scripts read the first worksheet. The model script writes aggregate CSVs under `outputs/tables/`. Review the output and compare against the thesis/SPSS results before using any estimates in the article. Because the dataset is not included, another researcher needs authorized access to the survey data to reproduce numerical results.

## Repository layout

```text
jpif-property-investment-method/
├── data/
│   ├── raw/                 # local-only input; ignored by git
│   └── README.md
├── docs/
│   └── analysis_notes.md
├── outputs/tables/          # aggregate outputs; generated locally
├── src/
│   ├── 01_validate_input.py
│   └── 02_run_ordered_models.py
├── .gitignore
├── requirements.txt
└── README.md
```

## Citation

Bouslama, Z. (manuscript in preparation). *Financially Rational, Behaviourally Influenced: Why Property Investors Follow the Crowd*. Journal of Property Investment & Finance, Practice Briefing (planned submission).

Please update this citation if the manuscript is accepted or published. Do not describe the manuscript as published before then.
