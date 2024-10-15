from flask import Flask, jsonify
from flask_cors import CORS  # Importiere CORS
import requests
from requests.auth import HTTPBasicAuth
import json
from datetime import datetime

app = Flask(__name__)

# Aktiviere CORS für alle Routen
CORS(app)

# InfluxDB connection details (for hsma-iot.de)
INFLUXDB_URL = "https://hsma-iot.de/influxdb/query"  
INFLUXDB_USERNAME = "hsma_faki_stud2024" 
INFLUXDB_PASSWORD = "N8Yqotmhe1lHZZTY2l8py4Hl6BUqEl" 
INFLUXDB_DB = "HSMA_weather_stations"

# Lese die Koordinaten aus der JSON-Datei ein
with open('Koordinaten.json') as file:
    coordinates_data = json.load(file)

# Helper function to escape strings for InfluxDB queries
def escape_string(value):
    return value.replace("'", "\\'").replace('"', '\\"')

# Helper function to make requests to InfluxDB
def query_influxdb(query):
    params = {
        "db": INFLUXDB_DB,
        "q": query
    }
    response = requests.get(INFLUXDB_URL, params=params, auth=HTTPBasicAuth(INFLUXDB_USERNAME, INFLUXDB_PASSWORD))
    response.raise_for_status()  # Raises an exception if the status code is 4xx or 5xx
    return response.json()

# Extract locations
def extract_locations(data):
    locations = set()
    if 'results' in data:
        for result in data['results']:
            if 'series' in result:
                for series in result['series']:
                    for value in series['values']:
                        locations.add(value[1])  # Assuming the location is at index 1
    return locations

# Extract measurements
def extract_measurements(data):
    measurements = set()
    if 'results' in data:
        for result in data['results']:
            if 'series' in result:
                for series in result['series']:
                    for value in series['values']:
                        measurements.add(value[0])  # Assuming the measurement is at index 0
    return measurements

# Extract latest values for each measurement
def extract_latest_values(data):
    latest_values = {}
    if 'results' in data:
        for result in data['results']:
            if 'series' in result:
                for series in result['series']:
                    measurement_name = series['name']
                    if series['values']:
                        latest_values[measurement_name] = series['values'][0][1]  # Assuming value is at index 1
    return latest_values

# Helper function to format the time
def format_time(timestamp):
    try:
        # Prüfe, ob der Zeitstempel ein Integer (Unix-Timestamp) ist
        if isinstance(timestamp, int):
            # Konvertiere Unix-Timestamp zu einem lesbaren Format
            dt = datetime.utcfromtimestamp(timestamp)  # Umwandlung in UTC-Zeit
            return dt.strftime("%d.%m.%Y %H:%M:%S")
        
        # Falls es ein String ist, wird angenommen, dass es im ISO-Format vorliegt
        elif isinstance(timestamp, str):
            dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
            return dt.strftime("%d.%m.%Y %H:%M:%S")
        
        # Falls das Format nicht passt, gib den Zeitstempel unverändert zurück
        return timestamp

    except Exception as e:
        # Fallback, falls ein unerwartetes Format vorliegt
        return str(e)

# Helper function to get coordinates for a location
def get_coordinates_for_location(location):
    for coord in coordinates_data:
        if coord["location"] == location:
            return coord["x"], coord["y"]
    return None, None  # Falls keine Koordinaten vorhanden sind

# API endpoint to retrieve weather data
@app.route('/api/data', methods=['GET'])
def get_weather_data():
    try:
        # 1. Get all locations
        query = "SHOW TAG VALUES WITH KEY = \"location\""
        location_data = query_influxdb(query)
        locations = extract_locations(location_data)

        location_to_measurements_map = {}

        # 2. For each location, get all measurements and their latest values
        for location in locations:
            # Get all measurements for the current location
            measurements_query = f"SHOW MEASUREMENTS WHERE \"location\" = '{escape_string(location)}'"
            measurements_data = query_influxdb(measurements_query)
            measurements = extract_measurements(measurements_data)

            measurements_with_values = {}

            if measurements:
                # Create query to get the latest values for all measurements for the current location
                value_query = " ".join([f"SELECT LAST(*) FROM \"{escape_string(measurement)}\" WHERE \"location\" = '{escape_string(location)}';"
                                        for measurement in measurements])
                value_data = query_influxdb(value_query)

                # Extract the latest values
                measurements_with_values = extract_latest_values(value_data)

            # Füge die Koordinaten zur Location hinzu
            x, y = get_coordinates_for_location(location)
            measurements_with_values["x"] = x
            measurements_with_values["y"] = y

            # Überprüfe, ob ein Zeitstempel vorhanden ist und formatiere ihn
            if "Time" in measurements_with_values:
                measurements_with_values["Time"] = format_time(measurements_with_values["Time"])

            location_to_measurements_map[location] = measurements_with_values

        # 3. Return the data as JSON
        return jsonify(location_to_measurements_map)

    except requests.exceptions.HTTPError as err:
        return jsonify({"error": str(err)}), 500  # Handle HTTP errors
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # General error handling

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
