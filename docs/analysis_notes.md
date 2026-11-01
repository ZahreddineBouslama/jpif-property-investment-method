# Analysis notes

## Variable map

| Analysis label | Source column | Role |
|---|---|---|
| RCG | `I2_IP_IOT` | Ordered capital-gain rationale outcome |
| RFR | `I3_IP_AFR` | Ordered financial-return rationale outcome |
| RHI | `I4_IP_HAI` | Ordered inflation-hedging rationale outcome |
| BHI | `B2_informherdnum` | Information-herding indicator; code 3 becomes 2, codes 1–2 become 1 |
| BHS | `B3_socialherdnum` | Social-herding indicator; code 3 becomes 2, codes 1–2 become 1 |
| BO | `B1_Omission_likert` | Omission/regret measure |
| AGE | `D1_age_num` | Age category/measure as coded in source |
| DXP | `D2_XP_RE` | Real-estate experience measure |
| DIG | `D3_incomegroupnum` | Income group |
| DE | `D4_educationnum` | Education category |
| DG | `D5_gendernum` | Gender category |
| DLOSS | `D6_riskprofile1num` | Risk-profile measure 1 |
| DGAIN | `D7_riskprofile2num` | Risk-profile measure 2 |
| NSEQ | `N1_seq1bin` | Normative sequence measure |
| NLTV | `N3_LTV` | Loan-to-value consideration |
| NVAL | `N4_Val_fin` | Valuation/financial consideration |

Check all category meanings against the questionnaire and thesis codebook before interpreting coefficients. Several predictors are categorical codes; treating them as numeric imposes a linear trend across categories. This mirrors the prior thesis specification but should be justified or tested against factor-coded specifications in the final paper.

## Estimation and reporting

Each outcome is estimated using a five-category cumulative logit (ordered logit) model with the same predictor set and complete cases for that outcome. The script uses `statsmodels.miscmodels.ordinal_model.OrderedModel` with a logit link. Report the analytic N for every model, coefficient direction, uncertainty, odds ratios where helpful, and model fit.

The proportional-odds assumption is substantive, not a technical footnote. The financial-return model was previously reported to violate it. Before making inferential claims from that model, inspect the original diagnostic output and implement a justified alternative or sensitivity analysis (for example, a partial proportional-odds model or a clearly motivated category-specific model). The present script does not perform the proportional-odds test and does not implement partial proportional odds. State this limitation rather than implying the assumption was tested here.

With N=150 and 13 predictors, sparse outcome/predictor categories and overfitting are possible. Inspect convergence, standard errors, category counts, and influence. The analysis is observational and cross-sectional; results are associations, not causal effects. Mention the February 2020 survey date and limits to generalisability in the article.

## Data protection

Input validation rejects common direct-identifier or timing column names. The code reads only the required analysis columns and writes no case-level file. This is a guardrail, not a substitute for data governance: use only an authorized, sanitized workbook and do not commit it or its derivatives.
