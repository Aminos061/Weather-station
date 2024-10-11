from flask import Flask, jsonify
import json
import paho.mqtt.client as mqtt
import threading

app = Flask(__name__)

# MQTT connection details
MQTT_BROKER = "hsma-iot.de"
MQTT_PORT = 8883
MQTT_USERNAME = "hsma_faki_stud2024"
MQTT_PASSWORD = "N8Yqotmhe1lHZZTY2l8py4Hl6BUqEl"
MQTT_TOPIC = "HSMA_Weather/BWConsV1/JSON"

# Global variable to hold the latest weather data
latest_weather_data = {}

# MQTT callback functions
def on_connect(client, userdata, flags, rc):
    print("Connected with result code: " + str(rc))
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    global latest_weather_data
    try:
        # Parse the incoming JSON message
        data = json.loads(msg.payload.decode())
        # Update the latest weather data
        latest_weather_data = {
            'name': data.get('ID'),
            'timestamp': data.get('Time'),
            'temperature': float(data.get('T')),
            'humidity': float(data.get('H')),
            # Optional: weitere Daten können hier hinzugefügt werden
            'wind_speed': float(data.get('WSm')),
            'wind_angle': float(data.get('WD')),
            'rainfall': float(data.get('R')),
            'battery': data.get('Bat'),
            'gateway_id': data.get('GWID'),
            'pc': data.get('PC'),
        }
    except json.JSONDecodeError:
        print("Received non-JSON message")

# Start MQTT client in a separate thread
def start_mqtt_client():
    client = mqtt.Client()
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.tls_set()  # Enable SSL
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
    client.loop_forever()

# Start the MQTT client in a separate thread
mqtt_thread = threading.Thread(target=start_mqtt_client)
mqtt_thread.start()

# API endpoint to retrieve weather data
@app.route('/api/data', methods=['GET'])
def get_weather_data():
    if latest_weather_data:
        return jsonify(latest_weather_data)  # Return the latest weather data
    else:
        return jsonify({"error": "No data available"}), 404  # Handle no data available

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
