## Introduction to tecmap
"Transports en Commun" map is a lightweight map to locate bus in real-time using open data.

![tecview map](tecview-liege.jpg?raw=true "Tecview map")

It has been developed using HTML+CSS+Javascript only to be run through a single HTML page. It relies on transit data locally stored, and real-time data coming from a remote API.
This has been tested with GTFS static transit data for Wallonia in Belgium (TEC, downloaded from [https://beltac.tec-wl.be](https://beltac.tec-wl.be/))
including routes and stops, and real-time traffic information assumed to be accessible through an API that returns it in JSON format.

The typical use cases are individuals willing to know if their buses are on time to plan their trips, e.g. someone at home who doesn't 
want to wait 10 minutes outside in the cold, or someone at their desk who wants to optimize their life and work until the last minute before their bus comes,
or someone having a good time with a loved one but not willing to miss the very last bus. ;)
Please note no automatic planning is provided, you must use your mental calculation skills to construct your route, which in principle consumes 
less energy than running a routing algorithm on GAFAM servers. ;)

## Data preparation
Download GTFS routes and stops data 
Process data using python scripts and put processed Javascript files into the data/ directory.

## Edit tecmap.html
1. Edit your **tecmap.html** `<script src="...">` if local files are not located in data/ or named in another way.
2. Edit **RT_API_URL** so that it refers to the API endpoint that returns real-time traffic data in JSON format (gtfsRealtimeVersion": "1.0"), expected to be formatted as follows:

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


3. Edit **TILE_API_KEY** if you want to use the Transport raster tiles from Thunderforest.com [https://www.thunderforest.com/maps/transport/](https://www.thunderforest.com/maps/transport/), otherwise default OSM raster tiles will be used.

## Run locally
Open the tecmap.html page in your browser.


