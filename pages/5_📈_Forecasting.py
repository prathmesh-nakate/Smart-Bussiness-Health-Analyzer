import streamlit as st
import plotly.express as px
from utils.data_utils import get_active_df, infer_column_types, detect_business_columns
from utils.ml_utils import simple_linear_forecast

st.set_page_config(page_title="Forecasting", page_icon="📈", layout="wide")
df = get_active_df()

st.title("📈 Forecasting")

types = infer_column_types(df)
detected = detect_business_columns(df)

date_options = types["datetime"] or ([detected["date"]] if detected["date"] else [])
if not date_options:
    st.warning("No datetime column detected in your dataset. Forecasting requires a date column.")
    st.stop()

c1, c2, c3 = st.columns(3)
date_col = c1.selectbox("Date column", date_options)
value_col = c2.selectbox("Value to forecast", types["numeric"],
                          index=(types["numeric"].index(detected["revenue"])
                                 if detected["revenue"] in types["numeric"] else 0))
periods = c3.slider("Days to forecast", 7, 180, 30)

result = simple_linear_forecast(df, date_col, value_col, periods)

if result is None:
    st.warning("Not enough historical data points to build a forecast (need at least 5).")
else:
    fig = px.line(result, x=date_col, y="value", color="type",
                  title=f"{value_col} Forecast — Next {periods} Days")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Forecast Data")
    st.dataframe(result.tail(periods + 5), use_container_width=True)

    st.download_button(
        "⬇️ Download forecast as CSV",
        data=result.to_csv(index=False).encode("utf-8"),
        file_name="forecast.csv",
        mime="text/csv",
    )

    st.info(
        "This is a lightweight linear-trend forecast meant for quick directional insight, "
        "not a substitute for a dedicated time-series model on critical decisions."
    )