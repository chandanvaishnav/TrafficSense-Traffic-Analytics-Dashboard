from pathlib import Path

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="TrafficSense Dashboard",
    page_icon="🚦",
    layout="wide"
)


# ==================================================
# DARK THEME CSS
# ==================================================

st.markdown("""
<style>

/* Main Background */
.stApp {
    background-color: #0E1117;
    color: white;
}

/* Main Content */
.main {
    background-color: #0E1117;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #161B22;
}

/* Sidebar Text */
[data-testid="stSidebar"] * {
    color: white;
}

/* Headings */
h1, h2, h3 {
    color: #FFFFFF;
}

/* Normal Text */
p, span, label {
    color: #D1D5DB;
}

/* Metric Cards */
[data-testid="stMetric"] {
    background-color: #1C2128;
    padding: 20px;
    border-radius: 10px;
    border: 1px solid #30363D;
}

[data-testid="stMetricLabel"] {
    color: #AAB2BF;
}

[data-testid="stMetricValue"] {
    color: #00D4FF;
}

/* Divider */
hr {
    border-color: #30363D;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    background-color: #161B22;
}

/* Multiselect */
[data-baseweb="select"] {
    background-color: #1C2128;
}

</style>
""", unsafe_allow_html=True)


# ==================================================
# LOAD DATA
# ==================================================

DATA_PATH = Path(__file__).resolve().parent / "cleaned_traffic_data.csv"
REQUIRED_COLUMNS = {
    "date_time", "traffic_volume", "weather_main", "year", "month",
    "month_name", "day_name", "hour", "day_type",
}


@st.cache_data
def load_data(path):
    if not path.is_file():
        raise FileNotFoundError(f"The cleaned dataset was not found: {path.name}")

    df = pd.read_csv(path)
    missing_columns = REQUIRED_COLUMNS.difference(df.columns)
    if missing_columns:
        raise ValueError(
            "The cleaned dataset is missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    df["date_time"] = pd.to_datetime(df["date_time"], errors="coerce")
    if df["date_time"].isna().any():
        raise ValueError("The cleaned dataset contains invalid date_time values.")
    if df.empty:
        raise ValueError("The cleaned dataset contains no records.")
    return df


try:
    df = load_data(DATA_PATH)
except (OSError, pd.errors.ParserError, ValueError) as error:
    st.error(f"Unable to load the traffic dataset. {error}")
    st.info("Place a valid cleaned_traffic_data.csv beside app.py and try again.")
    st.stop()


# ==================================================
# SIDEBAR FILTERS
# ==================================================

st.sidebar.title("🔍 Filter Traffic Data")


def reset_filters():
    for key in ("year_filter", "month_filter", "weather_filter", "day_type_filter"):
        st.session_state.pop(key, None)


st.sidebar.button("Reset Filters", on_click=reset_filters, width="stretch")

# YEAR FILTER
years = sorted(df["year"].unique())

selected_year = st.sidebar.multiselect(
    "Select Year",
    years,
    default=years,
    key="year_filter",
)


# MONTH FILTER
months = sorted(df["month"].unique())

selected_month = st.sidebar.multiselect(
    "Select Month",
    months,
    default=months,
    key="month_filter",
)


# WEATHER FILTER
weather = sorted(df["weather_main"].unique())

selected_weather = st.sidebar.multiselect(
    "Select Weather",
    weather,
    default=weather,
    key="weather_filter",
)


# DAY TYPE FILTER
day_types = sorted(df["day_type"].unique())

selected_day_type = st.sidebar.multiselect(
    "Select Day Type",
    day_types,
    default=day_types,
    key="day_type_filter",
)


# ==================================================
# APPLY FILTERS
# ==================================================

filtered_df = df[
    (df["year"].isin(selected_year)) &
    (df["month"].isin(selected_month)) &
    (df["weather_main"].isin(selected_weather)) &
    (df["day_type"].isin(selected_day_type))
]


# ==================================================
# DASHBOARD HEADER
# ==================================================

st.title("🚦 TrafficSense Dashboard")

st.subheader("Traffic Volume Analysis and Visualization")

st.write(
    "An interactive data analytics dashboard for analyzing traffic patterns "
    "based on time, day, month, weather, and traffic volume."
)

st.divider()


# ==================================================
# TRAFFIC OVERVIEW
# ==================================================

st.header("📊 Traffic Overview")

total_records = len(filtered_df)

if filtered_df.empty:
    st.info("No records match these filters. Adjust your selections or reset the filters.")
    st.stop()

average_traffic = filtered_df["traffic_volume"].mean()

maximum_traffic = filtered_df["traffic_volume"].max()


# Peak Hour
if len(filtered_df) > 0:

    hourly_data = (
        filtered_df.groupby("hour")["traffic_volume"]
        .mean()
    )

    peak_hour = hourly_data.idxmax()

else:
    peak_hour = 0


# METRICS
col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Records",
    f"{total_records:,}"
)

col2.metric(
    "Average Traffic Volume",
    f"{average_traffic:.0f}"
)

col3.metric(
    "Maximum Traffic Volume",
    f"{maximum_traffic:,}"
)

col4.metric(
    "Peak Traffic Hour",
    f"{peak_hour}:00"
)


st.divider()


# ==================================================
# KEY INSIGHTS
# ==================================================

st.header("💡 Key Insights")
peak_hour = int(filtered_df.groupby("hour")["traffic_volume"].mean().idxmax())
busiest_day = filtered_df.groupby("day_name")["traffic_volume"].mean().idxmax()
busiest_weather = filtered_df.groupby("weather_main")["traffic_volume"].mean().idxmax()
highest_month = filtered_df.groupby("month_name")["traffic_volume"].mean().idxmax()

insight_col1, insight_col2 = st.columns(2)
insight_col1.markdown(
    f"- **Busiest average hour:** {peak_hour:02d}:00 "
    f"({filtered_df.groupby('hour')['traffic_volume'].mean().max():,.0f} vehicles)\n"
    f"- **Busiest day:** {busiest_day} "
    f"({filtered_df.groupby('day_name')['traffic_volume'].mean().max():,.0f} vehicles)"
)
insight_col2.markdown(
    f"- **Highest-average weather category:** {busiest_weather}\n"
    f"- **Highest-average month:** {highest_month}"
)
st.caption("Insights are recalculated from the records that match the current filters.")

st.divider()


# ==================================================
# GRAPH 1 - TRAFFIC BY HOUR
# ==================================================

st.header("📈 Average Traffic Volume by Hour")

hourly_traffic = (
    filtered_df.groupby("hour")["traffic_volume"]
    .mean()
)

fig, ax = plt.subplots(figsize=(12, 5))

fig.patch.set_facecolor("#161B22")
ax.set_facecolor("#161B22")

ax.plot(
    hourly_traffic.index,
    hourly_traffic.values,
    marker="o",
    linewidth=2
)

ax.set_title(
    "Average Traffic Volume by Hour",
    color="white",
    fontsize=16
)

ax.set_xlabel("Hour", color="white")
ax.set_ylabel("Average Traffic Volume", color="white")

ax.tick_params(colors="white")

ax.grid(
    True,
    alpha=0.3
)

for spine in ax.spines.values():
    spine.set_color("white")

st.pyplot(fig, width="stretch")
st.caption("Each point is the mean observed traffic volume for that hour.")


st.divider()


# ==================================================
# GRAPH 2 - TRAFFIC BY DAY
# ==================================================

st.header("📅 Average Traffic Volume by Day")

day_order = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]

daily_traffic = (
    filtered_df.groupby("day_name")["traffic_volume"]
    .mean()
    .reindex(day_order)
)

fig, ax = plt.subplots(figsize=(12, 5))

fig.patch.set_facecolor("#161B22")
ax.set_facecolor("#161B22")

ax.bar(
    daily_traffic.index,
    daily_traffic.values
)

ax.set_title(
    "Average Traffic Volume by Day",
    color="white",
    fontsize=16
)

ax.set_xlabel("Day", color="white")
ax.set_ylabel("Average Traffic Volume", color="white")

ax.tick_params(
    axis="x",
    colors="white",
    rotation=30
)

ax.tick_params(
    axis="y",
    colors="white"
)

for spine in ax.spines.values():
    spine.set_color("white")

st.pyplot(fig, width="stretch")
st.caption("Daily means are shown in calendar order for the filtered records.")


st.divider()


# ==================================================
# GRAPH 3 - TRAFFIC BY WEATHER
# ==================================================

st.header("🌦️ Average Traffic Volume by Weather")

weather_traffic = (
    filtered_df.groupby("weather_main")["traffic_volume"]
    .mean()
    .sort_values(ascending=False)
)

fig, ax = plt.subplots(figsize=(12, 5))

fig.patch.set_facecolor("#161B22")
ax.set_facecolor("#161B22")

ax.bar(
    weather_traffic.index,
    weather_traffic.values
)

ax.set_title(
    "Average Traffic Volume by Weather",
    color="white",
    fontsize=16
)

ax.set_xlabel("Weather", color="white")
ax.set_ylabel("Average Traffic Volume", color="white")

ax.tick_params(
    axis="x",
    colors="white",
    rotation=35
)

ax.tick_params(
    axis="y",
    colors="white"
)

for spine in ax.spines.values():
    spine.set_color("white")

st.pyplot(fig, width="stretch")
st.caption("Weather categories are ordered from highest to lowest average traffic.")


st.divider()


# ==================================================
# GRAPH 4 - WEEKDAY VS WEEKEND
# ==================================================

st.header("🗓️ Weekday vs Weekend Traffic")

day_type_traffic = (
    filtered_df.groupby("day_type")["traffic_volume"]
    .mean()
)

fig, ax = plt.subplots(figsize=(8, 5))

fig.patch.set_facecolor("#161B22")
ax.set_facecolor("#161B22")

ax.bar(
    day_type_traffic.index,
    day_type_traffic.values
)

ax.set_title(
    "Weekday vs Weekend Traffic",
    color="white",
    fontsize=16
)

ax.set_xlabel("Day Type", color="white")
ax.set_ylabel("Average Traffic Volume", color="white")

ax.tick_params(colors="white")

for spine in ax.spines.values():
    spine.set_color("white")

st.pyplot(fig, width="stretch")
st.caption("Compares the mean traffic volume for weekdays and weekends.")


st.divider()


# ==================================================
# GRAPH 5 - MONTHLY TRAFFIC
# ==================================================

st.header("📆 Average Traffic Volume by Month")

monthly_traffic = (
    filtered_df.groupby("month")["traffic_volume"]
    .mean()
)

fig, ax = plt.subplots(figsize=(12, 5))

fig.patch.set_facecolor("#161B22")
ax.set_facecolor("#161B22")

ax.plot(
    monthly_traffic.index,
    monthly_traffic.values,
    marker="o",
    linewidth=2
)

ax.set_title(
    "Average Traffic Volume by Month",
    color="white",
    fontsize=16
)

ax.set_xlabel("Month", color="white")
ax.set_ylabel("Average Traffic Volume", color="white")

ax.set_xticks(range(1, 13))

ax.tick_params(colors="white")

ax.grid(
    True,
    alpha=0.3
)

for spine in ax.spines.values():
    spine.set_color("white")

st.pyplot(fig, width="stretch")
st.caption("Monthly means use month number, so they combine the selected years.")


st.divider()
st.header("🧾 Filtered Records")
st.caption(f"Showing {len(filtered_df):,} matching records.")
st.dataframe(filtered_df, width="stretch", hide_index=True)
st.download_button(
    "Download filtered data as CSV",
    data=filtered_df.to_csv(index=False).encode("utf-8"),
    file_name="trafficsense_filtered_data.csv",
    mime="text/csv",
    width="stretch",
)


st.divider()


# ==================================================
# DATA TABLE
# ==================================================

st.header("📋 Filtered Traffic Data")

st.dataframe(
    filtered_df,
    width="stretch",
    height=400
)


# ==================================================
# DATA DOWNLOAD
# ==================================================

st.header("⬇️ Download Filtered Data")

csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Filtered Traffic Data",
    data=csv,
    file_name="filtered_traffic_data.csv",
    mime="text/csv"
)


# ==================================================
# FOOTER
# ==================================================

st.divider()

st.markdown(
    """
    <div style="text-align:center; color:#8B949E;">
        TrafficSense | Traffic Data Analytics Project<br>
        Built using Python, Pandas, Matplotlib and Streamlit
    </div>
    """,
    unsafe_allow_html=True
)