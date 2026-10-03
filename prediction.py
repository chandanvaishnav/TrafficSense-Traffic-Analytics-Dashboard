from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

DATA_PATH = Path(__file__).resolve().parent / "cleaned_traffic_data.csv"
FEATURE_COLUMNS = [
    "temp_celsius",
    "rain_1h",
    "snow_1h",
    "clouds_all",
    "hour",
    "month",
]


def main():
    if not DATA_PATH.is_file():
        raise FileNotFoundError(f"Cleaned dataset not found: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)
    required_columns = {*FEATURE_COLUMNS, "traffic_volume", "date_time"}
    missing_columns = required_columns.difference(df.columns)
    if missing_columns:
        raise ValueError(
            "Dataset is missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    df["date_time"] = pd.to_datetime(df["date_time"], errors="coerce")
    df = df.dropna(subset=["date_time", *FEATURE_COLUMNS, "traffic_volume"])
    df = df.sort_values("date_time").reset_index(drop=True)
    split_index = int(len(df) * 0.8)
    if split_index < 2 or len(df) - split_index < 2:
        raise ValueError("At least five valid records are required for an 80/20 split.")

    # Keep the newest 20% completely out of model fitting.
    train_df = df.iloc[:split_index]
    test_df = df.iloc[split_index:]
    X_train, y_train = train_df[FEATURE_COLUMNS], train_df["traffic_volume"]
    X_test, y_test = test_df[FEATURE_COLUMNS], test_df["traffic_volume"]

    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)
    rmse = mean_squared_error(y_test, predictions) ** 0.5
    r_squared = r2_score(y_test, predictions)

    print("\n===== CHRONOLOGICAL HOLDOUT PERFORMANCE =====")
    print(f"Training records: {len(train_df):,} (oldest 80%)")
    print(f"Test records: {len(test_df):,} (newest 20%)")
    print(f"Test period: {test_df['date_time'].min()} through {test_df['date_time'].max()}")
    print(f"MAE: {mae:,.2f} vehicles")
    print(f"RMSE: {rmse:,.2f} vehicles")
    print(f"R²: {r_squared:.4f}")
    print(
        "\nPrediction summary: On unseen later timestamps, predictions differ from "
        f"observed traffic by about {mae:,.0f} vehicles on average (MAE). "
        f"The model explains {r_squared:.1%} of test-set traffic variation by R²."
    )
    print("The model is not saved; this script has no inference or deployment consumer.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, pd.errors.ParserError, ValueError) as error:
        raise SystemExit(f"Prediction analysis failed: {error}") from error