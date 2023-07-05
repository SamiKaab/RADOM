from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/sensor-data', methods=['GET'])
def get_sensor_data():
    # Read the sensor data from your sensors
    distance = 123  # Example distance value
    human_presence = True  # Example human presence value

    # Create a dictionary with the sensor data
    data = {
        'distance': distance,
        'human_presence': human_presence
    }

    # Return the sensor data as JSON
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
