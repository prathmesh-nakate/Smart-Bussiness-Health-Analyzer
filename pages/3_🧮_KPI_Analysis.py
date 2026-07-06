import streamlit as st
import pandas as pd
from utils.data_utils import (
    get_active_df,
    infer_column_types,
    detect_business_columns,
)

st.set_page_config(
    page_title="KPI Analysis",
    page_icon="🧮",
    layout="wide",
)

# Load active dataset
df = get_active_df()

st.title("🧮 KPI Analysis")

# Detect column types
types = infer_column_types(df)
detected = detect_business_columns(df)

# ==========================
# Summary Statistics
# ==========================

st.subheader("📊 Summary Statistics (Numeric Columns)")

if types["numeric"]:
    st.dataframe(
        df[types["numeric"]].describe().T,
        use_container_width=True,
    )
else:
    st.info("No numeric columns detected.")

st.divider()

# ==========================
# Custom KPI Builder
# ==========================

st.subheader("📈 Custom KPI Builder")

c1, c2, c3 = st.columns(3)

metric_col = c1.selectbox(
    "Metric column",
    options=types["numeric"] if types["numeric"] else df.columns.tolist(),
)

group_options = ["None"] + types["categorical"]

group_col = c2.selectbox(
    "Group by (optional)",
    options=group_options,
)

agg_func = c3.selectbox(
    "Aggregation",
    ["sum", "mean", "median", "max", "min", "count"],
)

if group_col == "None":
    value = getattr(df[metric_col], agg_func)()

    if isinstance(value, (int, float)):
        st.metric(
            f"{agg_func.title()} of {metric_col}",
            f"{value:,.2f}",
        )
    else:
        st.metric(
            f"{agg_func.title()} of {metric_col}",
            str(value),
        )

else:
    grouped = (
        df.groupby(group_col)[metric_col]
        .agg(agg_func)
        .sort_values(ascending=False)
        .reset_index()
    )

    st.dataframe(grouped, use_container_width=True)

    st.bar_chart(
        grouped.set_index(group_col)
    )

st.divider()

# ==========================
# Period-over-Period Analysis
# ==========================

st.subheader("📅 Period-over-Period Comparison")

if detected["date"]:

    date_col = detected["date"]

    work = df.copy()

    work[date_col] = pd.to_datetime(
        work[date_col],
        errors="coerce",
    )

    work = work.dropna(subset=[date_col])

    if not work.empty and types["numeric"]:

        metric2 = st.selectbox(
            "Metric to compare",
            options=types["numeric"],
            key="period_metric",
        )

        frequency = st.selectbox(
            "Frequency",
            options=[
                "Daily",
                "Weekly",
                "Monthly",
                "Quarterly",
                "Yearly",
            ],
            index=2,
        )

        freq_map = {
            "Daily": "D",
            "Weekly": "W",
            "Monthly": "ME",     # Pandas 3.x
            "Quarterly": "QE",   # Pandas 3.x
            "Yearly": "YE",      # Pandas 3.x
        }

        freq = freq_map[frequency]

        ts = (
            work.set_index(date_col)[metric2]
            .resample(freq)
            .sum()
            .reset_index()
        )

        ts["Previous Period"] = ts[metric2].shift(1)

        ts["Change"] = (
            ts[metric2]
            - ts["Previous Period"]
        )

        ts["% Change"] = (
            ts[metric2]
            .pct_change()
            .fillna(0)
            * 100
        )

        st.dataframe(
            ts,
            use_container_width=True,
        )

        st.line_chart(
            ts.set_index(date_col)[metric2]
        )

    else:
        st.info("No numeric columns available.")

else:
    st.info(
        "No date column detected. Period comparison is unavailable."
    )