"""
Shared data utilities.
Every page calls get_active_df() to read the single source of truth
stored in st.session_state. No page should ever read a CSV from disk
except intentional "download cleaned data" actions.
"""

import pandas as pd
import numpy as np
import streamlit as st


def require_dataset():
    """Stops page execution with a friendly warning if no dataset is loaded."""
    if "df" not in st.session_state or st.session_state["df"] is None:
        st.warning("⚠️ Please upload a dataset first on the **Data Upload** page.")
        st.stop()
    return st.session_state["df"]


def get_active_df() -> pd.DataFrame:
    """Returns the current working dataframe (post any in-session cleaning)."""
    return require_dataset()


def infer_column_types(df: pd.DataFrame) -> dict:
    """Classifies columns into numeric, categorical, datetime, and text."""
    numeric_cols, categorical_cols, datetime_cols, text_cols = [], [], [], []

    for col in df.columns:
        series = df[col]
        if pd.api.types.is_numeric_dtype(series):
            numeric_cols.append(col)
        elif pd.api.types.is_datetime64_any_dtype(series):
            datetime_cols.append(col)
        else:
            # try datetime parse
            sample = series.dropna().astype(str).head(20)
            parsed = pd.to_datetime(sample, errors="coerce", format=None)
            if parsed.notna().mean() > 0.7 and len(sample) > 0:
                datetime_cols.append(col)
            elif series.nunique(dropna=True) <= max(50, int(0.2 * len(series))):
                categorical_cols.append(col)
            else:
                text_cols.append(col)

    return {
        "numeric": numeric_cols,
        "categorical": categorical_cols,
        "datetime": datetime_cols,
        "text": text_cols,
    }


def auto_clean(df: pd.DataFrame) -> pd.DataFrame:
    """Light, safe automatic cleaning applied right after upload."""
    df = df.copy()

    # Strip column names
    df.columns = [str(c).strip() for c in df.columns]

    # Drop fully empty rows/cols
    df = df.dropna(axis=0, how="all")
    df = df.dropna(axis=1, how="all")

    # Try converting obvious date-like columns
    for col in df.columns:
        if df[col].dtype == object:
            lower = col.lower()
            if "date" in lower or "time" in lower:
                converted = pd.to_datetime(df[col], errors="coerce")
                if converted.notna().mean() > 0.5:
                    df[col] = converted

    # Fill numeric NaNs with median, categorical NaNs with mode/"Unknown"
    types = infer_column_types(df)
    for col in types["numeric"]:
        if df[col].isna().any():
            df[col] = df[col].fillna(df[col].median())
    for col in types["categorical"] + types["text"]:
        if df[col].isna().any():
            mode = df[col].mode(dropna=True)
            fill_val = mode.iloc[0] if not mode.empty else "Unknown"
            df[col] = df[col].fillna(fill_val)

    return df


def find_column(df: pd.DataFrame, keywords: list[str]):
    """Best-effort fuzzy match: finds a column whose name contains any keyword."""
    cols_lower = {c: c.lower() for c in df.columns}
    for kw in keywords:
        for col, low in cols_lower.items():
            if kw in low:
                return col
    return None


def detect_business_columns(df: pd.DataFrame) -> dict:
    """Heuristically detects common business columns (revenue, profit, date, etc.)."""
    return {
        "revenue": find_column(df, ["revenue", "sales", "amount", "total_sales", "income"]),
        "profit": find_column(df, ["profit", "margin", "net_income"]),
        "cost": find_column(df, ["cost", "expense", "expenditure"]),
        "date": find_column(df, ["date", "order_date", "transaction_date", "timestamp"]),
        "customer": find_column(df, ["customer", "client", "user_id", "customer_id"]),
        "product": find_column(df, ["product", "item", "sku", "category"]),
        "region": find_column(df, ["region", "state", "country", "location", "city"]),
        "quantity": find_column(df, ["quantity", "qty", "units"]),
    }

def assess_data_quality(df: pd.DataFrame) -> dict:
    """
    Checks whether the uploaded dataset looks 'dirty' and needs cleaning.
    Returns a report used to show a recommendation banner to the student/user.
    """
    issues = []
    total_cells = df.shape[0] * df.shape[1]
    missing_cells = df.isna().sum().sum()
    missing_pct = (missing_cells / total_cells * 100) if total_cells else 0

    duplicate_rows = df.duplicated().sum()

    # Inconsistent text casing/whitespace in object columns
    messy_text_cols = []
    for col in df.select_dtypes(include="object").columns:
        sample = df[col].dropna().astype(str)
        if len(sample) == 0:
            continue
        has_whitespace_issue = (sample != sample.str.strip()).any()
        has_case_issue = sample.nunique() != sample.str.lower().nunique()
        if has_whitespace_issue or has_case_issue:
            messy_text_cols.append(col)

    if missing_pct > 2:
        issues.append(f"{missing_pct:.1f}% of all cells are missing.")
    if duplicate_rows > 0:
        issues.append(f"{duplicate_rows} duplicate rows found.")
    if messy_text_cols:
        issues.append(f"Inconsistent text formatting in: {', '.join(messy_text_cols)}.")

    is_dirty = len(issues) > 0

    return {
        "is_dirty": is_dirty,
        "issues": issues,
        "missing_pct": round(missing_pct, 2),
        "duplicate_rows": int(duplicate_rows),
        "messy_text_cols": messy_text_cols,
    }


def deep_clean(df: pd.DataFrame) -> pd.DataFrame:
    """
    Full cleaning pass — used when the user clicks 'Clean my data'.
    Trims text, fixes casing, removes duplicates, then runs auto_clean().
    """
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    df = df.drop_duplicates()

    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()

    df = auto_clean(df)
    return df