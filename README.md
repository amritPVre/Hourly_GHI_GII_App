# Hourly_GHI_GII_App
# Daily Clear-sky GHI & GII Calculation App
Pvlib Library used to develop this Calculation (Forecasting) App. Clear-sky (based on Ineichen model) Method has been followed to calculate the GHI and GII (Plane of Array) Values in 10 minutes’ interval for throughout the day. This App can predict Hourly GHI and GII for each point of coordinates in the world, 365 days a year.
This App has Four Main Parts –
1.	Input Section – You need to provide inputs like project site’s Timezone, Location coordinates, desired Tilt of PV array, Orientation of PV array as Azimuth, and Two Date picker.
2.	Hourly GHI & GII Calculation – This section will take 2 dates of a year and generate sub-hourly GHI & GII data for you. And Key metrics like Total Daily GHI (Kwh/m2) GII (Kwh/m2) values, Peak GII (W/m2) and the Daily GII vs GHI gains for you.
3.	Summer & Winter Solstice – Same as the above section, this part too gives sub-hourly and daily GHI, GII values for TWO pre-determined days that are 21st June and 21st December, based on the input section.
4.	Sunpath Plotting – This is the last section which generates Cartesian sunpath for the location coordinate that you have selected in the input section.
