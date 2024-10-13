import os
import json
import urllib3
from datetime import datetime
from influxdb import InfluxDBClient
from flask import Flask, jsonify, request
from flask_cors import CORS  # Importiere flask_cors

# Warnungen bezüglich unbestätigter HTTPS-Anfragen deaktivieren (optional)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# CORS für alle Routen aktivieren
CORS(app)

def fetch_weather_data():
    # Pfade zu den Dateien
    credentials_file_path = 'credentials.txt'
    koordinaten_file_path = 'Koordinaten.json'

    # Standardwerte für alle Attribute
    default_values = {
        "humidity": None,
        "rain": None,
        "temperature": None,
        "timestamp": None,
        "x": None,
        "y": None
    }

    # Benutzername und Passwort aus der Datei lesen
    props = {}
    try:
        with open(credentials_file_path, 'r') as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    props[key.strip()] = value.strip()
    except IOError as e:
        return {"error": f"Fehler beim Lesen der Credentials-Datei: {e}"}, 500

    USERNAME = props.get('username')
    PASSWORD = props.get('password')

    if USERNAME is None or PASSWORD is None:
        return {"error": "Benutzername oder Passwort nicht in der Credentials-Datei gefunden."}, 500

    # Koordinaten aus Koordinaten.json lesen
    koordinaten_map = {}
    try:
        with open(koordinaten_file_path, 'r') as reader:
            koordinaten_list = json.load(reader)
            for item in koordinaten_list:
                location = item.get('location')
                x = float(item.get('x'))
                y = float(item.get('y'))
                coords = {'x': x, 'y': y}
                koordinaten_map[location] = coords
    except IOError as e:
        return {"error": f"Fehler beim Lesen der Koordinaten-Datei: {e}"}, 500

    # Verbindung zur InfluxDB herstellen
    INFLUXDB_URL = 'hsma-iot.de'
    DATABASE = 'HSMA_weather_stations'

    influxdb_client = InfluxDBClient(
        host=INFLUXDB_URL,
        port=443,
        username=USERNAME,
        password=PASSWORD,
        database=DATABASE,
        ssl=True,
        verify_ssl=False,
        path='/influxdb/'
    )

    try:
        # Abfrage definieren, um die neuesten Datenpunkte jeder Wetterstation zu erhalten
        query_string = 'SELECT LAST(*) FROM /.*/ GROUP BY "location"'
        result = influxdb_client.query(query_string)

        # Dictionary zum Speichern der Daten
        data_map = {}

        # Verarbeitung des Abfrageergebnisses
        for series in result.raw.get('series', []):
            measurement = series.get('name')  # Measurement-Name
            tags = series.get('tags', {})
            location = tags.get('location')  # Standort

            if not location:
                continue

            # Die neuesten Werte abrufen
            columns = series.get('columns', [])
            values = series.get('values', [[]])[0]  # Nur ein Wert pro Serie

            # Daten für die aktuelle Location abrufen oder neuen Eintrag erstellen
            measurement_data = data_map.get(location, {})

            # Spaltennamen und Werte hinzufügen
            for i in range(1, len(columns)):  # Beginne bei 1, um "time" zu überspringen
                field = measurement
                value = values[i]

                # Speichere nur die gewünschten Felder
                if field in ['Humidity0', 'Temperature0', 'Rain0', 'Time']:
                    # Umbenennen der Felder für die JSON-Ausgabe
                    json_field_name = ''
                    if field == 'Humidity0':
                        json_field_name = 'humidity'
                    elif field == 'Temperature0':
                        json_field_name = 'temperature'
                    elif field == 'Rain0':
                        json_field_name = 'rain'
                    elif field == 'Time':
                        json_field_name = 'timestamp'
                        # Optional: Zeitstempel umwandeln
                        if isinstance(value, (int, float)):
                            unix_timestamp = float(value)
                            timestamp = int(unix_timestamp * 1000)
                            date = datetime.fromtimestamp(timestamp / 1000.0)
                            value = date.strftime('%Y-%m-%d %H:%M:%S')
                    measurement_data[json_field_name] = value

            # Speichere die Location
            measurement_data['location'] = location

            # Koordinaten hinzufügen
            coords = koordinaten_map.get(location)
            if coords:
                measurement_data['x'] = coords['x']
                measurement_data['y'] = coords['y']
            else:
                print(f"Keine Koordinaten für Location: {location}")

            # Aktualisiere die Daten in der data_map
            data_map[location] = measurement_data

        return list(data_map.values()), 200

    except Exception as e:
        return {"error": str(e)}, 500

    finally:
        # Verbindung schließen
        influxdb_client.close()


@app.route('/weather', methods=['GET'])
def get_weather_data():
    # Daten abrufen und als JSON zurückgeben
    data, status_code = fetch_weather_data()
    return jsonify(data), status_code

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
