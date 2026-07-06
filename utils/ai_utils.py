"""
Rule-based 'AI' business health scoring and recommendation engine.
Fully dynamic: works off whatever revenue/profit/cost/date columns
were detected in the uploaded dataset.
"""

import pandas as pd
import numpy as np


def compute_health_score(df: pd.DataFrame, cols: dict) -> dict:
    """
    Computes a 0-100 business health score from available signals:
    growth trend, profit margin, anomaly rate, data completeness.
    Returns score + breakdown + narrative recommendations.
    """
    score = 50.0
    breakdown = {}
    recommendations = []

    revenue_col, profit_col, cost_col, date_col = (
        cols.get("revenue"), cols.get("profit"), cols.get("cost"), cols.get("date")
    )

    # --- Growth trend ---
    if date_col and revenue_col:
        ts = df[[date_col, revenue_col]].dropna().copy()
        ts[date_col] = pd.to_datetime(ts[date_col], errors="coerce")
        ts = ts.dropna(subset=[date_col]).sort_values(date_col)
        if len(ts) >= 4:
            ts["period"] = pd.qcut(ts[date_col].rank(method="first"), 2, labels=["early", "late"])
            grp = ts.groupby("period")[revenue_col].sum()
            if grp.get("early", 0) > 0:
                growth = (grp.get("late", 0) - grp.get("early", 0)) / grp.get("early", 1) * 100
                growth_score = np.clip(50 + growth / 2, 0, 100)
                breakdown["Growth Trend"] = round(growth_score, 1)
                if growth > 5:
                    recommendations.append(f"Revenue is trending up (~{growth:.1f}% growth) — consider scaling marketing or inventory.")
                elif growth < -5:
                    recommendations.append(f"Revenue is declining (~{growth:.1f}%) — investigate churn, pricing, or demand shifts.")
                else:
                    recommendations.append("Revenue is roughly flat — explore new channels or products to reignite growth.")

    # --- Profitability ---
    if profit_col and revenue_col:
        total_rev = df[revenue_col].sum()
        total_profit = df[profit_col].sum()
        if total_rev > 0:
            margin = total_profit / total_rev * 100
            margin_score = np.clip(margin * 2, 0, 100)
            breakdown["Profit Margin"] = round(margin_score, 1)
            if margin < 10:
                recommendations.append(f"Profit margin is thin ({margin:.1f}%) — review cost structure and pricing strategy.")
            else:
                recommendations.append(f"Healthy profit margin ({margin:.1f}%) — maintain cost discipline as you scale.")
    elif cost_col and revenue_col:
        total_rev = df[revenue_col].sum()
        total_cost = df[cost_col].sum()
        if total_rev > 0:
            margin = (total_rev - total_cost) / total_rev * 100
            margin_score = np.clip(margin * 2, 0, 100)
            breakdown["Profit Margin (est.)"] = round(margin_score, 1)
            recommendations.append(f"Estimated margin from cost data: {margin:.1f}%.")

    # --- Data completeness ---
    completeness = (1 - df.isna().mean().mean()) * 100
    breakdown["Data Completeness"] = round(completeness, 1)
    if completeness < 80:
        recommendations.append("Data has notable gaps — improving data capture will sharpen future insights.")

    # --- Volatility / consistency ---
    if revenue_col:
        vals = df[revenue_col].dropna()
        if len(vals) > 1 and vals.mean() != 0:
            cv = vals.std() / abs(vals.mean())
            consistency_score = np.clip(100 - cv * 100, 0, 100)
            breakdown["Revenue Consistency"] = round(consistency_score, 1)
            if cv > 0.6:
                recommendations.append("Revenue is volatile across records — consider diversifying revenue streams.")

    if breakdown:
        score = float(np.mean(list(breakdown.values())))
    else:
        recommendations.append("Upload data with revenue/date columns for deeper scoring.")

    if not recommendations:
        recommendations.append("Dataset loaded successfully. Add revenue, profit, or date columns for richer AI insights.")

    return {
        "score": round(score, 1),
        "breakdown": breakdown,
        "recommendations": recommendations,
    }


def score_label(score: float) -> tuple[str, str]:
    """Returns (label, color) for a given health score."""
    if score >= 75:
        return "Excellent", "green"
    elif score >= 55:
        return "Good", "blue"
    elif score >= 35:
        return "Needs Attention", "orange"
    else:
        return "Critical", "red"