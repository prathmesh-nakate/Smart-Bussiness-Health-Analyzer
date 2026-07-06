import streamlit as st

st.set_page_config(
    page_title="Smart Business Health Analyzer",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Global session state initialization — single source of truth
if "df" not in st.session_state:
    st.session_state["df"] = None
if "df_raw" not in st.session_state:
    st.session_state["df_raw"] = None
if "upload_meta" not in st.session_state:
    st.session_state["upload_meta"] = {}

st.title("🧠 Smart Business Health Analyzer")
st.subheader("AI-Powered Business Intelligence Platform")

st.markdown(
    """
Welcome! This platform turns **any business CSV you upload** into a live,
self-updating intelligence suite — dashboards, KPIs, ML insights, forecasts,
AI recommendations, and exportable reports.

### How it works
1. Go to **📂 Data Upload** and upload your CSV.
2. Every other page automatically reads from that same dataset
   (`st.session_state["df"]`) — no fixed files, no reloading from disk.
3. Re-upload a new file anytime to refresh the entire app instantly.
"""
)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("#### 📊 Dynamic Dashboards")
    st.write("KPIs, trends, and breakdowns generated from your real columns.")
with col2:
    st.markdown("#### 🤖 ML & Forecasting")
    st.write("Clustering, anomaly detection, and revenue/sales forecasting.")
with col3:
    st.markdown("#### 💡 AI Recommendations")
    st.write("Rule-based business health scoring and actionable insights.")

st.divider()

if st.session_state["df"] is not None:
    df = st.session_state["df"]
    st.success(
        f"✅ Active dataset loaded: **{st.session_state['upload_meta'].get('filename','uploaded file')}** "
        f"— {df.shape[0]} rows × {df.shape[1]} columns"
    )
    st.dataframe(df.head(10), use_container_width=True)
else:
    st.warning("⚠️ No dataset loaded yet. Please go to **📂 Data Upload** in the sidebar to begin.")