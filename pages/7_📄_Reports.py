import streamlit as st
from fpdf import FPDF
from utils.data_utils import get_active_df, detect_business_columns
from utils.ai_utils import compute_health_score, score_label

st.set_page_config(page_title="Reports", page_icon="📄", layout="wide")

df = get_active_df()

st.title("📄 Reports")

# =========================
# Business Analysis
# =========================
detected = detect_business_columns(df)
result = compute_health_score(df, detected)
label, _ = score_label(result["score"])

st.subheader("Report Preview")

st.write(f"**Dataset Size:** {df.shape[0]} rows × {df.shape[1]} columns")
st.write(f"**Business Health Score:** {result['score']}/100 ({label})")

st.markdown("### Key Recommendations")

for rec in result["recommendations"]:
    st.markdown(f"- {rec}")

if result["breakdown"]:
    st.markdown("### Score Breakdown")
    st.json(result["breakdown"])


# =========================
# Clean text for PDF
# =========================
def clean_text(text):
    """
    Convert Unicode characters to Latin-1 compatible text.
    """

    replacements = {
        "—": "-",
        "–": "-",
        "•": "*",
        "₹": "Rs.",
        "✓": "[OK]",
        "✔": "[OK]",
        "✗": "[X]",
        "❌": "[X]",
        "⚠": "Warning:",
        "⚠️": "Warning:",
        "📈": "",
        "📉": "",
        "📊": "",
        "💰": "",
        "🚀": "",
        "🔥": "",
        "🎯": "",
        "😊": "",
        "🙂": "",
        "’": "'",
        "‘": "'",
        "“": '"',
        "”": '"',
        "…": "...",
        "×": "x",
    }

    text = str(text)

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Remove any remaining unsupported characters
    text = text.encode("latin-1", "ignore").decode("latin-1")

    return text


# =========================
# Build PDF
# =========================
def build_pdf():

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.add_page()

    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Smart Business Health Analyzer Report", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(3)

    pdf.set_font("Helvetica", "", 11)

    pdf.cell(
        0,
        8,
        clean_text(f"Dataset Size : {df.shape[0]} rows x {df.shape[1]} columns"),
        new_x="LMARGIN",
        new_y="NEXT",
    )

    pdf.cell(
        0,
        8,
        clean_text(f"Business Health Score : {result['score']}/100 ({label})"),
        new_x="LMARGIN",
        new_y="NEXT",
    )

    pdf.ln(5)

    # Score Breakdown
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "Score Breakdown", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 11)

    if result["breakdown"]:
        for key, value in result["breakdown"].items():
            line = clean_text(f"- {key}: {value}")
            pdf.multi_cell(0, 7, line)

    pdf.ln(4)

    # Recommendations
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "Recommendations", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 11)

    for rec in result["recommendations"]:
        pdf.multi_cell(0, 7, clean_text(f"- {rec}"))

    # Return PDF bytes
    return pdf.output(dest="S").encode("latin-1")


# =========================
# Download Buttons
# =========================
col1, col2 = st.columns(2)

with col1:
    st.download_button(
        label="⬇️ Download Dataset (CSV)",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="business_dataset.csv",
        mime="text/csv",
    )

with col2:
    pdf_bytes = build_pdf()

    st.download_button(
        label="⬇️ Download Summary Report (PDF)",
        data=pdf_bytes,
        file_name="business_health_report.pdf",
        mime="application/pdf",
    )