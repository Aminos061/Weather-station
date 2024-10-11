from flask import Flask, jsonify
import requests
from requests.auth import HTTPBasicAuth

app = Flask(__name__)

# InfluxDB connection details (for hsma-iot.de)
INFLUXDB_URL = "https://hsma-iot.de/influxdb/query"  
INFLUXDB_USERNAME = "hsma_faki_stud2024" 
INFLUXDB_PASSWORD = "N8Yqotmhe1lHZZTY2l8py4Hl6BUqEl" 
INFLUXDB_DB = "HSMA_weather_stations" 

# API endpoint to retrieve weather data
@app.route('/api/data', methods=['GET'])
def get_weather_data():
    # Prepare the query
    query = "SHOW SERIES"
    params = {
        "db": INFLUXDB_DB,
        "q": query
    }
    
    try:
        # Make the API request to InfluxDB
        response = requests.get(INFLUXDB_URL, params=params, auth=HTTPBasicAuth(INFLUXDB_USERNAME, INFLUXDB_PASSWORD))
        
        # Check the status code of the response
        response.raise_for_status()  # Raises an exception for error status
        data = response.json()  # Process JSON response
        
        return jsonify(data)  # Return successful response
    except requests.exceptions.HTTPError as err:
        return jsonify({"error": str(err)}), 500  # Handle errors
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # General error handling

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
