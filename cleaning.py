import argparse
from pathlib import Path

import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent
SOURCE_PATH = PROJECT_DIR / "Metro_Interstate_Traffic_Volume.csv"
DEFAULT_OUTPUT_PATH = PROJECT_DIR / "cleaned_traffic_data.csv"


def clean_data(source_path=SOURCE_PATH, output_path=DEFAULT_OUTPUT_PATH):
    source_path = Path(source_path).resolve()
    output_path = Path(output_path).resolve()
    if not source_path.is_file():
        raise FileNotFoundError(f"Source dataset not found: {source_path}")
    if source_path == output_path:
        raise ValueError("The cleaned output cannot overwrite the raw source dataset.")

    df = pd.read_csv(source_path)
    required_columns = {
        "holiday", "temp", "rain_1h", "snow_1h", "clouds_all",
        "weather_main", "date_time", "traffic_volume",
    }
    missing_columns = required_columns.difference(df.columns)
    if missing_columns:
        raise ValueError(
            "Source dataset is missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    df["holiday"] = df["holiday"].fillna("No Holiday")
    df = df.drop_duplicates().copy()
    df["date_time"] = pd.to_datetime(df["date_time"], errors="coerce")
    df = df.dropna(subset=["date_time", "traffic_volume"])
    df["temp_celsius"] = (df["temp"] - 273.15).round(2)
    df["year"] = df["date_time"].dt.year
    df["month"] = df["date_time"].dt.month
    df["month_name"] = df["date_time"].dt.month_name()
    df["day"] = df["date_time"].dt.day
    df["day_name"] = df["date_time"].dt.day_name()
    df["hour"] = df["date_time"].dt.hour
    df["day_type"] = df["day_name"].map(
        lambda day_name: "Weekend" if day_name in {"Saturday", "Sunday"} else "Weekday"
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    return df


def main():
    parser = argparse.ArgumentParser(description="Clean the Metro Interstate traffic dataset.")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help="Output CSV path (defaults to cleaned_traffic_data.csv).",
    )
    args = parser.parse_args()
    cleaned_df = clean_data(output_path=args.output)
    print(f"Cleaning completed: {len(cleaned_df):,} records saved to {args.output}")


if __name__ == "__main__":
    try:
        main()
    except (OSError, pd.errors.ParserError, ValueError) as error:
        raise SystemExit(f"Data cleaning failed: {error}") from error