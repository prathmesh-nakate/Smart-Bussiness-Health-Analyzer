import streamlit as st

st.set_page_config(
    page_title="Smart Business Health Analyzer",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Global Session State
# -----------------------------
if "df" not in st.session_state:
    st.session_state["df"] = None

if "df_raw" not in st.session_state:
    st.session_state["df_raw"] = None

if "upload_meta" not in st.session_state:
    st.session_state["upload_meta"] = {}

# -----------------------------
# Title
# -----------------------------
st.title("🧠 Smart Business Health Analyzer")
st.subheader("AI-Powered Business Intelligence Platform")

# -----------------------------
# Introduction
# -----------------------------
st.markdown("""
Welcome! This platform transforms **any business dataset** into a powerful
Business Intelligence dashboard.

It automatically analyzes uploaded business data and provides:

- 📊 Interactive Dashboards
- 📈 KPI Analysis
- 🤖 Machine Learning Insights
- 📉 Forecasting
- 💡 AI Recommendations
- 📄 Downloadable Reports

The goal is to help businesses make **faster, smarter, and data-driven decisions**.
""")

# -----------------------------
# Problem Statement
# -----------------------------
st.markdown("## 🎯 Problem Statement")

st.info("""
Businesses generate large amounts of data every day, but analyzing it manually is
time-consuming, complex, and prone to errors. Many small and medium-sized businesses
lack an easy-to-use platform that can automatically analyze their business data,
identify important KPIs, predict future trends, and provide intelligent recommendations.

The **Smart Business Health Analyzer** solves this problem by automatically cleaning
the uploaded data, generating interactive dashboards, calculating KPIs, applying
machine learning techniques, forecasting future business performance, and providing
AI-based recommendations—all within a single user-friendly application.
""")

# -----------------------------
# How It Works
# -----------------------------
st.markdown("## 🚀 How It Works")

st.markdown("""
1️⃣ Go to **📂 Data Upload**

2️⃣ Upload your Business CSV or Excel file

3️⃣ The application automatically:
- Cleans the data
- Detects important business columns
- Stores the dataset

4️⃣ Explore:
- 📊 Dashboard
- 🧮 KPI Analysis
- 🤖 ML Insights
- 📈 Forecasting
- 💡 AI Recommendations
- 📄 Reports

5️⃣ Download the final business report.
""")

# -----------------------------
# Features
# -----------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📊 Dynamic Dashboards")
    st.write(
        "Automatically generate interactive charts, KPIs, trends, and business visualizations."
    )

with col2:
    st.markdown("### 🤖 ML & Forecasting")
    st.write(
        "Apply Machine Learning to discover patterns, detect anomalies, and forecast future business performance."
    )

with col3:
    st.markdown("### 💡 AI Recommendations")
    st.write(
        "Generate intelligent business recommendations and calculate an overall Business Health Score."
    )

st.divider()

# -----------------------------
# Dataset Status
# -----------------------------
if st.session_state["df"] is not None:

    df = st.session_state["df"]

    st.success(
        f"✅ Active Dataset Loaded: **{st.session_state['upload_meta'].get('filename','Uploaded File')}**"
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Rows", df.shape[0])

    with col2:
        st.metric("Columns", df.shape[1])

    with col3:
        st.metric("Missing Values", int(df.isnull().sum().sum()))

    st.markdown("### 📋 Dataset Preview")
    st.dataframe(df.head(10), use_container_width=True)

else:

    st.warning(
        "⚠️ No dataset loaded yet.\n\nPlease open **📂 Data Upload** from the sidebar and upload a CSV or Excel file to begin."
    )

st.divider()

# -----------------------------
# Footer
# -----------------------------
st.caption(
    "© 2026 Smart Business Health Analyzer | Diploma Final Year Project | Developed using Python, Streamlit, Pandas, NumPy, Plotly & Scikit-learn."
)