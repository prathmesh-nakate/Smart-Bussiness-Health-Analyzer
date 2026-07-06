import streamlit as st
from utils.data_utils import get_active_df, detect_business_columns
from utils.ai_utils import compute_health_score, score_label

st.set_page_config(page_title="AI Recommendations", page_icon="💡", layout="wide")
df = get_active_df()

st.title("💡 AI-Powered Recommendations")

detected = detect_business_columns(df)
result = compute_health_score(df, detected)

label, color = score_label(result["score"])

c1, c2 = st.columns([1, 2])
with c1:
    st.metric("Business Health Score", f"{result['score']}/100")
    st.markdown(f"### Status: :{color}[{label}]")
    st.progress(min(int(result["score"]), 100))

with c2:
    if result["breakdown"]:
        st.subheader("Score Breakdown")
        st.bar_chart(result["breakdown"])

st.divider()
st.subheader("📋 Recommendations")
for i, rec in enumerate(result["recommendations"], 1):
    st.markdown(f"**{i}.** {rec}")

st.divider()
st.subheader("Detected Business Fields Used")
st.json({k: v for k, v in detected.items() if v})

st.caption(
    "Recommendations are generated from a transparent rule-based engine analyzing growth, "
    "profitability, consistency, and data quality signals in your uploaded dataset."
)