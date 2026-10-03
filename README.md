# TrafficSense: Traffic Volume Analysis Dashboard

TrafficSense is an interactive Streamlit dashboard for exploring hourly traffic volume alongside calendar, holiday, and weather information. The project includes a reproducible cleaning script, exploratory analysis, saved visualizations, and a chronological machine-learning evaluation.

## Purpose

The project makes traffic patterns easier to inspect across time and weather. It is an educational analysis of the Metro Interstate Traffic Volume dataset, not a live traffic service or a causal study of weather effects.

## Features

- Interactive year, month, weather, and weekday/weekend filters.
- Summary metrics, filter-aware key insights, and five charts.
- Filtered record table and CSV download.
- Friendly handling for missing, malformed, or no-match data.
- Cleaning, analysis, visualization, and chronological prediction scripts.
- SQL examples for common traffic questions.

## Technology Stack

- Python 3.10 or newer
- Streamlit for the dashboard
- pandas for data preparation and analysis
- Matplotlib for visualizations
- scikit-learn for the Random Forest regression evaluation
- SQLite-compatible SQL examples

Install the Python dependencies from `requirements.txt`.

## Dataset

The raw file `Metro_Interstate_Traffic_Volume.csv` is the Metro Interstate Traffic Volume dataset from the [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/492/metro+interstate+traffic+volume). It contains hourly westbound I-94 traffic observations near Minneapolis–St. Paul, Minnesota, from 2012-10-02 through 2018-09-30, with weather observations from a nearby airport. Important source fields include traffic volume, timestamp, temperature, precipitation, cloud coverage, weather category/description, and holiday.

The repository also includes `cleaned_traffic_data.csv` (48,187 rows and 17 columns). `cleaning.py` fills missing holiday labels with `No Holiday`, removes exact duplicate rows, parses timestamps, removes rows with invalid timestamps or missing traffic targets, converts Kelvin to Celsius, and derives year, month, month name, day, weekday name, hour, and weekday/weekend fields. The raw source is never used as the cleaning output. To write to a different output path, run `python cleaning.py --output path/to/output.csv`.

## Installation and Run

1. Install Python 3.10 or newer.
2. From the project folder, create and activate a virtual environment:

	```powershell
	python -m venv .venv
	.\.venv\Scripts\Activate.ps1
	```

	On macOS/Linux, activate it with `source .venv/bin/activate`.
3. Install dependencies:

	```shell
	python -m pip install -r requirements.txt
	```
4. Start the dashboard from the project folder:

	```shell
	python -m streamlit run app.py
	```

The cleaned CSV must remain beside `app.py`. If it is missing, regenerate it from the included raw CSV using `python cleaning.py`.

## Key Findings

Findings below are calculated from all 48,187 cleaned rows and are descriptive, not causal:

- The busiest average hour is 16:00, at approximately 5,664 vehicles per recorded hour.
- June has the highest average monthly traffic (approximately 3,417 vehicles); monthly averages combine years.
- Average weekday traffic is approximately 3,533 versus 2,571 on weekends.
- `Clouds` is the weather category with the highest average traffic in this dataset (approximately 3,618); category sample sizes and the underlying traffic/time mix differ.
- The holiday-labelled subset is small (61 records), so holiday comparisons should be treated cautiously.

The dashboard recomputes its insights using only the records currently selected by the filters.

## Prediction Approach

`prediction.py` sorts observations chronologically, uses the oldest 80% for training and the newest 20% for testing, and reports Mean Absolute Error (MAE), Root Mean Squared Error (RMSE), and R². In the included dataset run, the model evaluated on 9,638 records from 2017-11-01 through 2018-09-30 and scored MAE 665.09 vehicles, RMSE 1,033.18 vehicles, and R² 0.7243. Features are temperature in Celsius, rain, snow, cloud coverage, hour, and month; the target is traffic volume. The timestamp is used to order the split, not as a model feature. The model is kept in memory and is not saved because the repository has no inference/deployment path that consumes a serialized model.

This holdout avoids training on later observations and evaluating on earlier ones, but the model is intentionally a simple baseline and does not include holiday, weekday, or weather-category features. The command `python prediction.py` prints the current metrics; results may vary with dataset or library versions.

## Project Structure

```text
TrafficSense_Project/
├── app.py                               # Streamlit dashboard
├── cleaning.py                          # Raw-to-cleaned data preparation
├── data_analysis.py                     # Console-based exploratory analysis
├── prediction.py                        # Chronological regression evaluation
├── visualizations.py                    # Static chart generation
├── traffic_analysis.sql                 # SQLite query examples
├── Metro_Interstate_Traffic_Volume.csv  # Original dataset
├── cleaned_traffic_data.csv             # Prepared dashboard dataset
├── traffic_by_*.png                     # Saved analysis charts
├── weekday_vs_weekend.png               # Saved weekday/weekend chart
├── requirements.txt
└── README.md
```

## Screenshots

The repository includes static analysis charts: [traffic by hour](traffic_by_hour.png), [traffic by day](traffic_by_day.png), [traffic by month](traffic_by_month.png), [traffic by weather](traffic_by_weather.png), and [weekday versus weekend](weekday_vs_weekend.png). To add a screenshot of the interactive dashboard, create `docs/screenshots/` and save an image such as `dashboard-overview.png` there, then embed it with `![TrafficSense dashboard](docs/screenshots/dashboard-overview.png)`.

## Limitations

- The data represents one highway direction and location, and ends in 2018; it is not current traffic.
- Weather associations are observational and do not establish that weather caused a traffic change.
- Hourly sampling, missing source observations, and uneven category sizes affect comparisons.
- The prediction model uses a small set of features and a single chronological holdout; it is not production-validated and should not be used for operational decisions.
- The repository is an analysis/demo application and has no live data ingestion, authentication, or model-serving endpoint.

## Links

- GitHub repository: pending publication.
- Streamlit Community Cloud dashboard: pending deployment.
