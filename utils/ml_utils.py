"""
Machine learning utilities: clustering, anomaly detection, forecasting.
All functions are generic — they operate on whatever numeric/date columns
exist in the uploaded dataset, with no hardcoded schema assumptions.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error


def linear_regression_trend(df: pd.DataFrame, x_col: str, y_col: str):
    """
    Simple Linear Regression: fits y = mx + c on two numeric columns.
    Returns predictions, R² score, and coefficients — used to explain
    'what affects what' in plain numeric terms.
    """
    data = df[[x_col, y_col]].dropna()
    if data.shape[0] < 5:
        return None

    X = data[[x_col]].values
    y = data[y_col].values

    model = LinearRegression()
    model.fit(X, y)
    preds = model.predict(X)

    return {
        "data": data.assign(predicted=preds),
        "slope": float(model.coef_[0]),
        "intercept": float(model.intercept_),
        "r2": round(r2_score(y, preds), 3),
    }


def random_forest_predict(df: pd.DataFrame, feature_cols: list[str], target_col: str):
    """
    Random Forest Regressor: predicts target_col from feature_cols.
    Returns model performance + feature importance — great for showing
    'which factors matter most' in a diploma presentation.
    """
    data = df[feature_cols + [target_col]].dropna()
    if data.shape[0] < 20:
        return None

    X = data[feature_cols]
    y = data[target_col]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)

    importance = pd.Series(model.feature_importances_, index=feature_cols).sort_values(ascending=False)

    return {
        "r2": round(r2_score(y_test, preds), 3),
        "mae": round(mean_absolute_error(y_test, preds), 3),
        "importance": importance,
        "model": model,
    }

def run_kmeans(df: pd.DataFrame, numeric_cols: list[str], k: int = 3):
    """Runs KMeans clustering on selected numeric columns."""
    data = df[numeric_cols].dropna()
    if data.shape[0] < k or data.shape[1] == 0:
        return None, None

    scaler = StandardScaler()
    scaled = scaler.fit_transform(data)

    model = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = model.fit_predict(scaled)

    result = data.copy()
    result["cluster"] = labels
    return result, model


def run_anomaly_detection(df: pd.DataFrame, numeric_cols: list[str], contamination: float = 0.05):
    """Flags anomalous rows using Isolation Forest."""
    data = df[numeric_cols].dropna()
    if data.shape[0] < 10 or data.shape[1] == 0:
        return None

    model = IsolationForest(contamination=contamination, random_state=42)
    preds = model.fit_predict(data)  # -1 = anomaly, 1 = normal

    result = data.copy()
    result["is_anomaly"] = preds == -1
    return result


def simple_linear_forecast(df: pd.DataFrame, date_col: str, value_col: str, periods: int = 30):
    """
    Aggregates value_col by date_col (daily) and fits a simple linear trend
    plus seasonal-naive residual smoothing for a lightweight forecast.
    Returns a dataframe with historical + forecasted values.
    """
    ts = df[[date_col, value_col]].dropna().copy()
    ts[date_col] = pd.to_datetime(ts[date_col], errors="coerce")
    ts = ts.dropna(subset=[date_col])
    ts = ts.groupby(date_col, as_index=False)[value_col].sum().sort_values(date_col)

    if ts.shape[0] < 5:
        return None

    ts["t"] = np.arange(len(ts))
    X = ts[["t"]].values
    y = ts[value_col].values

    model = LinearRegression()
    model.fit(X, y)

    future_t = np.arange(len(ts), len(ts) + periods).reshape(-1, 1)
    future_dates = pd.date_range(
        ts[date_col].max() + pd.Timedelta(days=1), periods=periods, freq="D"
    )
    forecast_vals = model.predict(future_t)
    forecast_vals = np.maximum(forecast_vals, 0)  # no negative business values

    hist = ts[[date_col, value_col]].rename(columns={value_col: "value"})
    hist["type"] = "Actual"

    fut = pd.DataFrame({date_col: future_dates, "value": forecast_vals})
    fut["type"] = "Forecast"

    return pd.concat([hist, fut], ignore_index=True)