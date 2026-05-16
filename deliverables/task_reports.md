# Task Reports

This document summarizes the modeling tasks, plans, saved evidence, and recommendations. All evidence comes from saved CSV outputs in `data/processed`.

## Part I: NHIS Classification

### Objective 1: Model Comparison

**Written plan developed before execution**

Compare several classification models for the cost-related mental health care barrier target. Use metrics that are appropriate for an uncommon target, especially ROC AUC, average precision, recall, precision, and F1. Avoid relying on accuracy alone.

**Evidence of execution with annotated outputs**

Evidence file: `data/processed/nhis_objective1_model_comparison_results.csv`

Key saved results:

| Model or version | Notable saved output | Annotation |
|---|---|---|
| `A_baseline_adult_income / random_forest_balanced` | ROC AUC 0.8759, recall 0.7293, precision 0.2442 | Strong ranking performance with high recall at the saved threshold |
| `B_baseline_plus_paradata / random_forest_balanced` | ROC AUC 0.8756, recall 0.7052, precision 0.2578 | Similar ranking performance with paradata added |
| `gradient_boosting` versions | Accuracy about 0.94, recall about 0.19 to 0.20 | High accuracy but lower recall, which is less useful for a rare measured barrier |
| `logistic_regression_balanced` versions | Recall about 0.769, ROC AUC about 0.874 to 0.875 | Strong recall and simpler model structure than random forest |

**Conclusion and recommendation**

The balanced random forest is a strong Objective 1 recommendation for ranking performance, with the baseline adult-income version slightly highest on ROC AUC. The balanced logistic regression is also important because it provides a simpler benchmark with strong recall. The final choice should depend on whether the presentation emphasizes ranking performance, interpretability, or sensitivity to possible barriers.

### Objective 2: Interpretable Model Review

**Written plan developed before execution**

Compare simpler or more interpretable classifiers against flexible models. Use ROC AUC, recall, precision, and F1 to understand the tradeoff between explanation quality and predictive behavior.

**Evidence of execution with annotated outputs**

Evidence file: `data/processed/nhis_objective2_interpretable_model_results.csv`

Key saved results:

| Model | Notable saved output | Annotation |
|---|---|---|
| `logistic_regression_unweighted` | ROC AUC 0.8761, precision 0.5629, recall 0.1856 | Strong ranking and precision, but low recall |
| `logistic_regression_balanced` | ROC AUC 0.8749, recall 0.7686, F1 0.3391 | More sensitive to the positive class |
| `shallow_tree_balanced` | Recall 0.7402, ROC AUC 0.8495 | Easier to explain than a forest, but weaker ranking |

**Conclusion and recommendation**

The balanced logistic regression is a useful interpretable recommendation when recall is important. The unweighted logistic regression is useful as a precision-oriented comparison, but it misses more of the measured target. The recommendation is to present both models as different tradeoffs rather than treating one as universally best.

### Objective 3: Threshold, Lift, and Cost-Sensitive Review

**Written plan developed before execution**

Review threshold behavior and lift to understand how model decisions change when the cutoff changes. Focus on recall, precision, predicted positive rate, and lift in top-ranked groups. Keep the interpretation aggregate and avoid individual decision language.

**Evidence of execution with annotated outputs**

Evidence files:

- `data/processed/nhis_objective1_threshold_review.csv`
- `data/processed/nhis_objective3_threshold_review.csv`
- `data/processed/nhis_objective3_lift_cost_sensitive_results.csv`

Annotated outputs:

| Output | What it shows | Annotation |
|---|---|---|
| Threshold 0.10 | Recall 0.9934, precision 0.0842, predicted positive rate 0.7512 | Very sensitive but flags many rows |
| Threshold 0.50 | Recall 0.7293, precision 0.2442, predicted positive rate 0.1901 | More selective, with lower recall than low thresholds |
| `gradient_boosting_weighted_loss` | Lift top 10 percent 5.3893 | Strong concentration in the highest-ranked group |
| `random_forest_balanced` | Lift top 20 percent 3.7118 | Strong top-ranked concentration with strong ROC AUC |

**Conclusion and recommendation**

Objective 3 should be presented as a threshold and ranking review, not as a single final cutoff. Lower thresholds may capture more measured barriers but increase false positives. Lift results support using top-ranked groups for aggregate review, planning, and discussion, not individual decisions.

## Part II: MEPS Regression and Cost-Burden Workflow

### Objective 1: Model Comparison and Feature Importance

**Written plan developed before execution**

Compare regression models for total healthcare spending using dollar-scale error metrics. Because spending is skewed, review MAE, RMSE, R-squared, high-cost MAE, and feature effects or importance.

**Evidence of execution with annotated outputs**

Evidence files:

- `data/processed/meps_objective1_model_comparison_results.csv`
- `data/processed/meps_objective1_feature_importance.csv`

Annotated outputs:

| Output | What it shows | Annotation |
|---|---|---|
| `gradient_boosting` baseline adult | MAE 9,381.74 | Lowest saved Objective 1 MAE |
| `linear_regression` baseline adult | R2 0.1569 and high-cost MAE 39,562.92 | Stronger R-squared and high-cost MAE than several flexible models |
| Top feature effect | `categorical__chronic_condition_count_7`, absolute coefficient 19,844.06 | Large saved coefficient in the interpretable feature output |
| Insurance feature effect | `categorical__INSC1231_2`, absolute coefficient 8,196.44 | Insurance coverage appears in the saved feature output |

**Conclusion and recommendation**

The Objective 1 recommendation is to present the gradient boosting baseline as strongest on MAE while also showing the linear model as a useful benchmark. Feature importance and coefficients should be described as model behavior, not causal evidence.

### Objective 2: Interpretable Model Review

**Written plan developed before execution**

Review interpretable regression models that are easier to explain than flexible tree-based models. Compare MAE, RMSE, R-squared, and high-cost MAE.

**Evidence of execution with annotated outputs**

Evidence file: `data/processed/meps_objective2_interpretable_model_results.csv`

Key saved results:

| Model | Notable saved output | Annotation |
|---|---|---|
| `lasso_regression` | MAE 9,516.63, R2 0.1571 | Lowest MAE among saved interpretable models |
| `ridge_regression` | MAE 9,525.44, R2 0.1570 | Similar performance to lasso |
| `linear_regression` | High-cost MAE 39,562.92 | Slightly lowest high-cost MAE in this file |
| `shallow_regression_tree` | MAE 9,676.35, R2 0.1189 | More explainable tree structure but weaker error metrics |

**Conclusion and recommendation**

Lasso regression is a reasonable interpretable recommendation by MAE. Linear regression remains useful for high-cost segment comparison. The results should be presented as tradeoffs under a skewed expenditure outcome.

### Objective 3: High-Cost Segment, Predicted-vs-Actual, and Skew-Aware Review

**Written plan developed before execution**

Because spending is skewed, inspect model behavior in high-cost segments and compare robust or log-transformed results. Review whether high-ranked predicted groups align with actual spending groups.

**Evidence of execution with annotated outputs**

Evidence files:

- `data/processed/meps_objective1_high_cost_segment_review.csv`
- `data/processed/meps_objective3_high_cost_segment_review.csv`
- `data/processed/meps_objective1_predicted_actual_quintile.csv`
- `data/processed/meps_objective3_robust_skew_aware_results.csv`

Annotated outputs:

| Output | What it shows | Annotation |
|---|---|---|
| Objective 1 top 10 percent segment | Threshold 24,412, n 379, MAE 39,562.92 | Error is much larger among high-cost adults |
| Objective 1 top 30 percent segment | Threshold 6,756, n 1,135, MAE 18,132.19 | Error decreases as the segment broadens |
| Predicted-vs-actual quintile table | Q1/Q1 count 383 and Q5/Q5 count 377 | Higher counts on the diagonal suggest useful ranking behavior |
| `gradient_boosting_log1p` | Dollar MAE 7,812.58 and capture rate top 20 percent 0.4822 | Strong saved robust/skew-aware result |

**Conclusion and recommendation**

The robust/skew-aware review supports presenting `gradient_boosting_log1p` as a strong Objective 3 result by dollar MAE and top-20 capture rate. The high-cost segment outputs show why ordinary regression metrics need careful interpretation. These outputs are review tools and should not be used to label individual people by need or financial hardship.

