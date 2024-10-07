# app.py
from flask import Flask, jsonify
from influxdb import InfluxDBClient
import os

app = Flask(__name__)

# Verbindung zu InfluxDB über Umgebungsvariablen
INFLUXDB_HOST = os.getenv('INFLUXDB_HOST', 'localhost')
INFLUXDB_PORT = os.getenv('INFLUXDB_PORT', 8086)
INFLUXDB_USER = os.getenv('INFLUXDB_USER', 'admin')
INFLUXDB_PASSWORD = os.getenv('INFLUXDB_PASSWORD', 'password')
INFLUXDB_DBNAME = os.getenv('INFLUXDB_DBNAME', 'weather')

client = InfluxDBClient(host=INFLUXDB_HOST, port=INFLUXDB_PORT, username=INFLUXDB_USER, password=INFLUXDB_PASSWORD, database=INFLUXDB_DBNAME)

@app.route('/api/data', methods=['GET'])
def get_weather_data():
    # Abfrage von Daten aus InfluxDB
    query = 'SELECT * FROM weather_data LIMIT 10'
    result = client.query(query)
    data_points = list(result.get_points())
    
    return jsonify(data_points)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
