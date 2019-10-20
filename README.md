# WeatherMinner

Mine weather data from NOAA to csv using python3.6

## Obtaining a stations_list.txt

`curl -O https://nowdata.rcc-acis.org/<YourAbreviationHere>/station_list.txt`


## Basic usage
`python3.6 weatherMinner.py -s <startdata> -e <enddate>`

weatherMinner will use the station list file that you obtained from above
and start to create local copies of csv files.
