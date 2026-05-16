import streamlit as st


def apply_page_style() -> None:
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 2.25rem;
            padding-bottom: 3.5rem;
            max-width: 1180px;
        }
        body, p, li, .stMarkdown, [data-testid="stMarkdownContainer"] {
            font-size: 1.06rem;
            line-height: 1.65;
        }
        h1, h2, h3 {
            letter-spacing: 0;
        }
        h1 {
            margin-bottom: 0.25rem;
        }
        h2, h3 {
            margin-top: 1.25rem;
        }
        [data-testid="stMetric"] {
            background: #172033;
            border: 1px solid #3b82f6;
            border-radius: 8px;
            padding: 0.75rem 1rem;
            color: #f8fafc;
        }
        [data-testid="stMetric"] label,
        [data-testid="stMetric"] [data-testid="stMetricValue"],
        [data-testid="stMetric"] [data-testid="stMetricDelta"] {
            color: #f8fafc;
        }
        .section-gap {
            margin-top: 1.6rem;
        }
        .summary-card {
            min-height: 178px;
            padding: 1rem 1.05rem;
            border-radius: 8px;
            border: 1px solid #5eead4;
            background: linear-gradient(180deg, #172033 0%, #111827 100%);
            color: #f8fafc;
            box-shadow: 0 1px 0 rgba(255, 255, 255, 0.08) inset;
        }
        .summary-card .label {
            margin: 0 0 0.4rem 0;
            color: #bae6fd;
            font-size: 0.9rem;
            line-height: 1.25;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }
        .summary-card .value {
            margin: 0 0 0.55rem 0;
            color: #ffffff;
            font-size: 2rem;
            line-height: 1.1;
            font-weight: 800;
        }
        .summary-card .body {
            margin: 0;
            color: #dbeafe;
            font-size: 0.98rem;
            line-height: 1.45;
        }
        .chart-caption {
            margin-top: -0.5rem;
            margin-bottom: 1.2rem;
            color: #cbd5e1;
            font-size: 0.98rem;
            line-height: 1.5;
        }
        [data-testid="stCaptionContainer"] {
            font-size: 1rem;
            color: #cbd5e1;
        }
        [data-testid="stDataFrame"] {
            border: 1px solid #334155;
            border-radius: 8px;
        }
        .callout {
            margin: 1rem 0 1.25rem 0;
            padding: 1rem 1.1rem;
            border-radius: 8px;
            border: 1px solid #38bdf8;
            background: #0f2438;
            color: #e0f2fe;
        }
        .callout strong {
            color: #ffffff;
        }
        .caution {
            margin: 0.75rem 0 1.25rem 0;
            padding: 0.9rem 1rem;
            border-radius: 8px;
            border: 1px solid #fbbf24;
            background: #2a2111;
            color: #fef3c7;
        }
        .small-note {
            color: #cbd5e1;
            font-size: 0.92rem;
            line-height: 1.45;
            margin-top: -0.25rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str, body: str) -> str:
    return f"""
<div class="summary-card">
  <p class="label">{label}</p>
  <p class="value">{value}</p>
  <p class="body">{body}</p>
</div>
"""


def chart_caption(text: str) -> None:
    st.markdown(f'<div class="chart-caption">{text}</div>', unsafe_allow_html=True)


def callout(title: str, text: str) -> None:
    st.markdown(f'<div class="callout"><strong>{title}</strong><br>{text}</div>', unsafe_allow_html=True)


def caution_note(text: str) -> None:
    st.markdown(f'<div class="caution">{text}</div>', unsafe_allow_html=True)


def small_note(text: str) -> None:
    st.markdown(f'<div class="small-note">{text}</div>', unsafe_allow_html=True)


def home_intro() -> str:
    return """
An interactive workspace for exploring public-use survey outputs from NHIS and MEPS.
The app connects reported access barriers, affordability pressure, mental health cost barriers,
healthcare spending, high-cost segments, and model behavior in one place.

It is meant to be readable for people who want the story in plain language and useful for
reviewers who want to trace results back to the saved CSV artifacts. The app reads existing
outputs only; it does not retrain models or rewrite project data.
"""


def missing_data_note(path: str) -> str:
    return (
        f"`{path}` was not found or could not be read. "
        "The app is built to keep running when an expected file is missing; add the processed CSV and refresh the page."
    )


def ethics_sections() -> list[tuple[str, str]]:
    return [
        (
            "Public-use survey data",
            """
This project uses public-use survey files and processed summaries. Those files are designed to reduce disclosure risk,
but they still describe real people's experiences. The safest reading is aggregate: patterns across groups, with extra
care when a group has a small raw sample count.
""",
        ),
        (
            "Privacy",
            """
This app does not use names, addresses, or direct identifiers. It should not be extended with identifiable health data
without a separate privacy, security, and governance review. Screenshots and exports should favor summarized results
over row-level records whenever possible.
""",
        ),
        (
            "Survey weights",
            """
Survey weights help estimates better reflect the population represented by the survey design. Weighted and raw rates can
differ, so the weighted value is the better starting point for population-level interpretation. Raw counts still matter
because they show how much sample support sits behind a group estimate.
""",
        ),
        (
            "Correlation is not causation",
            """
The charts and models describe associations in survey data. They do not prove that one characteristic caused a cost
barrier. Policy, geography, insurance design, health status, income, and response patterns can all be entangled.
""",
        ),
        (
            "Model limitations",
            """
Predictive models reflect the variables, target definition, sample design, and modeling choices used to create them.
Strong aggregate metrics do not mean the model is reliable for every subgroup. Threshold choices involve tradeoffs:
a lower threshold may catch more measured barriers, while also flagging more records that do not have the measured outcome.
""",
        ),
        (
            "No individual decisions",
            """
The predictions and feature rankings in this project should not be used to make eligibility, care, coverage, pricing,
or outreach decisions about individual people. Treat them as planning and research tools that can guide questions for
human review, resource allocation analysis, and future validation.
""",
        ),
    ]
