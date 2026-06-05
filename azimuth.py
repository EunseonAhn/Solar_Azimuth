import streamlit as st
import pandas as pd
import pvlib
from datetime import datetime, time
from timezonefinder import TimezoneFinder
import pytz

st.title("Solar Azimuth/Altitude Calculator")

# -----------------------------------------------------
# Inputs
# -----------------------------------------------------
latitude = st.number_input("Enter Latitude", -90.0, 90.0, 0.0)
longitude = st.number_input("Enter Longitude", -180.0, 180.0, 0.0)

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date", datetime.today().date())
with col2:
    end_date = st.date_input("End Date", datetime.today().date())

interval_minutes = st.number_input("Time Resolution (minutes)", 1, 1440, 60)

# -----------------------------------------------------
# Local time
# -----------------------------------------------------
tf = TimezoneFinder()
tz_name = tf.timezone_at(lat=latitude, lng=longitude)
if tz_name is None:
    tz_name = "UTC"

local_tz = pytz.timezone(tz_name)

# -----------------------------------------------------
# Date Range Validation
# -----------------------------------------------------
if start_date > end_date:
    st.error("End date must be on or after start date.")
else:
    # Create start/end datetimes in local time
    start_local = local_tz.localize(datetime.combine(start_date, time.min))
    end_local = local_tz.localize(datetime.combine(end_date, time.max))

    times_local = pd.date_range(
        start=start_local,
        end=end_local,
        freq=f"{interval_minutes}min",
        tz=local_tz,
    )

    times_utc = times_local.tz_convert("UTC")

    # Calculate solar position
    location = pvlib.location.Location(latitude, longitude, tz=tz_name)
    solar_position = location.get_solarposition(times_utc)

    result_df = pd.DataFrame({
        "Local Time": times_local,
        "Solar Azimuth (°)": solar_position["azimuth"].values,
        "Solar Altitude (°)": solar_position["apparent_elevation"].values,
    })

    # Format to local time
    result_df["Local Time"] = result_df["Local Time"].dt.strftime("%Y-%m-%d %H:%M:%S")

    # -------------------------------------------------
    # Result Display
    # -------------------------------------------------
    st.subheader(f"Solar Azimuth and Altitude Results (Local Time)")
    st.dataframe(result_df)

    csv = result_df.to_csv(index=False)
    st.download_button(
        "Download CSV",
        data=csv,
        file_name="solar_azimuth_altitude.csv",
        mime="text/csv",
    )
