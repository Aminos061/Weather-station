from flask import Flask, jsonify
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.query_api import QueryApi
import os

app = Flask(__name__)

# Verbindung zu InfluxDB über Umgebungsvariablen
INFLUXDB_HOST = os.getenv('INFLUXDB_HOST', 'localhost')
INFLUXDB_PORT = os.getenv('INFLUXDB_PORT', 8086)
INFLUXDB_TOKEN = os.getenv('INFLUXDB_TOKEN', 'password')  # Token is used in InfluxDB 2.x
INFLUXDB_ORG = os.getenv('INFLUXDB_ORG', 'your_org')      # You need to provide the organization name
INFLUXDB_BUCKET = os.getenv('INFLUXDB_BUCKET', 'weather')  # Bucket is the new equivalent of database

# Initialize InfluxDB Client
client = InfluxDBClient(
    url=f"http://{INFLUXDB_HOST}:{INFLUXDB_PORT}",
    token=INFLUXDB_TOKEN,
    org=INFLUXDB_ORG
)

query_api = client.query_api()

@app.route('/api/data', methods=['GET'])
def get_weather_data():
    # Abfrage von Daten aus InfluxDB mit Flux query
    query = f'from(bucket: "{INFLUXDB_BUCKET}") |> range(start: -1h) |> limit(n: 10)'
    result = query_api.query(org=INFLUXDB_ORG, query=query)
    
    # Extract and format data points
    data_points = []
    for table in result:
        for record in table.records:
            data_points.append({
                'time': record.get_time(),
                'value': record.get_value(),
                'field': record.get_field(),
                'measurement': record.get_measurement()
            })
    
    return jsonify(data_points)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
