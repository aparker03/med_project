# Score Dataset and Results

This document describes the score dataset and saved scoring outputs for Part I, the NHIS classification workflow.

## Files

| File | Rows | Columns | Purpose |
|---|---:|---:|---|
| `data/processed/nhis_score_input_30_no_target.csv` | 30 | 34 | Input records for scoring, with the target removed |
| `data/processed/nhis_score_output_30_predictions.csv` | 30 | 12 | Saved model predictions, probabilities, labels, ranks, and top-group flag |
| `data/processed/nhis_score_validation_hidden_target.csv` | 30 | 2 | Hidden target reference for checking the scoring exercise |

## Score Input Dataset

File: `data/processed/nhis_score_input_30_no_target.csv`

The score input contains 30 rows with a `score_id` and predictor columns used by the saved models. It includes demographic, health, access, paradata, and derived count variables such as:

- `AGEP_A`
- `DISAB3_A`
- `REGION`
- `SEX_A`
- `poverty_group_imp`
- `affordability_pressure_count`
- `functioning_difficulty_count`
- `mental_health_history_count`
- `personal_visit_contact_share`
- `telephone_contact_share`

The target column is excluded on purpose. In a real scoring setting, the model receives predictor information and generates a probability or label for a new row. Keeping the target out of the score input prevents accidental leakage and makes the scoring exercise closer to a deployment workflow.

## Scored Output

File: `data/processed/nhis_score_output_30_predictions.csv`

The scored output contains predictions from the saved objective models. Key columns include:

- `score_id`
- `objective1_model`
- `objective1_probability`
- `objective1_predicted_label_050`
- `objective2_model`
- `objective2_probability`
- `objective2_predicted_label_050`
- `objective3_model`
- `objective3_probability`
- `objective3_predicted_label_050`
- `objective3_rank`
- `objective3_top_20pct_flag`

The probability columns show model-estimated probability for the measured target class. The 0.50 label columns show a thresholded prediction at the default threshold. The rank and top-20 percent flag support aggregate ranking review for Objective 3.

## Hidden Validation or Target Reference

File: `data/processed/nhis_score_validation_hidden_target.csv`

This file keeps the actual target reference separate from the score input. It includes:

- `score_id`
- `actual_target_hidden_check`

The hidden target reference can be used after scoring to check whether the scoring workflow joined predictions back to the correct rows. It should not be included in the score input because that would leak the answer into the prediction step.

## Interpretation Notes

The score files demonstrate a workflow, not an operational decision system. The output probabilities and labels should not be used to make clinical, insurance, eligibility, pricing, or individual outreach decisions. They are useful for showing how saved model artifacts could be applied to a held-out scoring file and then reviewed with caution.

