from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent
DATA_PATH = PROJECT_DIR / "cleaned_traffic_data.csv"
REQUIRED_COLUMNS = {"hour", "day_name", "weather_main", "day_type", "month", "traffic_volume"}


def main():
    if not DATA_PATH.is_file():
        raise FileNotFoundError(f"Cleaned dataset not found: {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    missing_columns = REQUIRED_COLUMNS.difference(df.columns)
    if missing_columns:
        raise ValueError("Dataset is missing required columns: " + ", ".join(sorted(missing_columns)))

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    charts = [
        ("traffic_by_hour.png", "Average Traffic Volume by Hour", "Hour", "Average Traffic Volume",
         df.groupby("hour")["traffic_volume"].mean(), "line"),
        ("traffic_by_day.png", "Average Traffic Volume by Day", "Day", "Average Traffic Volume",
         df.groupby("day_name")["traffic_volume"].mean().reindex(days), "bar"),
        ("traffic_by_weather.png", "Average Traffic Volume by Weather", "Weather", "Average Traffic Volume",
         df.groupby("weather_main")["traffic_volume"].mean().sort_values(ascending=False), "bar"),
        ("weekday_vs_weekend.png", "Weekday vs Weekend Traffic", "Day Type", "Average Traffic Volume",
         df.groupby("day_type")["traffic_volume"].mean(), "bar"),
        ("traffic_by_month.png", "Average Traffic Volume by Month", "Month", "Average Traffic Volume",
         df.groupby("month")["traffic_volume"].mean(), "line"),
    ]

    for filename, title, x_label, y_label, values, chart_type in charts:
        figure, axis = plt.subplots(figsize=(10, 5))
        if chart_type == "line":
            axis.plot(values.index, values.values, marker="o")
        else:
            axis.bar(values.index, values.values)
        axis.set(title=title, xlabel=x_label, ylabel=y_label)
        axis.grid(axis="y", alpha=0.25)
        axis.tick_params(axis="x", rotation=35)
        figure.tight_layout()
        figure.savefig(PROJECT_DIR / filename, dpi=150)
        plt.close(figure)

    print(f"Created {len(charts)} visualization files in {PROJECT_DIR}")


if __name__ == "__main__":
    try:
        main()
    except (OSError, pd.errors.ParserError, ValueError) as error:
        raise SystemExit(f"Visualization generation failed: {error}") from error