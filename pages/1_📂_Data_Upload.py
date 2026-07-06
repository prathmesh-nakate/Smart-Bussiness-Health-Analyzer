import streamlit as st
import pandas as pd
from utils.theme import apply_theme, info_card
from utils.data_utils import auto_clean, deep_clean, infer_column_types, detect_business_columns, assess_data_quality

st.set_page_config(page_title="Data Upload", page_icon="📂", layout="wide")
apply_theme()
st.title("📂 Data Upload")
info_card("Upload any business CSV here. Every other page in this app reads from this exact dataset — upload once, and dashboards, ML, and reports all update automatically.")

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file is not None:
    try:
        raw_df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Could not read file: {e}")
        st.stop()

    st.session_state["df_raw"] = raw_df.copy()

    # Always run light auto-clean first so basic columns work everywhere
    working_df = auto_clean(raw_df)
    st.session_state["df"] = working_df
    st.session_state["upload_meta"] = {
        "filename": uploaded_file.name,
        "rows": working_df.shape[0],
        "cols": working_df.shape[1],
    }
    st.success(f"✅ Loaded **{uploaded_file.name}** — {working_df.shape[0]} rows × {working_df.shape[1]} columns")

if st.session_state.get("df") is not None:
    df = st.session_state["df"]

    # ---- Data Quality Check & Recommendation ----
    quality = assess_data_quality(df)
    st.subheader("🩺 Data Quality Check")

    if quality["is_dirty"]:
        st.warning("⚠️ Your dataset looks **uncleaned**. We found the following issues:")
        for issue in quality["issues"]:
            st.markdown(f"- {issue}")
        st.markdown("**Recommendation:** Click below to auto-clean your data (removes duplicates, trims whitespace, fixes missing values) before analyzing it.")
        if st.button("🧹 Clean my data now"):
            st.session_state["df"] = deep_clean(df)
            st.success("Data cleaned! Re-checking quality...")
            st.rerun()
    else:
        st.success("✅ Your dataset looks clean and ready for analysis.")

    st.divider()
    st.subheader("Preview")
    st.dataframe(df.head(20), use_container_width=True)

    st.subheader("Column Overview")
    types = infer_column_types(df)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Numeric Columns", len(types["numeric"]))
    c2.metric("Categorical Columns", len(types["categorical"]))
    c3.metric("Datetime Columns", len(types["datetime"]))
    c4.metric("Text Columns", len(types["text"]))

    with st.expander("📘 What do these column types mean?"):
        st.write("**Numeric** = numbers used for math (revenue, quantity). **Categorical** = labels with few repeated values (region, product type). **Datetime** = dates/timestamps used for trends. **Text** = free-form text with many unique values.")

    st.subheader("Auto-Detected Business Fields")
    detected = detect_business_columns(df)
    info_card("The app guesses which columns represent revenue, profit, date, etc. so other pages can build charts automatically — no manual setup needed.")
    st.json(detected)

    st.subheader("Manual Options")
    colA, colB, colC = st.columns(3)
    with colA:
        if st.button("Drop rows with any missing values"):
            st.session_state["df"] = st.session_state["df"].dropna()
            st.rerun()
    with colB:
        if st.button("Deep clean (full pass)"):
            st.session_state["df"] = deep_clean(st.session_state["df_raw"])
            st.rerun()
    with colC:
        if st.button("Reset to original uploaded file"):
            st.session_state["df"] = st.session_state["df_raw"].copy()
            st.rerun()

    st.download_button(
        "⬇️ Download current working dataset as CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="working_dataset.csv",
        mime="text/csv",
    )
else:
    st.info("No dataset uploaded yet.")