from __future__ import annotations

import re

import pandas as pd


IMPORTANT_VARIABLES = {
    "mental_health_cost_barrier": "Mental health care delayed or not received because of cost",
    "AGEP_A": "Age",
    "SEX_A": "Sex",
    "HISPALLP_A": "Hispanic ethnicity and race group",
    "RACEALLP_A": "Race group",
    "EDUCP_A": "Education level",
    "REGION": "U.S. region",
    "URBRRL": "Urban-rural classification",
    "POVRATTC_A": "Family income as a ratio of the federal poverty level",
    "poverty_group_imp": "Family income group",
    "PHSTAT_A": "Self-rated health status",
    "LSATIS4_A": "Life satisfaction",
    "ANXEV_A": "Ever told had anxiety",
    "DEPEV_A": "Ever told had depression",
    "DISAB3_A": "Disability status",
    "NOTCOV_A": "Uninsured status",
    "MEDICARE_A": "Medicare coverage",
    "MEDICAID_A": "Medicaid coverage",
    "PRIVATE_A": "Private insurance coverage",
    "PAYBLL12M_A": "Problems paying medical bills in the past 12 months",
    "PAYWORRY_A": "Worry about paying medical bills",
    "MEDDL12M_A": "Delayed medical care because of cost",
    "MEDNG12M_A": "Needed but did not get medical care because of cost",
    "USUALPL_A": "Has a usual place for care",
    "LASTDR_A": "Time since last saw a doctor or health professional",
    "insurance_hierarchy_combined": "Combined insurance coverage category",
    "chronic_condition_count": "Chronic condition count",
    "mental_health_history_count": "Mental health history count",
    "functioning_difficulty_count": "Number of functioning difficulties",
    "affordability_pressure_count": "Number of affordability pressures",
    "weighted_rate": "Survey-weighted rate",
    "unweighted_rate": "Raw sample rate",
    "unweighted_n": "Raw sample count",
    "model": "Model",
    "version": "Model version",
    "objective": "Analysis objective",
    "n_features": "Number of features",
    "accuracy": "Accuracy",
    "roc_auc": "ROC AUC",
    "average_precision": "Average precision",
    "precision": "Precision",
    "recall": "Recall",
    "f1": "F1 score",
    "threshold": "Threshold",
    "precision_050": "Precision at 0.50 threshold",
    "recall_050": "Recall at 0.50 threshold",
    "f1_050": "F1 at 0.50 threshold",
    "predicted_positive_rate": "Share flagged by model",
    "lift_top_10pct": "Lift in top 10%",
    "lift_top_20pct": "Lift in top 20%",
    "lift_top_30pct": "Lift in top 30%",
    "TOTEXP23": "Total healthcare spending",
    "TOTEXP23_log1p": "Total healthcare spending, log scale",
    "AGE23X": "Age",
    "REGION23": "U.S. region",
    "POVCAT23": "Family income category",
    "INSC1231": "Insurance coverage",
    "HAVEUS42": "Usual source of care",
    "DLAYCA42": "Delayed medical care",
    "AFRDCA42": "Could not afford medical care",
    "DLAYPM42": "Delayed prescription medicines",
    "AFRDPM42": "Could not afford prescription medicines",
    "DLAYDN42": "Delayed dental care",
    "AFRDDN42": "Could not afford dental care",
    "access_barrier_count": "Access barrier count",
    "physical_difficulty_count": "Physical difficulty count",
    "limitation_indicator_count": "Limitation indicator count",
    "mental_health_screen_count": "Mental health screen count",
    "MAE": "Mean absolute error",
    "RMSE": "Root mean squared error",
    "R2": "R-squared",
    "high_cost_MAE": "High-cost segment mean absolute error",
    "log_MAE": "Log-scale mean absolute error",
    "log_RMSE": "Log-scale root mean squared error",
    "dollar_MAE": "Dollar-scale mean absolute error",
    "dollar_RMSE": "Dollar-scale root mean squared error",
    "dollar_R2": "Dollar-scale R-squared",
    "capture_rate": "Capture rate",
    "capture_rate_top20pct": "Capture rate in top 20%",
    "segment": "High-cost segment",
    "Actual quintile": "Actual spending group",
    "predicted_spending_group": "Predicted spending group",
    "actual_spending_group": "Actual spending group",
    "skew_aware_model": "Skew-aware model",
    "robust_model_review": "Robust model review",
}


VARIABLE_DETAILS = {
    "mental_health_cost_barrier": {
        "source": "nhis_model_ready_v1.csv",
        "meaning": "Outcome used in this app for whether mental health care was delayed or not received because of cost.",
        "notes": "Interpret as a measured survey outcome, not a complete measure of unmet need.",
    },
    "AGEP_A": {
        "source": "nhis_model_ready_v1.csv",
        "meaning": "Respondent age in years.",
        "notes": "Age patterns can reflect many social, health, and coverage differences at once.",
    },
    "SEX_A": {
        "source": "nhis_model_ready_v1.csv; nhis_weighted_rate_by_SEX_A.csv",
        "meaning": "Sex category available in the public-use NHIS file.",
        "notes": "Use the survey categories as coded; they may not capture every person's identity.",
    },
    "REGION": {
        "source": "nhis_model_ready_v1.csv; nhis_weighted_rate_by_REGION.csv",
        "meaning": "Broad U.S. Census region.",
        "notes": "Regional summaries can hide important state and local differences.",
    },
    "poverty_group_imp": {
        "source": "nhis_weighted_rate_by_poverty_group_imp.csv",
        "meaning": "Family income grouped relative to the federal poverty level.",
        "notes": "Income is imputed in NHIS; treat fine-grained comparisons cautiously.",
    },
    "DISAB3_A": {
        "source": "nhis_model_ready_v1.csv; nhis_weighted_rate_by_DISAB3_A.csv",
        "meaning": "Whether the respondent is classified as having a disability in the survey variable used here.",
        "notes": "A single survey indicator cannot capture every dimension of disability or access need.",
    },
    "affordability_pressure_count": {
        "source": "nhis_model_ready_v1.csv; nhis_weighted_rate_by_affordability_pressure_count.csv",
        "meaning": "Count of selected cost and affordability pressure indicators.",
        "notes": "Higher counts mean more recorded pressures, not a dollar estimate of burden.",
    },
    "functioning_difficulty_count": {
        "source": "nhis_model_ready_v1.csv; nhis_weighted_rate_by_functioning_difficulty_count.csv",
        "meaning": "Count of selected functioning difficulty indicators.",
        "notes": "This is a compact count built for analysis; review underlying items for detailed interpretation.",
    },
    "mental_health_history_count": {
        "source": "nhis_model_ready_v1.csv; nhis_weighted_rate_by_mental_health_history_count.csv",
        "meaning": "Count of selected mental health history indicators.",
        "notes": "This summarizes survey indicators and should not be read as a clinical diagnosis.",
    },
    "chronic_condition_count": {
        "source": "nhis_model_ready_v1.csv",
        "meaning": "Count of selected chronic condition indicators.",
        "notes": "A count is useful for broad adjustment, but it does not measure severity.",
    },
    "weighted_rate": {
        "source": "nhis_weighted_rate_by_*.csv",
        "meaning": "Estimated population rate after applying survey weights.",
        "notes": "Use with the unweighted count to judge whether a group has enough sample support.",
    },
    "unweighted_rate": {
        "source": "nhis_weighted_rate_by_*.csv",
        "meaning": "Raw rate in the analytic sample before survey weighting.",
        "notes": "Useful as a check, but not the preferred population estimate.",
    },
    "unweighted_n": {
        "source": "nhis_weighted_rate_by_*.csv",
        "meaning": "Number of sample records in the group before weighting.",
        "notes": "Small counts can make rates unstable.",
    },
    "roc_auc": {
        "source": "nhis_objective*_*.csv",
        "meaning": "How well the model ranks positive cases above negative cases across thresholds.",
        "notes": "A high value does not guarantee good subgroup performance or individual reliability.",
    },
    "average_precision": {
        "source": "nhis_objective*_*.csv",
        "meaning": "Precision-recall summary that is often useful when the outcome is uncommon.",
        "notes": "Compare alongside recall and threshold behavior.",
    },
    "precision": {
        "source": "nhis_objective*_*.csv; nhis_objective*_threshold_review.csv",
        "meaning": "Among records flagged by the model, the share with the measured outcome.",
        "notes": "Precision changes when the threshold changes.",
    },
    "recall": {
        "source": "nhis_objective*_*.csv; nhis_objective*_threshold_review.csv",
        "meaning": "Among records with the measured outcome, the share flagged by the model.",
        "notes": "Higher recall often comes with more false positives.",
    },
    "f1": {
        "source": "nhis_objective*_*.csv; nhis_objective*_threshold_review.csv",
        "meaning": "Single summary combining precision and recall.",
        "notes": "Useful for comparison, but it hides the practical threshold tradeoff.",
    },
    "predicted_positive_rate": {
        "source": "nhis_objective*_threshold_review.csv",
        "meaning": "Share of records the model would flag at a given threshold.",
        "notes": "This is a planning metric, not a recommendation for individual decisions.",
    },
    "TOTEXP23": {
        "source": "meps_model_ready_v1.csv; meps_model_ready_v1_with_saq.csv",
        "meaning": "Total healthcare spending recorded in the MEPS modeling file.",
        "notes": "Spending outcomes are usually skewed, with many low-cost rows and a smaller number of very high-cost rows.",
    },
    "TOTEXP23_log1p": {
        "source": "meps_model_ready_v1.csv; meps_model_ready_v1_with_saq.csv",
        "meaning": "A log-transformed version of total healthcare spending used for skew-aware modeling.",
        "notes": "Log-scale metrics are useful for modeling skewed spending, but they are not dollar amounts.",
    },
    "INSC1231": {
        "source": "meps_model_ready_v1.csv; meps_model_ready_v1_with_saq.csv",
        "meaning": "Insurance coverage concept used in MEPS modeling.",
        "notes": "Use the MEPS codebook for exact category definitions.",
    },
    "HAVEUS42": {
        "source": "meps_model_ready_v1.csv; meps_model_ready_v1_with_saq.csv",
        "meaning": "Usual source of care concept used as a healthcare access and utilization indicator.",
        "notes": "This is one access-related survey measure, not a complete measure of healthcare use.",
    },
    "access_barrier_count": {
        "source": "meps_model_ready_v1.csv; meps_model_ready_v1_with_saq.csv",
        "meaning": "Count of selected access and affordability barrier indicators.",
        "notes": "The count summarizes selected survey fields and does not measure individual hardship directly.",
    },
    "high_cost_segment": {
        "source": "meps_objective1_high_cost_segment_review.csv; meps_objective3_high_cost_segment_review.csv",
        "meaning": "A review group at the upper end of the healthcare spending distribution, such as the top 10%, 20%, or 30%.",
        "notes": "High-cost segment review is descriptive and should not be used to label individual people.",
    },
    "predicted_spending_group": {
        "source": "meps_objective1_predicted_actual_quintile.csv",
        "meaning": "A file-dependent predicted spending group, shown as a quintile in the saved review output.",
        "notes": "Use this to inspect ranking behavior, not to assign individual financial status.",
    },
    "actual_spending_group": {
        "source": "meps_objective1_predicted_actual_quintile.csv",
        "meaning": "A file-dependent actual spending group, shown as a quintile in the saved review output.",
        "notes": "Actual groups are based on observed spending in the saved evaluation output.",
    },
    "skew_aware_model": {
        "source": "meps_objective3_robust_skew_aware_results.csv",
        "meaning": "A model review approach that accounts for the skewed shape of healthcare spending outcomes.",
        "notes": "Skew-aware results should be read alongside dollar-scale and log-scale metrics.",
    },
    "robust_model_review": {
        "source": "meps_objective3_robust_skew_aware_results.csv",
        "meaning": "Saved checks for model behavior under a skewed-expenditure framing.",
        "notes": "Robust review supports interpretation, but it does not make the model appropriate for individual decisions.",
    },
    "out_of_pocket_spending": {
        "source": "MEPS processed outputs, file-dependent",
        "meaning": "Out-of-pocket healthcare spending concept when present in MEPS outputs.",
        "notes": "Column names can vary by MEPS processing step; confirm exact fields in the source file.",
    },
    "healthcare_utilization": {
        "source": "MEPS processed outputs, file-dependent",
        "meaning": "Healthcare use concepts such as usual source of care, delayed care, or service-use indicators.",
        "notes": "Use the MEPS codebook for exact survey item definitions.",
    },
}


GROUP_LABELS = {
    "SEX_A": {"1": "Male", "1.0": "Male", "2": "Female", "2.0": "Female"},
    "REGION": {"1": "Northeast", "2": "Midwest", "3": "South", "4": "West"},
    "DISAB3_A": {"1": "Has a disability", "1.0": "Has a disability", "2": "No disability", "2.0": "No disability"},
    "affordability_pressure_count": {
        "0": "0 affordability pressures",
        "1": "1 affordability pressure",
        "2": "2 affordability pressures",
        "3": "3 affordability pressures",
        "4": "4 affordability pressures",
    },
    "mental_health_history_count": {
        "0": "0 mental health history indicators",
        "1": "1 mental health history indicator",
        "2": "2 mental health history indicators",
    },
    "functioning_difficulty_count": {
        "0": "0 functioning difficulty indicators",
        "1": "1 functioning difficulty indicator",
        "2": "2 functioning difficulty indicators",
        "3": "3 functioning difficulty indicators",
        "4": "4 functioning difficulty indicators",
        "5": "5 functioning difficulty indicators",
        "6": "6 functioning difficulty indicators",
    },
}


GROUP_SORT_ORDER = {
    "poverty_group_imp": [
        "Poor: below 100% FPL",
        "Near poor: 100% to <125% FPL",
        "Low income: 125% to <200% FPL",
        "Middle income: 200% to <400% FPL",
        "High income: 400%+ FPL",
    ],
    "REGION": ["Northeast", "Midwest", "South", "West"],
    "SEX_A": ["Male", "Female"],
    "DISAB3_A": ["Has a disability", "No disability"],
}


GROUP_INTERPRETATION = {
    "poverty_group_imp": (
        "This view compares mental health cost-barrier rates across family income groups. "
        "Use the pattern as a descriptive estimate; income is tied to many other access and coverage factors."
    ),
    "REGION": (
        "This view compares broad U.S. regions. Regional estimates can point to geographic patterns, "
        "but they do not explain the policy, provider, or local conditions behind those differences."
    ),
    "SEX_A": (
        "This view compares the sex categories available in the public-use survey output. "
        "The rates are descriptive and should be read alongside the limits of the survey categories."
    ),
    "DISAB3_A": (
        "This view compares respondents by disability status as coded in the saved output. "
        "A single summary variable cannot capture the full range of disability experiences or access barriers."
    ),
    "affordability_pressure_count": (
        "This view groups rows by how many affordability-pressure indicators were recorded. "
        "Higher counts describe more recorded pressures, not the cause of a mental health cost barrier."
    ),
    "functioning_difficulty_count": (
        "This view groups rows by the number of functioning difficulty indicators. "
        "It can help orient the analysis, but it should not be read as a measure of need or severity."
    ),
    "mental_health_history_count": (
        "This view groups rows by the count of mental health history indicators. "
        "The count summarizes survey responses and is not a clinical assessment."
    ),
}


def friendly_label(name: str) -> str:
    if name in IMPORTANT_VARIABLES:
        return IMPORTANT_VARIABLES[name]
    feature_label = feature_friendly_label(str(name))
    if feature_label != str(name):
        return feature_label
    cleaned = re.sub(r"^(categorical|numeric)__", "", str(name))
    cleaned = re.sub(r"_+", " ", cleaned).strip()
    return cleaned[:1].upper() + cleaned[1:]


def feature_friendly_label(name: str) -> str:
    cleaned = re.sub(r"^(categorical|numeric)__", "", str(name))
    for variable in sorted(IMPORTANT_VARIABLES, key=len, reverse=True):
        prefix = f"{variable}_"
        if cleaned.startswith(prefix):
            value = cleaned[len(prefix) :]
            value_label = format_group_value(variable, value)
            if value_label != value:
                return f"{IMPORTANT_VARIABLES[variable]}: {value_label}"
            return f"{IMPORTANT_VARIABLES[variable]}: {value}"
    return str(name)


def dataset_label(filename: str) -> str:
    stem = filename.replace("nhis_weighted_rate_by_", "").replace(".csv", "")
    return friendly_label(stem)


def group_key_from_filename(filename: str) -> str:
    return filename.replace("nhis_weighted_rate_by_", "").replace(".csv", "")


def format_group_value(group_key: str, value: object) -> str:
    if pd.isna(value):
        return "Missing"
    value_text = str(value)
    value_text = value_text[:-2] if value_text.endswith(".0") else value_text
    labels = GROUP_LABELS.get(group_key, {})
    return labels.get(str(value), labels.get(value_text, value_text))


def label_group_values(df: pd.DataFrame, filename: str) -> pd.DataFrame:
    group_key = group_key_from_filename(filename)
    labeled = df.copy()
    if "group" in labeled.columns:
        labeled["group_display"] = labeled["group"].apply(lambda value: format_group_value(group_key, value))
    return labeled


def sort_weighted_rate_rows(df: pd.DataFrame, filename: str) -> pd.DataFrame:
    group_key = group_key_from_filename(filename)
    sorted_df = df.copy()

    if "group_display" not in sorted_df.columns:
        return sorted_df

    if group_key in GROUP_SORT_ORDER:
        order = {label: index for index, label in enumerate(GROUP_SORT_ORDER[group_key])}
        sorted_df["_sort_key"] = sorted_df["group_display"].map(order).fillna(len(order))
    elif group_key.endswith("_count") or "count" in group_key:
        sorted_df["_sort_key"] = pd.to_numeric(sorted_df["group"], errors="coerce")
    elif "weighted_rate" in sorted_df.columns:
        sorted_df["_sort_key"] = sorted_df["weighted_rate"]
    else:
        sorted_df["_sort_key"] = sorted_df["group_display"].astype(str)

    return sorted_df.sort_values("_sort_key", kind="stable").drop(columns="_sort_key")


def interpretation_for_group(filename: str) -> str:
    group_key = group_key_from_filename(filename)
    return GROUP_INTERPRETATION.get(
        group_key,
        "This view compares survey-weighted rates across groups in the selected processed output. Read the differences as descriptive patterns.",
    )


def display_columns(df: pd.DataFrame) -> pd.DataFrame:
    return df.rename(columns={col: friendly_label(col) for col in df.columns})


def dictionary_rows(available_columns: list[str] | None = None) -> list[dict[str, str]]:
    variables = list(IMPORTANT_VARIABLES)
    if available_columns:
        for column in available_columns:
            if column not in variables:
                variables.append(column)

    rows = []
    for variable in variables:
        details = VARIABLE_DETAILS.get(variable, {})
        rows.append(
            {
                "Plain-language label": friendly_label(variable),
                "Variable name": variable,
                "Source file or output file": details.get("source", "NHIS processed output or model artifact"),
                "What it means": details.get("meaning", friendly_label(variable)),
                "Notes or caution": details.get("notes", "Use with the survey documentation and project codebook when interpreting."),
            }
        )
    return rows
