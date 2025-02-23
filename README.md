## Introduction to tecmap
"Transports en Commun" map is a lightweight map to locate bus in real-time using open data. On the map below, buses coordinates are refreshed every 10 seconds and are colored according to delay (by comparing real-time data to static theoretical timetables which can be displayed by clicking on one bus: red > 5 minutes, 0 < orange < 5 minutes, green on time). A simple filter (by bus line numbers) allows to only display the buses of interest. You can get timelines and other details when you click on a bus marker on the map.

![tecmap](tecmap-liege.jpg?raw=true "Tecmap in Liège, Belgium")

It has been developed using HTML+CSS+Javascript only to be run through a single HTML page without any web framework. It relies on transit data locally stored, and real-time data coming from a remote API.
This has been tested with GTFS static transit data for Wallonia in Belgium (TEC, downloaded from [https://beltac.tec-wl.be](https://beltac.tec-wl.be/))
including routes and stops, and real-time traffic information assumed to be accessible through an API that returns it in JSON format.

The typical use cases are individuals willing to know if their buses are on time to plan their trips, e.g. someone at home who doesn't 
want to wait 10 minutes outside in the cold, or someone who has the possibility of taking several different buses and wants to know which one will arrive first,
or someone at their desk who wants to optimize their life and work until the last minute before their bus comes, or someone having a good time with a loved one 
but not willing to miss the very last bus. ;) Another use case is someone willing to discover new places they can reach with public transport without knowing the existing routes a priori.
Please note no automatic planning is provided, you must use your mental calculation skills to construct your route, which in principle consumes 
less energy than running a routing algorithm on GAFAM servers. ;)

## Data preparation
1. Create `data/` local directory
   
3. Download into ´data/` local directory GTFS routes and stops data (latest version from [https://beltac.tec-wl.be](https://beltac.tec-wl.be/Current%20GTFS/) or [https://busmaps.com/en/belgium/TEC-Transit/tec-transit](https://busmaps.com/en/belgium/TEC-Transit/tec-transit) )
   
5. Convert data using `convert_data.py` Python3 script:

    2.1 `data/stops.txt` will be converted to `data/stops.js`  (contains names of bus stops)
   
    2.2 `data/stop_times.txt` will be converted to `data/stop_times.js`(contains routes with sequences of bus stops and arrival times)
   I recommend to split original data into multiple .js files using the filter_strings, and load in tecmap.html the appropriate js file on-the-fly according e.g. to the day of the week.
   

## Edit tecmap.html
1. Edit the `loadScheduleFile()` function in **tecmap.html** if local files are not located in data/ or named in another way e.g. in the case of multiple files with splitted information per day.
3. Edit **RT_API_URL** in **config.js** so that it refers to the API endpoint that returns real-time traffic data in JSON format (gtfsRealtimeVersion": "1.0"), expected to be formatted as follows:

```
{
    "markers": [
        {
            "vehicleId": "XXX",
            "latitude": 50.632415771484375,
            "longitude": 5.555666923522949,
            "bearing": 141,
            "speed": 6,
            "currentStopSequence": 8,
            "timestamp": 1738589199,
            "stopId": "Llglamb1",
            "trip": {
                "tripId": "46212634-L_PA_2025-25_LG_N3-Sem-N-3-02",
                "startTime": "14:21:00",
                "startDate": "20250203",
                "routeId": "L0021-22065",
                "route_short_name": "21",
                "route_long_name": "Darchis - Laveu - St-Nicolas"
            },
            "agency": "L"
        },
        ...
        ]
}
```


3. Edit **TILE_API_KEY** in **config.js** if you want to use the Transport raster tiles from Thunderforest.com [https://www.thunderforest.com/maps/transport/](https://www.thunderforest.com/maps/transport/), otherwise default OSM [https://openstreetmap.org/](https://openstreetmap.org/) raster tiles will be used.

## Run locally
Open the tecmap.html page in your desktop computer's browser. Or copy the HTML page and data/ to a web server for remote access.

## Future plans, contact
I am aware of the limitations of such a client-side approach. 
Having a database to store routes and stops and an API called from the web client would be more elegant but for the moment I wanted to keep it very simple so that anyone can deploy it easily.
Please feel free to submit Issues or contact me.

## Acknowledgments
The map uses [http://openstreetmap.org/](http://openstreetmap.org/) data and [https://leafletjs.com/](https://leafletjs.com/) Javascript library.





