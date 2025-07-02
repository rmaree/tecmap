## Introduction to tecmap
"Transports en Commun" map is a lightweight map to locate bus in real-time using open data. On the map below, buses coordinates are refreshed every 10 seconds and are colored according to delay (by comparing real-time data to static theoretical timetables which can be displayed by clicking on one bus: red > 5 minutes, 0 < orange < 5 minutes, green on time). A simple filter (by bus line numbers) allows to only display the buses of interest (e.g. "21 58" will display buses following lines 21 and 58; "2?guill 58?guill" will display buses of line 2 that will pass through a stop which name includes "guill" as well as expected time schedule, and buses nr 58 that will pass through a stop name including "guill" which allow to organize your commute based on real-time data). You can get timelines and other details when you click on a bus marker on the map.

![tecmap](tecmap-liege.jpg?raw=true "Tecmap in Liège, Belgium")

It has been developed using HTML+CSS+Javascript only to be run through a single HTML page without any web framework. It relies on transit data locally stored, and real-time data coming from a remote API using ProtoBuf format (for data in Wallonia you have to submit a request to get the data here: [https://www.letec.be/View/Open_Data_of_TEC/4296]).
This has been tested with GTFS static transit data for Wallonia in Belgium (TEC, downloaded from [https://beltac.tec-wl.be](https://beltac.tec-wl.be/))
including routes and stops, and real-time traffic information assumed to be accessible through an API that returns it in ProtoBuf format.

The typical use cases are individuals willing to know if their buses are on time to plan their trips, e.g. someone at home who doesn't 
want to wait 10 minutes outside in the cold, or someone who has the possibility of taking several different buses and wants to know which one will arrive first,
or someone at their desk who wants to optimize their life and work until the last minute before their bus comes, or someone having a good time with a loved one 
but not willing to miss the very last bus. ;) Another use case is someone willing to discover new places they can reach with public transport without knowing the existing routes a priori.
Please note no automatic planning is provided, you must use your mental calculation skills to construct your route, which in principle consumes 
less energy than running a routing algorithm on GAFAM servers. ;)

## Data preparation
1. Create `data/` local directory
   
3. Download into ´data/` local directory GTFS static routes and stops data (latest version from [https://beltac.tec-wl.be](https://beltac.tec-wl.be/Current%20GTFS/) or [https://busmaps.com/en/belgium/TEC-Transit/tec-transit](https://busmaps.com/en/belgium/TEC-Transit/tec-transit) )
   
5. Convert GTFS static and dynamic data using `python3 convert_data.py` script:

    2.1 static `data/stops.txt` will be converted to `data/stops.js`  (contains names of bus stops)
   
    2.2 dynamic `data/stop_times.txt` (contains routes with sequences of bus stops and arrival times) will be converted to multiple `data/stop_times.js` files splitted by days using filter_strings 
   The original data is splitted into multiple .js files using the filter_strings to avoid loading too much data in the browser. In tecmap.html the appropriate js file is loaded on-the-fly according e.g. to the day of the week and holidays (Belgium).

    2.3 static `data/routes.txt` will be converted to `data/routes.js`  (contains route short and long names)
   

## Edit tecmap.html
1. Edit the `loadScheduleFile()` function in **tecmap.html** if local files are not located in data/ or named in another way if you modified the convert_data.py script.
3. Edit **RT_API_URL** in **config.js** so that it refers to the API endpoint that returns real-time traffic data in ProtoBuf format using the Protocol definition file for GTFS Realtime from https://github.com/google/transit/blob/master/gtfs-realtime/proto/gtfs-realtime.proto. In our code function transformGTFSData, we convert the Protobuf data into a JSON structure for easier manipulation, formatted as follows:

```
{
  "vehicles": [
    {
      "vehicleId": "3427",
      "latitude": 50.46605682373047,
      "longitude": 4.186469554901123,
      "speed": null,
      "currentStopSequence": 31,
      "timestamp": 1743537125,
      "stopId": "H2ll179f",
      "trip": {
        "tripId": "47395794-H_2025-H25_P2-Sem-N-3-03",
        "startTime": "21:12:00",
        "startDate": "20250401",
        "routeId": "H2030-22858",
        "route_short_name": "30",
        "route_long_name": "Strépy-Bracquegnies - Anderlues"
      },
      "agency": "H2030"
    },
    {
      "vehicleId": "3231",
      "latitude": 50.45465087890625,
      "longitude": 3.9430530071258545,
      "speed": 22,
      "currentStopSequence": 40,
      "timestamp": 1743537049,
      "stopId": "H1ms401a",
      "trip": {
        "tripId": "47397951-H_2025-H25_P2-Sem-N-3-03",
        "startTime": "21:17:00",
        "startDate": "20250401",
        "routeId": "H1022-22900",
        "route_short_name": "22",
        "route_long_name": "Mons - Binche"
      },
      "agency": "H1022"
    },
   ...
```


3. Edit **TILE_API_KEY** in **config.js** if you want to use the Transport raster tiles from Thunderforest.com [https://www.thunderforest.com/maps/transport/](https://www.thunderforest.com/maps/transport/), otherwise default OSM [https://openstreetmap.org/](https://openstreetmap.org/) raster tiles will be used.

## Run locally
Open the tecmap.html page in your desktop computer's browser. Or copy the HTML page and data/ to a web server for remote access.

## Future plans, contact
I am aware of the limitations of such a client-side approach. 
Having a database to store routes and stops and an API called from the web client would be more elegant but for the moment I wanted to keep it very simple so that anyone can deploy it easily.
Please feel free to submit Issues or contact me.

## Acknowledgments
The map uses the open access [http://openstreetmap.org/](http://openstreetmap.org/) data and the open-source [https://leafletjs.com/](https://leafletjs.com/) Javascript library.





