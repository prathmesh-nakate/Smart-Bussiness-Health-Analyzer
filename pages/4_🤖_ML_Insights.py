import streamlit as st
import plotly.express as px
from utils.data_utils import get_active_df, infer_column_types
from utils.ml_utils import run_kmeans, run_anomaly_detection

st.set_page_config(page_title="ML Insights", page_icon="🤖", layout="wide")
df = get_active_df()

st.title("🤖 Machine Learning Insights")
types = infer_column_types(df)
numeric_cols = types["numeric"]

if len(numeric_cols) < 2:
    st.warning("Need at least 2 numeric columns for clustering/anomaly detection.")
    st.stop()

tab1, tab2 = st.tabs(["🔵 Customer / Record Segmentation", "🚨 Anomaly Detection"])

from utils.theme import apply_theme, info_card
from utils.ml_utils import run_kmeans, run_anomaly_detection, linear_regression_trend, random_forest_predict

apply_theme()  # add after set_page_config

tab1, tab2, tab3, tab4 = st.tabs([
    "🔵 Segmentation (K-Means)",
    "🚨 Anomaly Detection",
    "📈 Linear Regression",
    "🌳 Random Forest"
])

with tab3:
    st.subheader("Linear Regression — Relationship Between Two Variables")
    info_card("Linear Regression fits a straight line through your data to show how one variable changes another. Example: how Quantity affects Revenue.")
    c1, c2 = st.columns(2)
    x_col = c1.selectbox("X (input variable)", numeric_cols, key="lr_x")
    y_col = c2.selectbox("Y (variable to predict)", numeric_cols, key="lr_y")

    if x_col != y_col:
        lr_result = linear_regression_trend(df, x_col, y_col)
        if lr_result:
            fig = px.scatter(lr_result["data"], x=x_col, y=y_col, trendline=None,
                              title=f"{y_col} vs {x_col}")
            fig.add_scatter(x=lr_result["data"][x_col], y=lr_result["data"]["predicted"],
                             mode="lines", name="Regression Line")
            st.plotly_chart(fig, use_container_width=True)

            m1, m2, m3 = st.columns(3)
            m1.metric("R² Score (fit quality)", lr_result["r2"])
            m2.metric("Slope", round(lr_result["slope"], 3))
            m3.metric("Intercept", round(lr_result["intercept"], 3))
            st.caption("R² closer to 1 means the line explains the data well; closer to 0 means a weak relationship.")
        else:
            st.info("Not enough valid data points (need at least 5).")
    else:
        st.warning("Choose two different columns.")

with tab4:
    st.subheader("Random Forest — Predict a Business Outcome")
    info_card("Random Forest combines many decision trees to predict a target value and tell you which features matter most. Example: predict Profit from Quantity, Cost, and Region.")
    target = st.selectbox("Target to predict", numeric_cols, key="rf_target")
    features = st.multiselect("Feature columns (inputs)", [c for c in numeric_cols if c != target],
                               default=[c for c in numeric_cols if c != target][:3])

    if features and st.button("Train Random Forest"):
        rf_result = random_forest_predict(df, features, target)
        if rf_result:
            m1, m2 = st.columns(2)
            m1.metric("R² Score", rf_result["r2"])
            m2.metric("Avg. Error (MAE)", rf_result["mae"])

            st.subheader("Which features matter most?")
            fig_imp = px.bar(rf_result["importance"], orientation="h", title="Feature Importance")
            st.plotly_chart(fig_imp, use_container_width=True)
        else:
            st.warning("Need at least 20 complete rows to train a reliable model.")

with tab1:
    st.subheader("KMeans Clustering")
    selected_cols = st.multiselect("Select numeric columns for clustering", numeric_cols, default=numeric_cols[:2])
    k = st.slider("Number of clusters", 2, 8, 3)

    if len(selected_cols) >= 2:
        result, model = run_kmeans(df, selected_cols, k)
        if result is not None:
            fig = px.scatter(
                result, x=selected_cols[0], y=selected_cols[1],
                color=result["cluster"].astype(str),
                title="Cluster Visualization"
            )
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("Cluster Profiles (mean values)")
            st.dataframe(result.groupby("cluster")[selected_cols].mean(), use_container_width=True)

            st.subheader("Cluster Sizes")
            st.bar_chart(result["cluster"].value_counts().sort_index())
        else:
            st.info("Not enough valid data for clustering with current selection.")
    else:
        st.info("Select at least 2 numeric columns.")

with tab2:
    st.subheader("Isolation Forest Anomaly Detection")
    anomaly_cols = st.multiselect("Select numeric columns to scan for anomalies",
                                   numeric_cols, default=numeric_cols[:3], key="anomaly_cols")
    contamination = st.slider("Expected anomaly rate", 0.01, 0.25, 0.05)

    if anomaly_cols:
        result = run_anomaly_detection(df, anomaly_cols, contamination)
        if result is not None:
            n_anomalies = result["is_anomaly"].sum()
            st.metric("Detected Anomalies", f"{n_anomalies} / {len(result)}")

            if len(anomaly_cols) >= 2:
                fig2 = px.scatter(
                    result, x=anomaly_cols[0], y=anomaly_cols[1],
                    color=result["is_anomaly"].map({True: "Anomaly", False: "Normal"}),
                    title="Anomaly Map"
                )
                st.plotly_chart(fig2, use_container_width=True)

            st.subheader("Flagged Anomalous Records")
            st.dataframe(result[result["is_anomaly"]], use_container_width=True)
        else:
            st.info("Not enough data for anomaly detection.")
    else:
        st.info("Select at least one numeric column.")