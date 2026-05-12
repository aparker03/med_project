# Healthcare Access and Cost Burden Explorer

This project studies healthcare access barriers and cost burden using public-use survey data. The work combines notebook-based data preparation and modeling with a Streamlit app that presents the saved outputs in a more readable form.

The project is intended for both technical and nontechnical readers. It keeps plain-language interpretation close to the results while preserving links back to the underlying variables, processed files, and modeling artifacts.

## Project Purpose

The main purpose is to examine patterns in healthcare access, affordability pressure, healthcare cost burden, and cost-related mental health care barriers. The project focuses on descriptive summaries and saved model outputs. It does not make causal claims, and it should not be used to make decisions about individual people.

## Data Sources

The repository uses public-use files from national health surveys:

- NHIS 2023 Sample Adult
- NHIS 2023 Sample Adult Imputed Income
- NHIS 2023 Paradata
- MEPS 2023 HC-251 Full Year Consolidated Public Use File

The Streamlit app reads saved CSV outputs from `data/processed`. It does not read raw files directly.

## Repository Structure

```text
app/
  Streamlit app, pages, shared utilities, and app-specific README

data/
  raw/          Original public-use source files
  interim/      Intermediate cleaned and merged files
  processed/    Model-ready files, weighted summaries, and saved model outputs

documentation/
  Public-use codebooks, survey documentation, and reference PDFs

notebooks/
  Data cleaning, merging, exploratory analysis, and modeling workflow

requirements.txt
  Python packages needed to run the app and notebooks
```

## Notebook Workflow

The current notebook workflow is organized around NHIS and MEPS preparation and modeling:

1. `notebooks/01_nhis_eda_cleaning.ipynb`  
   Initial NHIS exploration and cleaning.

2. `notebooks/02_nhis_merge_income_paradata.ipynb`  
   Merge NHIS Sample Adult data with imputed income and paradata.

3. `notebooks/03_nhis_modeling.ipynb`  
   NHIS modeling workflow and saved model-output CSVs.

4. `notebooks/01_meps_eda_cleaning_(4).ipynb`  
   Initial MEPS exploration and cleaning.

5. `notebooks/05_meps_modeling_(1).ipynb`  
   MEPS modeling work in progress.

## Processed Data Outputs

The `data/processed` folder currently includes NHIS model-ready data, weighted group-rate summaries, model comparison files, feature importance, threshold reviews, lift review outputs, and small scoring examples.

Key processed outputs include:

- `nhis_model_ready_v1.csv`
- `nhis_weighted_rate_by_*.csv`
- `nhis_objective1_model_comparison_results.csv`
- `nhis_objective1_random_forest_feature_importance.csv`
- `nhis_objective1_threshold_review.csv`
- `nhis_objective2_interpretable_model_results.csv`
- `nhis_objective3_lift_cost_sensitive_results.csv`
- `nhis_objective3_threshold_review.csv`
- `nhis_score_input_30_no_target.csv`
- `nhis_score_output_30_predictions.csv`
- `nhis_score_validation_hidden_target.csv`
- `nhis_statistical_screening_checks.csv`

## Streamlit App

The Streamlit app lives in `app/`. It provides a project workspace for reviewing saved outputs without rerunning notebooks or retraining models.

Current pages include:

- Home page with project status and available output counts
- NHIS Explorer for weighted rates by group
- MEPS Explorer for app-ready MEPS CSV previews when processed files are available
- Model Lab for saved model comparisons, feature importance, threshold tradeoffs, and lift review
- Ethics and Limitations
- Data Dictionary companion reference

See `app/README.md` for app-specific details.

## Ethical and Methodological Notes

This project uses public-use survey data. Public-use files are designed to reduce disclosure risk, but they still describe real people and should be handled carefully.

Important interpretation notes:

- Survey weights are important for population-level estimates.
- Raw sample counts should be checked when comparing groups.
- The weighted summaries describe group patterns. They do not prove cause and effect.
- Model outputs describe learned patterns in the saved training and evaluation workflow.
- Predictions and model scores should not be used as clinical tools, eligibility tools, pricing tools, or individual risk labels.
- Feature importance is not the same as causality.

## How to Run the App Locally

From the repository root:

```powershell
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

The app expects the existing processed CSV files to remain in `data/processed`.

## Requirements

The app requirements are listed in `requirements.txt`:

- streamlit
- pandas
- numpy
- plotly
- scikit-learn
- openpyxl

## Current Status

The app is under active development. The NHIS Explorer and Model Lab use saved NHIS outputs now. MEPS app pages are prepared for processed or interim MEPS CSVs, but the current app does not read raw MEPS data directly.

