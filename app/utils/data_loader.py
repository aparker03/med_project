from pathlib import Path

import pandas as pd
import streamlit as st


REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"
INTERIM_DIR = DATA_DIR / "interim"


def _safe_csv_path(filename: str) -> Path:
    return PROCESSED_DIR / filename


@st.cache_data(show_spinner=False)
def load_csv(filename: str) -> pd.DataFrame | None:
    path = _safe_csv_path(filename)
    if not path.exists():
        return None
    try:
        return pd.read_csv(path)
    except Exception:
        return None


@st.cache_data(show_spinner=False)
def load_csv_from_path(path: Path | str) -> pd.DataFrame | None:
    path = Path(path)
    if not path.exists():
        return None
    try:
        return pd.read_csv(path)
    except Exception:
        return None


@st.cache_data(show_spinner=False)
def list_processed_files() -> list[str]:
    if not PROCESSED_DIR.exists():
        return []
    return sorted(path.name for path in PROCESSED_DIR.glob("*.csv"))


@st.cache_data(show_spinner=False)
def list_weighted_rate_files() -> list[str]:
    if not PROCESSED_DIR.exists():
        return []
    return sorted(path.name for path in PROCESSED_DIR.glob("nhis_weighted_rate_by_*.csv"))


@st.cache_data(show_spinner=False)
def list_csv_files(relative_dirs: list[str]) -> list[Path]:
    files: list[Path] = []
    for relative_dir in relative_dirs:
        path = REPO_ROOT / relative_dir
        if path.exists():
            files.extend(sorted(path.glob("*.csv")))
    return files
