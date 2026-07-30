# ----------------------------------------------------------------------------
# Author: Raphaël Marée
# License: Apache License 2.0
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ----------------------------------------------------------------------------

import pandas as pd
import json
import csv
import sys
import os

#Input files (GTFS in text format, e.g. https://opendata.tec-wl.be/Current%20GTFS/)
stops_csv_input_filename = "data/stops.txt" # Fichier GTFS csv incluant toutes les routes/trips
routes_csv_input_filename = "data/routes.txt" #fichier GTFS statique CSV incluant toutes les routes
stop_times_csv_input_filename = "data/stop_times.txt"  # Fichier GTFS csv incluant tous les stop_times
stops_osmjson_input_filename = "data/stops_osm.json"  #Fichier json provenant d'Overpass turbo (OpenStreetmap) avec tous les arrêts TEC
#[out:json][timeout:40];           
#area["ISO3166-1"="BE"]->.be;
#(
#	     node["highway"="bus_stop"]["operator"="TEC"](area.be);
#	     node["public_transport"="platform"]["operator"="TEC"](area.be);
#);
#out body geom;



#Output Javascript files
output_dir = "data"
stops_js_output_filename = "data/stops_with_coords.js"
routes_js_output_filename = "data/routes.js" #fichier JS de sortie indexé par route_id
stop_times_js_output_filename_SEM = "data/stop_times-SEM.js"
stop_times_js_output_filename_MER = "data/stop_times-MER.js"
stop_times_js_output_filename_SAM = "data/stop_times-SAM.js"
stop_times_js_output_filename_DIM = "data/stop_times-DIM.js" # Fichier js de sortie
stop_times_js_output_filename_VAC = "data/stop_times-SEM_VAC.js"    # Fichier js de sortie, à renommer si e.g. par jour stop_times-DIM.js

#Filter strings found in stop_times for day types, depends on naming by public transport
filter_strings_SEM_only = ["-Sem-N-"] #semaines normales
filter_strings_DIM_only = ["-Dimanche-"]
filter_strings_MER_only = ["-Mercredi-"]
filter_strings_SAM_only = ["-Samedi-"]
filter_strings_SEM_VAC_only = ["-Sem-Vac-","-Sem-Cong"]

#Filter strings found in stop_times corresponding to the different regions, depends on naming by public transport
REGIONS = {
    "LG": ["-L_PA_"], #Liege-verviers
    "CHOI": ["-choi-"], #Charleroi
    "BW": ["-BW_"], #Brabant Wallon
    "H": ["-H_"], #Hainaut
    "NAM": ["-N_"], #Namur
    "LUX": ["-X-"], #Luxembourg
}


NETWORK_CODES = {
    "TECL": "L",
    "TECX": "X",
    "TECN": "N",
    "TECH": "H",
    "TECC": "C",
}


# ----------------------------------------------------------------------
# Function to convert csv routes.txt to JS dictionary
def convert_routes_csv_to_js2(input_csv, output_js):
    routes = {}
    with open(input_csv, mode="r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            rid = row["route_id"]
            routes[rid] = {
                "rsn": row["route_short_name"],
                "rln": row["route_long_name"]
            }

    js_content = f"const routeData={json.dumps(routes, separators=(',', ':'))};"
    
    with open(output_js, mode="w", encoding="utf-8") as jsfile:
        jsfile.write(js_content)
    print(f"Conversion static routes file done '{output_js}' generated successfully.")

        
#--------------------------------------------------------------------------------------
# Function to convert stop_times from csv line format to JS dictionary, by region and daytypes (filter_strings)
def convert_stop_times_csv_to_js_by_region(csv_filename, output_dir, day_type, filter_strings, regions):
    
    # One dict per region
    horaires_by_region = {region: {} for region in regions}

    with open(csv_filename, mode="r", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        
        for row in reader:
            trip_id = row["trip_id"]

            # Filter day type
            if filter_strings and not any(f in trip_id for f in filter_strings):
                continue

            # Detect region
            matched_region = None
            for region, patterns in regions.items():
                if any(p in trip_id for p in patterns):
                    matched_region = region
                    break

            if not matched_region:
                continue  # ignore if no region matched

            horaires_data = horaires_by_region[matched_region]

            if trip_id not in horaires_data:
                horaires_data[trip_id] = []

            horaires_data[trip_id].append({
                "a": row["arrival_time"][:5],
                "s": row["stop_id"],
                "seq": int(row["stop_sequence"])
            })

    # Write files per region and day types
    for region, data in horaires_by_region.items():

        if not data:
            continue

        json_data = json.dumps(data, separators=(",", ":"), ensure_ascii=False)

        filename = os.path.join(output_dir, f"stop_times_{region}_{day_type}.js")

        with open(filename, mode="w", encoding="utf-8") as js_file:
            js_file.write(f"window.horairesChunk = {json_data};\n")

        print(f"Conversion done: {filename}")

        


# -------------------------------------------------------------------------------------
#Convert GTFS csv file with stops to JS object (id,name)
def convert_stops_csv_to_js(csv_filename, js_filename):
    stops = {}

    with open(csv_filename, mode="r", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            stop_id = row["stop_id"]
            stop_name = row["stop_name"]
            stops[stop_id] = stop_name  # Stocker stop_id comme clé et stop_name comme valeur

    with open(js_filename, mode="w", encoding="utf-8") as js_file:
        js_file.write(f"const stopsData = {stops};\n")

    print(f"Conversion static stops done : {js_filename}")



# -------------------------------------------------------------------------------------
#Convert GTFS csv file with stops to JS object (id,name) with lat,lng coordinates
def clean_stop_name(name):
    return name.replace("(terminus)", "").strip()

def convert_stops_csv_to_js_with_coords(csv_filename, js_filename):
    stops = {}

    with open(csv_filename, mode="r", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        
        for row in reader:
            stop_id = row["stop_id"]
            stop_name = row["stop_name"]
            lat = float(row["stop_lat"])
            lon = float(row["stop_lon"])
            stops[stop_id] = {
                "n": clean_stop_name(stop_name),
                "la": lat,
                "lo": lon
            }

    json_data = json.dumps(stops, separators=(",", ":"), ensure_ascii=False)

    with open(js_filename, mode="w", encoding="utf-8") as js_file:
        js_file.write(f"const stopsData = {json_data};\n")

    print(f"Conversion static stops done : {js_filename}")




def convert_stops_csv_to_js_with_coords_and_osm(csv_filename,
                                                js_filename,
                                                osm_json_filename=None):

    # ------------------------------------------------------------------
    # 1) Lecture du GTFS
    # ------------------------------------------------------------------

    stops = {}

    with open(csv_filename, mode="r", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:

            stop_id = row["stop_id"]

            stops[stop_id] = {
                "n": clean_stop_name(row["stop_name"]),
                "la": float(row["stop_lat"]),
                "lo": float(row["stop_lon"])
            }

    # ------------------------------------------------------------------
    # 2) Enrichissement avec OSM (optionnel)
    # ------------------------------------------------------------------

    if osm_json_filename:

        with open(osm_json_filename, encoding="utf-8") as f:
            osm = json.load(f)

        for element in osm["elements"]:

            tags = element.get("tags", {})

            # Recherche du ref:TEC*
            stop_id = None

            for key, value in tags.items():
                if key.startswith("ref:TEC"):
                    stop_id = value
                    break

            if not stop_id:
                continue

            if stop_id not in stops:
                continue

            stop = stops[stop_id]

            # id OSM
            stop["oid"] = element["id"]

            #we assume lat and lon are more precise on OSM due to user displacement editing,
            #so we erase la,lo from GTFS
            stop["la"] = element["lat"]
            stop["lo"] = element["lon"]
            
            # réseau
            if "network" in tags:
                stop["net"] = NETWORK_CODES.get(tags["network"], tags["network"])
            #if "network" in tags:
            #    stop["net"] = tags["network"]

            # lignes
            for key, value in tags.items():
                if key.startswith("route_ref:TEC"):
                    stop["rr"] = value
                    break

            # zone
            if "zone:TEC" in tags:
                stop["z"] = tags["zone:TEC"]

            # équipements (uniquement si "yes")
            if tags.get("shelter") == "yes":
                stop["sh"] = 1

            if tags.get("bench") == "yes":
                stop["be"] = 1

            if tags.get("bin") == "yes":
                stop["bi"] = 1

            if tags.get("lit") == "yes":
                stop["li"] = 1

            if tags.get("tactile_paving") == "yes":
                stop["ta"] = 1

            # photo Panoramax
            if "panoramax" in tags:
                stop["pa"] = tags["panoramax"]

    # ------------------------------------------------------------------
    # 3) Export JS compact
    # ------------------------------------------------------------------

    json_data = json.dumps(
        stops,
        separators=(",", ":"),
        ensure_ascii=False
    )

    with open(js_filename, "w", encoding="utf-8") as js_file:
        js_file.write(f"const stopsData={json_data};")

    print(f"Conversion static stops done : {js_filename}")


    
    
# -------------------------------------------------------------------------------------
# Execute conversions for static data
convert_routes_csv_to_js2(routes_csv_input_filename, routes_js_output_filename)
#convert_stops_csv_to_js(stops_csv_input_filename, stops_js_output_filename)
#convert_stops_csv_to_js_with_coords(stops_csv_input_filename, stops_js_output_filename)
convert_stops_csv_to_js_with_coords_and_osm(stops_csv_input_filename, stops_js_output_filename,stops_osmjson_input_filename)

exit
#generate horaires data for each region on SEM, SEM_VAC, DIM, MER, SAM days
convert_stop_times_csv_to_js_by_region(
    stop_times_csv_input_filename,
    output_dir,
    "SEM",
    filter_strings_SEM_only,
    REGIONS
)
convert_stop_times_csv_to_js_by_region(
    stop_times_csv_input_filename,
    output_dir,
    "SEM_VAC",
    filter_strings_SEM_VAC_only,
    REGIONS
)
convert_stop_times_csv_to_js_by_region(
    stop_times_csv_input_filename,
    output_dir,
    "DIM",
    filter_strings_DIM_only,
    REGIONS
)
convert_stop_times_csv_to_js_by_region(
    stop_times_csv_input_filename,
    output_dir,
    "MER",
    filter_strings_MER_only,
    REGIONS
)
convert_stop_times_csv_to_js_by_region(
    stop_times_csv_input_filename,
    output_dir,
    "SAM",
    filter_strings_SAM_only,
    REGIONS
)



#not used anymore, for stats only
#Lister nombre de valeurs differentes dans stop_times avec filtre
def list_unique_values(csv_filename):
    unique_values = set()

    with open(csv_filename, mode="r", encoding="utf-8") as csv_file:
        reader = csv.reader(csv_file)
        next(reader, None)  # Ignorer l'en-tête si présent
        for row in reader:
            if row and "_LG_" in row[0]:  # Vérifier que la ligne n'est pas vide
                unique_values.add(row[0])  # Ajouter la première colonne à l'ensemble

    return sorted(unique_values)  # Trier les valeurs pour un affichage ordonné

# Exemple d'utilisation
#unique_values = list_unique_values(stop_times_csv_filename)
#print("Valeurs uniques de la première colonne :")
#for value in unique_values:
#    print(value)
#print("Nbre de valeurs uniques:",len(unique_values));

sys.exit()
    
    
