# -*- coding: utf-8 -*-
"""
Created on Sun Aug 15 19:57:43 2021

@author: Amrit
"""



import streamlit as st
import plotly.express as px
import pvlib as pvlib
import numpy as np
import pandas as pd
import pytz
import time
import datetime
import base64
import folium
from pvlib import location
from pvlib import irradiance
from pvlib import solarposition
import matplotlib.pyplot as plt
from datetime import datetime, date, time
from streamlit_folium import folium_static


#---------------------------------------------------------------------------

st.set_page_config(
    page_title='Hourly GHI-GII',page_icon=None,layout="centered",initial_sidebar_state="expanded",)



time_zone=pytz.all_timezones[:]


st.header('Daily Clearsky GHI & GII Calculation App')
st.caption('Pvlib Library used to develop this Calculation (Forecasting) App. Clearsky (based on Ineichen model) Method has been followed to calculate the GHI and GII (Plane of Array) Values in 10 minutes interval for through out the day. This App can predict Hourly GHI and GII for each point of coordinates in the world, 365 days a year. \n')
st.subheader("")

#-----------------------Timezone selection Sidebar-----------------------

st.sidebar.subheader("Select Your Local Time zone: ")
default_ix=time_zone.index('Europe/Berlin')
tz = st.sidebar.selectbox('',time_zone,index=default_ix)
st.write('Your Project Site Timezone is:', tz)

#------------------------------------------------------------------------


#--------------------------date time picker-----------------------------


st.sidebar.subheader("Pick TWO Dates for TWO Seasons ")
sd_wd=st.sidebar.columns(2)
sd=sd_wd[0].date_input('Date#1')
wd=sd_wd[1].date_input('Date#2')
st.write('The Selected Dates are:', sd,wd)


#------------------------------------------------------------------------

#-----------------------Take inputs for lat, lon------------------------
lat_lon=st.columns(2)
lat = lat_lon[0].number_input('Insert the Latitude:',value=52.4830986)
lon = lat_lon[1].number_input('Insert the Longitude:',value=13.4920913)
st.write(f'Selected Site Coordinate is :{lat}°, {lon}°')

print('lat is ',lat)


#------------------------------------------------------------------------

#---------------------Tilt and Azimuth Selection-----------------------
tilt_range=range(0,91)
aimuth_range=range(0,361)

tilt = st.sidebar.select_slider('Set the Tilt Angle of PV Array:',options=tilt_range,value=22)
surface_azimuth = st.sidebar.select_slider('Define the PV Array Azimuth:',options=aimuth_range,value=180)
st.write(f'PV Array Tilt and Azimuth are {tilt}° & {surface_azimuth}°')

#------------------------------------------------------------------------

#------------------------Location Map------------------------------------
# center on Coordinate
m = folium.Map(location=(lat,lon), zoom_start=8,
               width='100%',height='80%',control_scale=True,
               position='relative',zoom_control=True,
               )

  # add marker for Coordinate
tooltip = "Proposed Solar PV Site"
folium.Marker(
    (lat,lon), popup="Proposed Solar PV Site", tooltip=tooltip
   ).add_to(m)
# call to render Folium map in Streamlit
folium_static(m)

#-----------------------------------------------------------------------

#----------------------Main PVlib Function------------------------------

# Create location object to store lat, lon, timezone
site = location.Location(lat, lon, tz=tz)



# Calculate clear-sky GHI and transpose to plane of array
# Define a function so that we can re-use the sequence of operations with
# different locations
def get_irradiance(site_location, date, tilt, surface_azimuth):
    # Creates one day's worth of 10 min intervals
    times = pd.date_range(date, freq='10min', periods=6*24,
                          tz=site_location.tz)
    # Generate clearsky data using the Ineichen model, which is the default
    # The get_clearsky method returns a dataframe with values for GHI, DNI,
    # and DHI
    clearsky = site_location.get_clearsky(times)
    # Get solar azimuth and zenith to pass to the transposition function
    solar_position = site_location.get_solarposition(times=times)
    # Use the get_total_irradiance function to transpose the GHI to POA
    POA_irradiance = irradiance.get_total_irradiance(
        surface_tilt=tilt,
        surface_azimuth=surface_azimuth,
        dni=clearsky['dni'],
        ghi=clearsky['ghi'],
        dhi=clearsky['dhi'],
        solar_zenith=solar_position['apparent_zenith'],
        solar_azimuth=solar_position['azimuth'])
    # Return DataFrame with only GHI and POA
    return pd.DataFrame({'GHI': clearsky['ghi'],
                         'POA': POA_irradiance['poa_global']})


#---------------------Generating & Plotting Day#1 & Day#2 Data-------------

# Get irradiance data for summer and winter solstice, assuming 25 degree tilt
# and a south facing array
day1_irradiance = get_irradiance(site, sd, tilt, surface_azimuth)
day2_irradiance = get_irradiance(site, wd, tilt, surface_azimuth)

# Convert Dataframe Indexes to Hour:Minute format to make plotting easier
day1_irradiance.index = day1_irradiance.index.strftime("%H:%M")
day2_irradiance.index = day2_irradiance.index.strftime("%H:%M")

#--------------------------------------------------------

# Plot GHI vs. POA for winter and summer using Matplotlib
#fig1, (ax1, ax2) = plt.subplots(1, 2, sharey=True)
#summer_irradiance['GHI'].plot(ax=ax1, label='GHI')
#summer_irradiance['POA'].plot(ax=ax1, label='POA')
#winter_irradiance['GHI'].plot(ax=ax2, label='GHI')
#winter_irradiance['POA'].plot(ax=ax2, label='POA')
#ax1.set_xlabel('Time of day (Summer)')
#ax2.set_xlabel('Time of day (Winter)')
#ax1.set_ylabel('Irradiance ($W/m^2$)')
#ax1.legend()
#ax2.legend()

#st.pyplot(fig1)

#--------------------------------------------------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    pass
with col3:
    pass
with col2 :
    st.subheader('Daily Irradiance Values')

#--------------------Metrics Value Day1-----------------------------------

#--------Extracting the Max Value of GHI & POA for both the days-----
max_ghi_d1=day1_irradiance['GHI'].max()
max_gii_d1=day1_irradiance['POA'].max()
max_ghi_d2=day2_irradiance['GHI'].max()
max_gii_d2=day2_irradiance['POA'].max()

#Getting Total Daily values of GHI & GII for both the days
sum_d1=day1_irradiance.sum(axis=0, skipna=True)
sum_d2=day2_irradiance.sum(axis=0, skipna=True)

#Daily GII Gain for Both the days
gain_d1="{:.0%}". format((sum_d1.POA-sum_d1.GHI)/sum_d1.GHI)
gain_d2="{:.0%}". format((sum_d2.POA-sum_d2.GHI)/sum_d2.GHI)


d1_1, d1_2, d1_3=st.columns(3)
d1_1.metric(label="GHI (kWh/m\u00b2/day)", value="{:.3f}".format(sum_d1.GHI/1000))
d1_2.metric(label="GII (kWh/m\u00b2/day)", value="{:.3f}".format(sum_d1.POA/1000), delta=gain_d1)
d1_3.metric(label="Peak GII (W/m\u00b2)", value="{:.2f}".format(max_gii_d1), 
            delta="{:.0%}". format((max_gii_d1-max_ghi_d1)/max_ghi_d1))


#Ploting the GHI to POA for 1st date
fig1 = px.line(day1_irradiance, y=['GHI','POA'],title=f'Hourly Solar Irradiance (W/m\u00b2) for {sd}')
fig1.update_layout(title_text=f'<b>Hourly Solar Irradiance (W/m\u00b2) for {sd}</b>', title_x=0.5,
                   xaxis_title="Time (in HH:MM)",yaxis_title="Irradiance (W/m\u00b2)")
st.plotly_chart(fig1)
#--------------------Metrics Value for Day 2-----------------------------------

d2_1, d2_2, d2_3=st.columns(3)
d2_1.metric(label="GHI (kWh/m\u00b2/day)", value="{:.3f}".format(sum_d2.GHI/1000))
d2_2.metric(label="GII (kWh/m\u00b2/day)", value="{:.3f}".format(sum_d2.POA/1000), delta=gain_d2)
d2_3.metric(label="Peak GII (W/m\u00b2)", value="{:.2f}".format(max_gii_d2), 
            delta="{:.0%}". format((max_gii_d2-max_ghi_d2)/max_ghi_d2))

#Ploting the GHI to POA for 2nd date
fig2 = px.line(day2_irradiance, y=['GHI','POA'],title=f'Hourly Solar Irradiance (W/m\u00b2) for {wd}')
fig2.update_layout(title_text=f'<b>Hourly Solar Irradiance (W/m\u00b2) for {wd}</b>', title_x=0.5,
                   xaxis_title="Time (in HH:MM)",yaxis_title="Irradiance (W/m\u00b2)")
st.plotly_chart(fig2)

#--------------------Showing Dataframe as Data Table---------------------
day1_irradiance.rename(columns={'GHI':'GHI (W/m\u00b2)','POA':'GII (W/m\u00b2)'}, inplace=True)
day2_irradiance.rename(columns={'GHI':'GHI (W/m\u00b2)','POA':'GII (W/m\u00b2)'}, inplace=True)

col1,col2=st.columns(2)
col1.dataframe(day1_irradiance[0:])
col2.dataframe(day2_irradiance[0:])



#----------------------------Download csv data---------------------------
col1,col2=st.columns(2)

def st_pandas_to_csv_download_link(_df:pd.DataFrame, file_name:str = "dataframe.csv"): 
    csv_exp = _df.to_csv(index=False)
    b64 = base64.b64encode(csv_exp.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}" download="{file_name}" > Download Day-1 Irradiance Data (W/m\u00b2) </a>'
    col1.markdown(href, unsafe_allow_html=True)

data_d1=st_pandas_to_csv_download_link(day1_irradiance, file_name = "Day#1_irradiance.csv")


def st_pandas_to_csv_download_link(_df:pd.DataFrame, file_name:str = "dataframe.csv"): 
    csv_exp = _df.to_csv(index=False)
    b64 = base64.b64encode(csv_exp.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}" download="{file_name}" > Download Day-2 Irradiance Data (W/m\u00b2) </a>'
    col2.markdown(href, unsafe_allow_html=True)

data_d2=st_pandas_to_csv_download_link(day2_irradiance, file_name = "Day#2_irradiance.csv")



#-------------------Summer & Winter Irradiance Plotting--------------
col1, col2, col3 = st.columns(3)

with col1:
    pass
with col3:
    pass
with col2 :
    st.subheader('Daily Irradiance Values')


# Get irradiance data for summer and winter solstice
summer_irradiance = get_irradiance(site, '06-21-2020', tilt, surface_azimuth)
winter_irradiance = get_irradiance(site, '12-21-2020', tilt, surface_azimuth)




#figs = px.line(summer_irradiance, y=['GHI','POA'],title='Hourly Solar Irradiance - GHI & GII (W/m\u00b2)')
#figs.update_layout(title_text='<b>Hourly Data - Summer Solstice (21st Jun)</b>', title_x=0.5,xaxis_title="Time (in HH:MM)",yaxis_title="Irradiance (W/m\u00b2)")


#figw = px.line(winter_irradiance, y=['GHI','POA'],title='Hourly Solar Irradiance - GHI & GII (W/m\u00b2)')
#figw.update_layout(title_text='<b>Hourly Data - Winter Solstice (21st Dec)</b>', title_x=0.5,xaxis_title="Time (in HH:MM)",yaxis_title="Irradiance (W/m\u00b2)")

figs,figw=st.columns(2)


figs.plotly_chart(px.line(summer_irradiance, y=['GHI','POA'],
                          title='<b>Hourly Data-Summer Solstice (21st Jun)</b>'),xaxis_title="Time (in HH:MM)",yaxis_title="Irradiance (W/m\u00b2)",use_container_width=True,sharing="streamlit")

figw.plotly_chart(px.line(winter_irradiance, y=['GHI','POA'],title='<b>Hourly Data-Winter Solstice (21st Dec)</b>'),use_container_width=True,sharing="streamlit",xaxis_title="Time (in HH:MM)",yaxis_title="Irradiance (W/m\u00b2)")


summer_irradiance.index = summer_irradiance.index.strftime("%H:%M")
winter_irradiance.index = winter_irradiance.index.strftime("%H:%M")

#--------------------Metrics Value Summer & Winter Solstice-----------------------------------

#--------Extracting the Max Value of GHI & POA for both the days-----
max_ghi_s=summer_irradiance['GHI'].max()
max_gii_s=summer_irradiance['POA'].max()
max_ghi_w=winter_irradiance['GHI'].max()
max_gii_w=winter_irradiance['POA'].max()

#Getting Total Daily values of GHI & GII for both the days
sum_s=summer_irradiance.sum(axis=0, skipna=True)
sum_w=winter_irradiance.sum(axis=0, skipna=True)

#Daily GII Gain for Both the days
gain_s="{:.0%}". format((sum_s.POA-sum_s.GHI)/sum_s.GHI)
gain_w="{:.0%}". format((sum_w.POA-sum_w.GHI)/sum_w.GHI)


#--------------------Metrics Value for Summer Solstice----------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    pass
with col3:
    pass
with col2 :
    st.subheader('Summer Solstice')


s_1, s_2, s_3=st.columns(3)
s_1.metric(label="GHI (kWh/m\u00b2/day)", value="{:.3f}".format(sum_s.GHI/1000))
s_2.metric(label="GII (kWh/m\u00b2/day)", value="{:.3f}".format(sum_s.POA/1000), delta=gain_s)
s_3.metric(label="Peak GII (W/m\u00b2)", value="{:.2f}".format(max_gii_s), 
            delta="{:.0%}". format((max_gii_s-max_ghi_s)/max_ghi_s))


#--------------------Metrics Value for Winter Solstice-----------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    pass
with col3:
    pass
with col2 :
    st.subheader('Winter Solstice')


w_1, w_2, w_3=st.columns(3)
w_1.metric(label="GHI (kWh/m\u00b2/day)", value="{:.3f}".format(sum_w.GHI/1000))
w_2.metric(label="GII (kWh/m\u00b2/day)", value="{:.3f}".format(sum_w.POA/1000), delta=gain_w)
w_3.metric(label="Peak GII (W/m\u00b2)", value="{:.2f}".format(max_gii_w), 
            delta="{:.0%}". format((max_gii_w-max_ghi_w)/max_ghi_w))




summer_irradiance.rename(columns={'GHI':'GHI (W/m\u00b2)','POA':'GII (W/m\u00b2)'}, inplace=True)
winter_irradiance.rename(columns={'GHI':'GHI (W/m\u00b2)','POA':'GII (W/m\u00b2)'}, inplace=True)

col1,col2=st.columns(2)
col1.dataframe(summer_irradiance)
col2.dataframe(winter_irradiance)


ssc1_ssc2=st.sidebar.columns(2)

def convert_df(df):
    #Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')
csv = convert_df(summer_irradiance)
ssc1=ssc1_ssc2[0].download_button(label="Summer.Solstice",
                   data=csv,
                   file_name='Summer__Solstice.csv',
                   mime='text/csv',
                   )

csv1 = convert_df(winter_irradiance)
ssc2=ssc1_ssc2[1].download_button(label="Winter.Solstice",
                   data=csv1,
                   file_name='Winter__Solstice.csv',
                   mime='text/csv',
                   )

#--------------------------Sunpath Plotting--------------------------
col1, col2, col3 = st.columns(3)

with col1:
    pass
with col3:
    pass
with col2 :
    st.title('SunPath Plotting')








times = pd.date_range('2019-01-01 00:00:00', '2020-01-01', closed='left',
                      freq='H', tz=tz)

solpos = solarposition.get_solarposition(times, lat, lon)
# remove nighttime
solpos = solpos.loc[solpos['apparent_elevation'] > 0, :]

figz, ax = plt.subplots()
points = ax.scatter(solpos.azimuth, solpos.apparent_elevation, s=2,
                    c=solpos.index.dayofyear, label=None)
figz.colorbar(points)

for hour in np.unique(solpos.index.hour):
    # choose label position by the largest elevation for each hour
    subset = solpos.loc[solpos.index.hour == hour, :]
    height = subset.apparent_elevation
    pos = solpos.loc[height.idxmax(), :]
    ax.text(pos['azimuth'], pos['apparent_elevation'], str(hour))

for date in pd.to_datetime(['2020-03-21', '2020-06-21', '2020-12-21']):
    times = pd.date_range(date, date+pd.Timedelta('24h'), freq='5min', tz=tz)
    solpos = solarposition.get_solarposition(times, lat, lon)
    solpos = solpos.loc[solpos['apparent_elevation'] > 0, :]
    label = date.strftime('%Y-%m-%d')
    ax.plot(solpos.azimuth, solpos.apparent_elevation, label=label)

ax.figure.legend(loc='upper left')
ax.set_xlabel('Solar Azimuth (degrees)')
ax.set_ylabel('Solar Elevation (degrees)')

st.pyplot(figz)

    


#------------------------------------




