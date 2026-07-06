import streamlit as st
import plotly.express as px
from utils.data_utils import get_active_df, infer_column_types, detect_business_columns

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
df = get_active_df()  # stops automatically if no df in session_state

st.title("📊 Business Dashboard")

types = infer_column_types(df)
detected = detect_business_columns(df)

from utils.theme import apply_theme, info_card
apply_theme()  # add this near the top, after st.set_page_config

# ... (keep existing KPI + trend + breakdown code) ...

st.divider()
st.subheader("📦 Distribution Analysis")
info_card("Histograms show how a numeric value is spread out — useful for spotting outliers or typical ranges.")

if types["numeric"]:
    dist_col = st.selectbox("Choose a numeric column", types["numeric"], key="dist_col")
    fig_hist = px.histogram(df, x=dist_col, nbins=30, marginal="box", title=f"Distribution of {dist_col}")
    st.plotly_chart(fig_hist, use_container_width=True)

st.divider()
st.subheader("🥧 Category Share (Donut Chart)")
if types["categorical"]:
    pie_col = st.selectbox("Choose a category column", types["categorical"], key="pie_col")
    pie_data = df[pie_col].value_counts().head(10).reset_index()
    pie_data.columns = [pie_col, "count"]
    fig_donut = px.pie(pie_data, names=pie_col, values="count", hole=0.45, title=f"Share by {pie_col}")
    st.plotly_chart(fig_donut, use_container_width=True)

st.divider()
st.subheader("🔥 Correlation Heatmap")
info_card("Shows how strongly numeric columns move together. Closer to 1 or -1 = stronger relationship.")
if len(types["numeric"]) >= 2:
    corr = df[types["numeric"]].corr()
    fig_corr = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu_r", title="Correlation Matrix")
    st.plotly_chart(fig_corr, use_container_width=True)
else:
    st.info("Need at least 2 numeric columns for a correlation heatmap.")

# --- KPI row ---
st.subheader("Key Metrics")
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Records", f"{df.shape[0]:,}")

if detected["revenue"]:
    total_rev = df[detected["revenue"]].sum()
    k2.metric(f"Total {detected['revenue']}", f"{total_rev:,.2f}")
else:
    k2.metric("Total Revenue", "N/A")

if detected["profit"]:
    total_profit = df[detected["profit"]].sum()
    k3.metric(f"Total {detected['profit']}", f"{total_profit:,.2f}")
elif detected["cost"] and detected["revenue"]:
    est_profit = df[detected["revenue"]].sum() - df[detected["cost"]].sum()
    k3.metric("Estimated Profit", f"{est_profit:,.2f}")
else:
    k3.metric("Profit", "N/A")

if detected["customer"]:
    k4.metric("Unique Customers", df[detected["customer"]].nunique())
else:
    k4.metric("Columns", df.shape[1])

st.divider()

# --- Trend over time ---
if detected["date"] and detected["revenue"]:
    st.subheader(f"{detected['revenue']} Over Time")
    trend_df = df[[detected["date"], detected["revenue"]]].dropna()
    trend_df[detected["date"]] = trend_df[detected["date"]]
    trend_agg = trend_df.groupby(detected["date"], as_index=False)[detected["revenue"]].sum()
    fig = px.line(trend_agg, x=detected["date"], y=detected["revenue"], markers=True)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Add a date column and a revenue-like column for trend charts.")

# --- Category breakdown ---
col1, col2 = st.columns(2)
with col1:
    if detected["product"] and detected["revenue"]:
        st.subheader(f"{detected['revenue']} by {detected['product']}")
        agg = df.groupby(detected["product"], as_index=False)[detected["revenue"]].sum().sort_values(
            detected["revenue"], ascending=False
        ).head(15)
        fig2 = px.bar(agg, x=detected["product"], y=detected["revenue"])
        st.plotly_chart(fig2, use_container_width=True)
    elif types["categorical"]:
        cat_col = types["categorical"][0]
        st.subheader(f"Record Count by {cat_col}")
        agg = df[cat_col].value_counts().head(15).reset_index()
        agg.columns = [cat_col, "count"]
        fig2 = px.bar(agg, x=cat_col, y="count")
        st.plotly_chart(fig2, use_container_width=True)

with col2:
    if detected["region"] and detected["revenue"]:
        st.subheader(f"{detected['revenue']} by {detected['region']}")
        agg = df.groupby(detected["region"], as_index=False)[detected["revenue"]].sum().sort_values(
            detected["revenue"], ascending=False
        ).head(15)
        fig3 = px.pie(agg, names=detected["region"], values=detected["revenue"])
        st.plotly_chart(fig3, use_container_width=True)
    elif len(types["categorical"]) > 1:
        cat_col = types["categorical"][1]
        agg = df[cat_col].value_counts().head(15).reset_index()
        agg.columns = [cat_col, "count"]
        st.subheader(f"Record Count by {cat_col}")
        fig3 = px.pie(agg, names=cat_col, values="count")
        st.plotly_chart(fig3, use_container_width=True)

st.divider()

st.subheader("Custom Explorer")
c1, c2, c3 = st.columns(3)
x_axis = c1.selectbox("X-axis", options=df.columns, index=0)
num_cols = types["numeric"] or list(df.columns)
y_axis = c2.selectbox("Y-axis (numeric)", options=num_cols, index=0)
chart_type = c3.selectbox("Chart type", ["Bar", "Line", "Scatter", "Box"])

try:
    if chart_type == "Bar":
        fig = px.bar(df, x=x_axis, y=y_axis)
    elif chart_type == "Line":
        fig = px.line(df, x=x_axis, y=y_axis)
    elif chart_type == "Scatter":
        fig = px.scatter(df, x=x_axis, y=y_axis)
    else:
        fig = px.box(df, x=x_axis, y=y_axis)
    st.plotly_chart(fig, use_container_width=True)
except Exception as e:
    st.error(f"Couldn't render chart with selected columns: {e}")