"""
Shared visual theme for the whole app.
Call apply_theme() at the top of every page for a consistent, polished look.
"""

import streamlit as st


def apply_theme():
    st.markdown(
        """
        <style>
        /* Page background gradient */
        .stApp {
            background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        }

        /* Headings */
        h1, h2, h3 {
            color: #38bdf8 !important;
            font-family: 'Trebuchet MS', sans-serif;
        }

        /* Metric cards */
        div[data-testid="stMetric"] {
            background: rgba(56, 189, 248, 0.08);
            border: 1px solid rgba(56, 189, 248, 0.35);
            padding: 14px;
            border-radius: 14px;
        }

        /* Buttons */
        .stButton button, .stDownloadButton button {
            border-radius: 10px;
            border: 1px solid #38bdf8;
            font-weight: 600;
        }

        /* Info / success / warning boxes */
        div[data-testid="stAlert"] {
            border-radius: 12px;
        }

        /* Sidebar */
        section[data-testid="stSidebar"] {
            background: #0b1220;
        }

        /* Card-style container helper */
        .info-card {
            background: rgba(255,255,255,0.04);
            border-left: 4px solid #38bdf8;
            padding: 12px 16px;
            border-radius: 8px;
            margin-bottom: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def info_card(text: str):
    """Renders a styled explanation box — use these to teach viewers what a section does."""
    st.markdown(f'<div class="info-card">ℹ️ {text}</div>', unsafe_allow_html=True)