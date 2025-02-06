# tecviewmap
"Transports en Commun"view map is a lightweight (client-side) map to locate bus in real-time using open data.

![tecview map](tecview-liege.jpg?raw=true "Tecview map")

While a client-server approach might be more efficient and elegant, it has been developed to be run locally in a single HTML page
with transit data locally stored, and real-time data coming from an API.
This has been tested with GTFS static transit data for Belgium (TEC, from [https://beltac.tec-wl.be](https://beltac.tec-wl.be/))
including routes and stops, and real-time traffic information assumed to be accessible through an API that returns it in JSON format.

The typical use case are individuals willing to know if their buses are on time to infer planning. 
No automatic planning is provided.

##Data preparation
Download data into data/
Process data using python scripts.

#Run locally
Open the HTML page in your browser.


