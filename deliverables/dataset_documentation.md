# Dataset Documentation

This document summarizes the datasets used in the healthcare access and cost burden project. Counts are based on files currently available in the repository. Public-use documentation is stored in `documentation/`.

## Part I: NHIS Classification Workflow

### Dataset Name

NHIS 2023 Sample Adult, Sample Adult Imputed Income, and Paradata.

### Source and URL

- Source: National Center for Health Statistics, National Health Interview Survey 2023
- URL: https://www.cdc.gov/nchs/nhis/documentation/2023-nhis.html
- Local documentation used for reference:
  - `documentation/adult-codebook (1).pdf`
  - `documentation/adult-summary (1).pdf`
  - `documentation/adultinc-summary.pdf`
  - `documentation/paradata-codebook.pdf`
  - `documentation/paradata-summary.pdf`
  - `documentation/srvydesc-508.pdf`
  - `documentation/srvydesc-paradata-508.pdf`

### Observations and Variables

| File | Observations | Variables | Notes |
|---|---:|---:|---|
| `data/raw/nhis_2023_sample_adult.csv` | 29,522 | 647 | Main Sample Adult public-use file |
| `data/raw/nhis_2023_sample_adult_imputed_income.csv` | 295,220 | 7 | Imputed income records, with multiple imputation structure |
| `data/raw/nhis_2023_paradata.csv` | 63,591 | 123 | Interview process and contact paradata |
| `data/processed/nhis_model_ready_v1.csv` | 28,777 | 57 | Model-ready analytic file used by the app and saved modeling outputs |

### Variable Description Table

| Variable name | Plain-language label | Role | Measurement level | Description | Source file |
|---|---|---|---|---|---|
| `mental_health_cost_barrier` | Cost-related mental health care barrier | Target | Binary | Indicator for delayed or unmet mental health care because of cost, as defined in the modeling workflow | `data/processed/nhis_model_ready_v1.csv` |
| `AGEP_A` | Age | Predictor | Continuous | Adult respondent age | NHIS Sample Adult |
| `SEX_A` | Sex | Predictor | Nominal | Sex category available in the public-use file | NHIS Sample Adult |
| `REGION` | U.S. region | Predictor, grouping | Nominal | Broad Census region | NHIS Sample Adult |
| `RACEALLP_A` | Race group | Predictor | Nominal | Race category in the public-use adult file | NHIS Sample Adult |
| `HISPALLP_A` | Hispanic ethnicity and race group | Predictor | Nominal | Hispanic origin and race grouping | NHIS Sample Adult |
| `EDUCP_A` | Education level | Predictor | Ordinal | Adult education category | NHIS Sample Adult |
| `POVRATTC_A` | Family income to poverty ratio | Predictor | Continuous | Ratio of family income to the federal poverty threshold | NHIS imputed income |
| `poverty_group_imp` | Family income group | Predictor, grouping | Ordinal | Poverty ratio grouped for interpretation | Derived from NHIS imputed income |
| `DISAB3_A` | Disability status | Predictor, grouping | Binary | Disability status summary used in processed outputs | NHIS Sample Adult |
| `PHSTAT_A` | Self-rated health status | Predictor | Ordinal | General health status rating | NHIS Sample Adult |
| `ANXEV_A` | Anxiety history | Predictor | Binary | Ever told had anxiety | NHIS Sample Adult |
| `DEPEV_A` | Depression history | Predictor | Binary | Ever told had depression | NHIS Sample Adult |
| `PAYBLL12M_A` | Problems paying medical bills | Predictor | Binary | Problems paying medical bills in the past 12 months | NHIS Sample Adult |
| `PAYWORRY_A` | Worry about medical bills | Predictor | Ordinal | Worry about being able to pay medical bills | NHIS Sample Adult |
| `MEDDL12M_A` | Delayed medical care because of cost | Predictor | Binary | Delayed care due to cost | NHIS Sample Adult |
| `MEDNG12M_A` | Needed but did not get medical care because of cost | Predictor | Binary | Unmet medical care due to cost | NHIS Sample Adult |
| `affordability_pressure_count` | Number of affordability pressures | Derived predictor, grouping | Count | Count of selected cost and affordability indicators | Processed NHIS |
| `functioning_difficulty_count` | Number of functioning difficulties | Derived predictor, grouping | Count | Count of selected functioning difficulty indicators | Processed NHIS |
| `mental_health_history_count` | Mental health history count | Derived predictor, grouping | Count | Count of selected mental health history indicators | Processed NHIS |
| `MODE_P` | Interview mode | Predictor | Nominal | Paradata measure related to interview process | NHIS Paradata |
| `personal_visit_contact_share` | Personal visit contact share | Derived predictor | Continuous | Derived paradata contact pattern measure | Processed NHIS |
| `telephone_contact_share` | Telephone contact share | Derived predictor | Continuous | Derived paradata contact pattern measure | Processed NHIS |

### Why This Dataset and Problem Are Important

NHIS is useful for studying access barriers because it includes health status, insurance, care access, affordability, disability, income, and demographic measures in a national public-use survey. The project uses NHIS to study a measured cost-related mental health care barrier. The classification workflow is useful because the target is uncommon, which makes model evaluation more nuanced than simple accuracy.

## Part II: MEPS Regression and Cost-Burden Workflow

### Dataset Name

MEPS 2023 HC-251 Full Year Consolidated Public Use File.

### Source and URL

- Source: Agency for Healthcare Research and Quality, Medical Expenditure Panel Survey
- URL: https://meps.ahrq.gov/mepsweb/data_stats/download_data_files.jsp
- Local documentation used for reference:
  - `documentation/h251doc.pdf`
  - `documentation/h251cb.pdf`

### Observations and Variables

| File | Observations | Variables | Notes |
|---|---:|---:|---|
| `data/raw/meps_2023_hc251_full_year_consolidated.xlsx` | Available in repo | Available in repo | Raw Excel public-use file |
| `data/processed/meps_model_ready_v1.csv` | 15,123 | 57 | Model-ready MEPS analytic file used by app outputs |
| `data/processed/meps_model_ready_v1_with_saq.csv` | Available in repo | Available in repo | Model-ready file with additional self-administered questionnaire fields |

### Variable Description Table

| Variable name | Plain-language label | Role | Measurement level | Description | Source file |
|---|---|---|---|---|---|
| `TOTEXP23` | Total healthcare spending | Target | Continuous | Total annual healthcare expenditures used in MEPS regression modeling | MEPS HC-251, processed MEPS |
| `TOTEXP23_log1p` | Total healthcare spending, log scale | Target transform | Continuous | Log-transformed spending used for skew-aware modeling | Processed MEPS |
| `AGE23X` | Age | Predictor | Continuous | Age in years | MEPS HC-251 |
| `SEX` | Sex | Predictor | Nominal | Sex category | MEPS HC-251 |
| `RACETHX` | Race and ethnicity | Predictor | Nominal | Race and ethnicity category | MEPS HC-251 |
| `REGION23` | U.S. region | Predictor | Nominal | Census region | MEPS HC-251 |
| `POVCAT23` | Family income category | Predictor | Ordinal | Poverty or income category | MEPS HC-251 |
| `INSC1231` | Insurance coverage | Predictor | Nominal | Insurance coverage status concept used in modeling | MEPS HC-251 |
| `HAVEUS42` | Usual source of care | Predictor | Binary or categorical | Indicator related to having a usual source of care | MEPS HC-251 |
| `DLAYCA42` | Delayed medical care | Predictor | Binary or categorical | Delayed medical care indicator | MEPS HC-251 |
| `AFRDCA42` | Could not afford medical care | Predictor | Binary or categorical | Affordability barrier for medical care | MEPS HC-251 |
| `DLAYPM42` | Delayed prescription medicines | Predictor | Binary or categorical | Delayed prescriptions indicator | MEPS HC-251 |
| `AFRDPM42` | Could not afford prescription medicines | Predictor | Binary or categorical | Affordability barrier for prescription medicines | MEPS HC-251 |
| `DLAYDN42` | Delayed dental care | Predictor | Binary or categorical | Delayed dental care indicator | MEPS HC-251 |
| `AFRDDN42` | Could not afford dental care | Predictor | Binary or categorical | Affordability barrier for dental care | MEPS HC-251 |
| `chronic_condition_count` | Chronic condition count | Derived predictor | Count | Count of selected chronic condition indicators | Processed MEPS |
| `mental_health_screen_count` | Mental health screen count | Derived predictor | Count | Count of selected mental health screening indicators | Processed MEPS |
| `physical_difficulty_count` | Physical difficulty count | Derived predictor | Count | Count of selected physical difficulty indicators | Processed MEPS |
| `access_barrier_count` | Access barrier count | Derived predictor | Count | Count of selected access and affordability barrier indicators | Processed MEPS |
| `high_cost_segment` | High-cost segment | Review concept | Ordinal group | Top spending groups used for high-cost model review | `meps_objective*_high_cost_segment_review.csv` |
| `Actual quintile` | Actual spending group | Review output | Ordinal group | Actual observed spending quintile in the saved review output | `meps_objective1_predicted_actual_quintile.csv` |

### Why This Dataset and Problem Are Important

MEPS is useful for the regression extension because it focuses on healthcare expenditures, use, insurance coverage, and payment context. Healthcare spending is typically skewed, with many low-cost rows and a smaller group of very high-cost rows. That makes regression evaluation challenging and motivates high-cost segment review, predicted-vs-actual spending group review, and skew-aware model checks.

