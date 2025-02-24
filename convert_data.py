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


stop_times_csv_input_filename = "data/stop_times.txt"  # Fichier GTFS csv incluant tous les stop_times
stop_times_js_output_filename = "data/stop_times.js"    # Fichier js de sortie, à renommer si e.g. par jour stop_times-DIM.js
#Filters to reduce size of stop_times data, depending on regions and/or weekdays
filter_strings = ["_LG_N3-Sem-", "-SC-N3-Sem-", "-choi-Sem-","BW_A_P2-Sem-"] #regular weeks
#filter_strings = ["-Sem-Vac","-Sem-Cong"] #"_PA_2025-25_SP_VA-Sem-Vac","choi-Sem-Cong"] #holiday weeks
#filter_strings = ["-Samedi-"] #"H25_P2-Sem"]
#filter_strings = ["-Dimanche-"] #"H25_P2-Sem"]
#filter_strings = ["-Mercredi-"] #"H25_P2-Sem"]
stops_csv_input_filename = "data/stops.txt" # Fichier GTFS csv incluant toutes les routes/trips
stops_js_output_filename = "data/stops.js"


# ----------------------------------------------------------------------
# Fonction pour convertir stop_times du format csv à un dictionnaire JS
def convert_stop_times_csv_to_js(csv_filename, js_filename, filter_strings=None):
    horaires_data = {}

    with open(csv_filename, mode="r", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        
        for row in reader:
            trip_id = row["trip_id"]
            
            # Appliquer le filtre si une chaîne est spécifiée
            if filter_strings and not any(f in trip_id for f in filter_strings):
                continue

            if trip_id not in horaires_data:
                horaires_data[trip_id] = []

            horaires_data[trip_id].append({
                "a": row["arrival_time"][:5],  #arrival_time
                #"d": row["departure_time"][:5], #departure_time
                "s": row["stop_id"],               #stop_id
                "seq": int(row["stop_sequence"])  #stop_sequence int
            })

    # Convertir le dictionnaire en JSON formaté
    #json_data = json.dumps(horaires_data, indent=2, ensure_ascii=False)
    json_data = json.dumps(horaires_data, separators=(",", ":"), ensure_ascii=False)

    # Écrire dans un fichier JS avec une déclaration de variable
    with open(js_filename, mode="w", encoding="utf-8") as js_file:
        js_file.write(f"const horairesData = {json_data};\n")

    print(f"Conversion stop_times terminée {js_filename}")



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

    print(f"Conversion stops terminée : {js_filename}")

    

# Execute conversions
convert_stop_times_csv_to_js(stop_times_csv_input_filename, stop_times_js_output_filename, filter_strings)
convert_stops_csv_to_js(stops_csv_input_filename, stops_js_output_filename)



#not used, for stats only
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
    
    
