# Streamlit App

This folder contains the Streamlit app for the Healthcare Access and Cost Burden Explorer. The app turns saved CSV outputs into a readable project workspace for reviewing weighted NHIS summaries, MEPS spending outputs, model artifacts, limitations, and variable references.

The app uses existing processed files only. It does not retrain models, rewrite data, or read raw survey files directly.

## What the App Does

The app helps users review:

- Survey-weighted NHIS rates for a cost-related mental health care barrier
- Raw sample counts behind each weighted group estimate
- Saved model comparison results
- Saved feature importance outputs
- Saved threshold tradeoffs
- Saved lift and cost-sensitive review outputs
- MEPS high-cost segment reviews
- MEPS predicted-vs-actual spending group review
- MEPS robust and skew-aware modeling results
- Ethical and methodological cautions
- Plain-language labels linked back to technical variable names

The app is designed as a project review space, not as a clinical tool or an operational decision system.

## App Pages

```text
streamlit_app.py
  Home page and app entry point

pages/1_NHIS_Explorer.py
  Interactive weighted-rate explorer for NHIS processed summaries

pages/2_MEPS_Explorer.py
  MEPS spending, high-cost segment, predicted-vs-actual group, and skew-aware output review

pages/3_Model_Lab.py
  Saved NHIS and MEPS model comparisons, feature importance, threshold tradeoffs, lift review, skew-aware review, and metric explanations

pages/4_Ethics_and_Limitations.py
  Public-use data, privacy, survey weights, non-causal interpretation, and model-use cautions

pages/5_Data_Dictionary.py
  Companion reference for plain-language labels, variable names, source files, and cautions
```

Shared helpers live in `app/utils/`.

## Data Files Used by the App

The app reads CSV files from `data/processed`, including:

- `nhis_model_ready_v1.csv`
- `nhis_weighted_rate_by_affordability_pressure_count.csv`
- `nhis_weighted_rate_by_DISAB3_A.csv`
- `nhis_weighted_rate_by_functioning_difficulty_count.csv`
- `nhis_weighted_rate_by_mental_health_history_count.csv`
- `nhis_weighted_rate_by_poverty_group_imp.csv`
- `nhis_weighted_rate_by_REGION.csv`
- `nhis_weighted_rate_by_SEX_A.csv`
- `nhis_objective1_model_comparison_results.csv`
- `nhis_objective1_random_forest_feature_importance.csv`
- `nhis_objective1_threshold_review.csv`
- `nhis_objective2_interpretable_model_results.csv`
- `nhis_objective3_lift_cost_sensitive_results.csv`
- `nhis_objective3_threshold_review.csv`
- `meps_model_ready_v1.csv`
- `meps_model_ready_v1_with_saq.csv`
- `meps_modeling_checkpoint.csv`
- `meps_objective1_model_comparison_results.csv`
- `meps_objective1_feature_importance.csv`
- `meps_objective1_high_cost_segment_review.csv`
- `meps_objective1_predicted_actual_quintile.csv`
- `meps_objective2_interpretable_model_results.csv`
- `meps_objective3_high_cost_segment_review.csv`
- `meps_objective3_robust_skew_aware_results.csv`

The MEPS page uses saved processed MEPS CSVs in `data/processed`. It intentionally avoids `data/raw`.

## How to Run Locally

From the repository root:

```powershell
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

If a processed file is missing, the app should show a friendly message instead of failing silently.

## Design Goals

The app is being shaped around a few practical goals:

- Accessible contrast in dark mode
- Plain-language labels before technical variable names
- Readable charts with larger labels and short captions
- Visible raw sample counts for weighted survey summaries
- MEPS spending charts that acknowledge skewed expenditure outcomes
- Careful model interpretation
- Clear separation between app pages, chart helpers, labels, metrics, and text blocks

## Model Lab Caution

The Model Lab is a decision-support learning tool for reviewing saved model behavior. It is not a clinical tool, eligibility tool, pricing tool, financial hardship labeler, or individual risk labeler.

The saved NHIS models estimate whether a row belongs to the measured target class based on patterns in training data. In this project, that target is a cost-related mental health care barrier. The saved MEPS models focus on healthcare spending outcomes, which are often skewed because many people have low or zero costs and a smaller group has very high costs. The model outputs can help compare tradeoffs such as precision, recall, F1, AUC, average precision, threshold behavior, lift, MAE, RMSE, high-cost segment error, and skew-aware performance. They do not identify who truly needs care or who deserves services.

## Future Improvements

Possible next steps include:

- Add survey-design notes near each weighted estimate
- Add exportable chart images or summary tables
- Improve subgroup stability warnings for small raw sample counts
- Add richer MEPS spending and utilization summaries as more processed outputs stabilize
- Add tests for app utility functions
- Add a deployment configuration once the app structure stabilizes
