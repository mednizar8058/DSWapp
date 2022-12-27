import streamlit as st
import pandas as pd
import numpy as np
import os
import pydeck as pdk
import plotly.express as px

data_url = (
    "Motor_Vehicle_Collisions_-_Crashes.csv"
)

st.title("Motor Vehiule Collisions in NY city")
st.markdown("Analysing motor vehicule collisons in NY city using a Streamlit Dashboard !")

# loading data
#@st.cache(persist=True) #caching results
def load_data_by_rows(nrows):
    data = pd.read_csv(data_url, nrows = nrows,names=['CRASH_DATE','CRASH_TIME','BOROUGH','ZIP_CODE','LATITUDE','LONGITUDE','LOCATION','ON_STREET_NAME','CROSS_STREET_NAME','OFF_STREET_NAME','INJURED_PERSONS','KILLED_PERSONS','INJURED_PEDESTRIANS','KILLED_PEDESTRIANS','INJURED_CYCLISTS','KILLED_CYCLISTS','INJURED_MOTORISTS','KILLED_MOTORISTS','CONTRIBUTING_FACTOR_VEHICLE_1','CONTRIBUTING_FACTOR_VEHICLE_2','CONTRIBUTING_FACTOR_VEHICLE_3','CONTRIBUTING_FACTOR_VEHICLE_4','CONTRIBUTING_FACTOR_VEHICLE_5','COLLISION_ID','VEHICLE_TYPE_1','VEHICLE_TYPE_2','VEHICLE_TYPE_3','VEHICLE_TYPE_4','VEHICLE_TYPE_5'],parse_dates=[['CRASH_DATE','CRASH_TIME']])
    data.dropna(subset=['LATITUDE','LONGITUDE'], inplace=True)
    lowercase = lambda x: str(x).lower() #lambda function
    data.rename(lowercase, axis='columns', inplace=True)
    data.rename(columns={'crash_date_crash_time' : 'date/time'}, inplace=True)

    return data

data = load_data_by_rows(100000)
original_data = data



# QUESTION
st.header("Where are the most injured people in NYC")
injured_people = st.slider("Number of injured",0,19)
st.map(data.query("injured_persons >= @injured_people")[['latitude','longitude']].dropna(how='any'))

# QUESTION:
st.markdown("How many collisions occur during a given time of day ")
hour = st.sidebar.slider("Hours",0,23)
data = data[data['date/time'].dt.hour == hour]

st.header("Vehicule collisions between %i:00 and %i:00" % (hour,(hour+1) %24))
midpoint = (np.average(data['latitude']),np.average(data['longitude']))

# write a pydeck figure
st.write(pdk.Deck(
    map_style = "mapbox://styles/mapbox/light-v9",
    initial_view_state = {
        "latitude" : midpoint[0],
        "longitude" : midpoint[1],
        "zoom" : 11,
        "pitch" : 50,
    },
    layers = pdk.Layer(
        "HexagonLayer",
        data = data[["date/time","latitude","longitude"]],
        get_position = ["longitude","latitude"],
        radius = 40,
        extruded = True,
        pickable = True,
        elevation_scale = 4,
        elavation_range = [0,1000],
    )
))

st.subheader("Breakdown by minute between %i:00 and %i:00" % (hour,(hour + 1) %24))
filtered_data = data[
    (data['date/time'].dt.hour >= hour) & (data['date/time'].dt.hour < (hour + 1))
]
hist = np.histogram(filtered_data['date/time'].dt.minute, bins=60, range=(0,60))[0]
chart_data = pd.DataFrame({'minute' : range(60), 'crashes' : hist})
figure = px.bar(chart_data, x='minute', y='crashes', hover_data = ['minute','crashes'], height=400)
st.write(figure)

#
st.header("Top 5 dangerous streets by affected type")
select = st.selectbox("Affected type of people",['Pedestrians','Cyclists','Motorists'])

if select == 'Pedestrians':
    st.write(original_data
    .query("injured_pedestrians >= 1")[['on_street_name','injured_pedestrians']]
    .sort_values(by=['injured_pedestrians'], ascending = False)
    .dropna(how = 'any')[:5])

if select == 'Cyclists':
    st.write(original_data
    .query("injured_cyclists >= 1")[['on_street_name','injured_cyclists']]
    .sort_values(by=['injured_cyclists'], ascending = False)
    .dropna(how = 'any')[:5])

if select == 'Motorists':
    st.write(original_data
    .query("injured_motorists >= 1")[['on_street_name','injured_motorists']]
    .sort_values(by=['injured_motorists'], ascending = False)
    .dropna(how = 'any')[:5])

if st.checkbox("Show raw data", False):
    st.subheader("Raw data")
    st.write(data)
