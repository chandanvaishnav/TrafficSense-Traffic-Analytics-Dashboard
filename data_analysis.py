from pathlib import Path

import pandas as pd

DATA_PATH = Path(__file__).resolve().parent / "cleaned_traffic_data.csv"
REQUIRED_COLUMNS = {"traffic_volume", "hour", "day_name", "day_type", "weather_main", "holiday"}


def main():
    if not DATA_PATH.is_file():
        raise FileNotFoundError(f"Cleaned dataset not found: {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    missing_columns = REQUIRED_COLUMNS.difference(df.columns)
    if missing_columns:
        raise ValueError("Dataset is missing required columns: " + ", ".join(sorted(missing_columns)))

    print("\n===== DATASET INFORMATION =====")
    print(df.info())
    print("\n===== TRAFFIC VOLUME STATISTICS =====")
    print(df["traffic_volume"].describe())

    hourly_traffic = df.groupby("hour")["traffic_volume"].mean()
    print("\n===== AVERAGE TRAFFIC BY HOUR =====")
    print(hourly_traffic)
    print("\n===== AVERAGE TRAFFIC BY DAY =====")
    print(df.groupby("day_name")["traffic_volume"].mean())
    print("\n===== WEEKDAY VS WEEKEND =====")
    print(df.groupby("day_type")["traffic_volume"].mean())
    print("\n===== TRAFFIC BY WEATHER =====")
    print(df.groupby("weather_main")["traffic_volume"].mean().sort_values(ascending=False))
    print("\n===== HOLIDAY ANALYSIS =====")
    print(df.groupby("holiday")["traffic_volume"].mean().sort_values(ascending=False))
    print("\n===== PEAK TRAFFIC HOUR =====")
    print(f"Peak hour: {hourly_traffic.idxmax()}:00")
    print(f"Average traffic volume: {hourly_traffic.max():,.2f}")


if __name__ == "__main__":
    try:
        main()
    except (OSError, pd.errors.ParserError, ValueError) as error:
        raise SystemExit(f"Data analysis failed: {error}") from error