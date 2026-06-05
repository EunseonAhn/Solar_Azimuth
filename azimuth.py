import streamlit as st
import pandas as pd
import pvlib
from datetime import datetime

st.title("Solar Azimuth and Altitude Calculator")

latitude = st.number_input("Enter Latitude", min_value=-90.0, max_value=90.0, value=0.0)
longitude = st.number_input("Enter Longitude", min_value=-180.0, max_value=180.0, value=0.0)

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date", datetime.today())
with col2:
    end_date = st.date_input("End Date", datetime.today())

# Input: Time Resolution
interval_minutes = st.number_input("Time Resolution (minutes)", min_value=1, max_value=1440, value=60)

# Convert dates to datetime range covering full days (00:00 to 23:59 UTC)
start_datetime = datetime.combine(start_date, datetime.min.time())
end_datetime = datetime.combine(end_date, datetime.max.time())

if start_datetime >= end_datetime:
    st.error("End date must be after start date.")
else:
    times = pd.date_range(start=start_datetime, end=end_datetime, freq=f'{interval_minutes}min', tz='UTC')

    # calc solar position
    location = pvlib.location.Location(latitude, longitude)
    solar_position = location.get_solarposition(times)

    azimuth = solar_position['azimuth']
    altitude = solar_position['apparent_elevation']  # altitude = elevation above horizon

    # table
    st.subheader("Solar Azimuth and Altitude Results")
    result_df = pd.DataFrame({
        'Time (UTC)': times,
        'Solar Azimuth (degrees)': azimuth.values,
        'Solar Altitude (degrees)': altitude.values
    })
    st.dataframe(result_df)

    # Download as CSV
    csv = result_df.to_csv(index=False)
    st.download_button("Download CSV", data=csv, file_name='solar_azimuth_altitude.csv', mime='text/csv')
