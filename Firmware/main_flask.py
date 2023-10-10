"""
File: main.py
Description: This script runs the main program for the Standup Desk Sensor Bin.
Author: Sami Kaab
Date: 2023-07-05
"""
import time
import os

import threading
from collections import deque
from flask import Flask, jsonify,request,render_template, session,redirect, url_for
import configparser
from waitress import serve


import lib.SDL_DS3231 as RTC
import lib.full_color_led as led
import backup_to_drive as google_drive
from lib.battery import compute_battery_level

from shared_resources import stop_event, CONFIG_FILE
from sensor_thread import read_write_loop
from upload_thread import upload_loop
from led_thread import pulsate_led

sensor_data_queue = deque(maxlen=10)
status_queue = deque(maxlen=10)
sensor_datetime = []
sensor_presence = []
sensor_distance = []



def signal_handler(sig, frame):
    # Set the stop_event flag to False when Ctrl-C is pressed
    if not stop_event.is_set():
        stop_event.set()
    elif stop_event.is_set():
        stop_event.clear()

    print("Ctrl-C pressed")





def internet_check_loop(led_status_queue):
    while True:
        try:
            connected = google_drive.is_internet_available()
            led_status_queue.append(("connected", connected))
        except:
            pass
        time.sleep(5)   
    print("Internet check thread stopped")



app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/')
def home():
    return render_template('login.html')

# SSE route to send real-time data to the client
@app.route('/update_data', methods=['GET'])
def update_data():
    if len(sensor_data_queue):
        while len(sensor_data_queue):
            # Get the latest data from the queue
            sensor_data = sensor_data_queue.popleft()
            # Send both datetime and distance value to the client
            datetime_str = sensor_data[0].strftime("%Y-%m-%d %H:%M:%S")  # Format datetime as a string
            # append the new data to the sensor lists and shift data if the list is longer than 10
            sensor_datetime.append(datetime_str)
            sensor_distance.append(sensor_data[1])
            sensor_presence.append(sensor_data[2])
            if len(sensor_datetime) > 10:
                sensor_datetime.pop(0)
                sensor_distance.pop(0)
                sensor_presence.pop(0)
                
            

        return jsonify({'datetime': sensor_datetime, 'distance': sensor_distance, 'presence': sensor_presence})
    else:
        return jsonify({'data': None})

@app.route('/get_battery', methods=['GET'])
def get_battery():
    battery_level = int(compute_battery_level())
    return jsonify({'battery_level': battery_level})


@app.route('/button_click', methods=['POST'])
def button_click():
    data = request.json
    action = data.get('action')

    if action == 'start':
        print("start")
        stop_event.clear()
    elif action == 'stop':
        print("stop")
        stop_event.set()

    return jsonify({'message': f'Button pressed for action: {action}'})

@app.route('/get_device_info', methods=['GET'])
def get_device_id():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    ID = config.get('DEFAULT', 'ID')
    SAMPLING_PERIOD = config.getint('DEFAULT', 'SAMPLING_PERIOD')
    WAKE_AT = config.get('DEFAULT', 'WAKE_AT')
    SLEEP_AT = config.get('DEFAULT', 'SLEEP_AT')
    if status_queue:
        status = status_queue.popleft()
    
    return jsonify({'ID': ID, 'SP': SAMPLING_PERIOD, 'WAKE_AT': WAKE_AT, 'SLEEP_AT': SLEEP_AT, 'STATUS': status})


@app.route('/check_password', methods=['POST'])
def check_password():
    data = request.json
    password = data.get('password')
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    correct_password = config.get('DEFAULT', 'PASSWORD')
    
    if password == correct_password:
        session['user_role'] = 'admin'
        return jsonify({'valid': True, 'redirect': url_for('admin_dashboard')})
    else:
        return jsonify({'valid': False})

@app.route('/admin/dashboard')
def admin_dashboard():
    # Check if the user is authenticated as an admin
    print(f"{session.get('user_role')}")
    if session.get('user_role') == 'admin':
        session['user_role'] = None
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)
        ID = config.get('DEFAULT', 'ID')
        SAMPLING_PERIOD = config.getint('DEFAULT', 'SAMPLING_PERIOD')
        WAKE_AT = config.get('DEFAULT', 'WAKE_AT')
        SLEEP_AT = config.get('DEFAULT', 'SLEEP_AT')
        UPLOAD_PERIOD = config.getint('DEFAULT', 'UPLOAD_PERIOD')
        NEW_FILE_PERIOD = config.getint('DEFAULT', 'NEW_FILE_PERIOD')
        LED_INTENSITY = config.getint('DEFAULT', 'LED_INTENSITY') 
        WRITE_PERIOD = config.getint('DEFAULT', 'WRITE_PERIOD')


        return render_template('admin_dashboard.html', ID=ID, SP=SAMPLING_PERIOD, WAKE_AT=WAKE_AT, SLEEP_AT=SLEEP_AT, UP=UPLOAD_PERIOD, NFP=NEW_FILE_PERIOD, LED_INTENSITY=LED_INTENSITY, WP=WRITE_PERIOD)
    else:
        return render_template('login.html')

@app.route('/viewer/dashboard')
def viewer_dashboard():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    ID = config.get('DEFAULT', 'ID')
    SAMPLING_PERIOD = config.getint('DEFAULT', 'SAMPLING_PERIOD')
    WAKE_AT = config.get('DEFAULT', 'WAKE_AT')
    SLEEP_AT = config.get('DEFAULT', 'SLEEP_AT')
    UPLOAD_PERIOD = config.getint('DEFAULT', 'UPLOAD_PERIOD')
    NEW_FILE_PERIOD = config.getint('DEFAULT', 'NEW_FILE_PERIOD')
    LED_INTENSITY = config.getint('DEFAULT', 'LED_INTENSITY') 
    WRITE_PERIOD = config.getint('DEFAULT', 'WRITE_PERIOD')
    return render_template('viewer_dashboard.html', ID=ID, SP=SAMPLING_PERIOD, WAKE_AT=WAKE_AT, SLEEP_AT=SLEEP_AT, UP=UPLOAD_PERIOD, NFP=NEW_FILE_PERIOD, LED_INTENSITY=LED_INTENSITY, WP=WRITE_PERIOD)


def update_config_file(config_data):
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    for key, value in config_data.items():
        config.set('DEFAULT', key, value)
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)
    led_status_queue.append(("led_intensity", config_data['led_intensity']))
    print("Config file updated")

def check_config_values(config_data):
    required_keys = ['sampling_period', 'write_period', 'new_file_period', 'upload_period']
    for key in required_keys:
        if key not in config_data:
            return config_data
    sampling_period = int(config_data['sampling_period'])
    write_period = int(config_data['write_period'])
    new_file_period = int(config_data['new_file_period'])
    upload_period = int(config_data['upload_period'])
    if sampling_period < 1:
        config_data['sampling_period'] = str(1)
    if write_period < sampling_period:
        write_period = str(sampling_period * 2)
        config_data['write_period'] = write_period

    if new_file_period < write_period:
        new_file_period = str(write_period * 2)
        config_data['new_file_period'] = new_file_period
        
    if upload_period < new_file_period:
        upload_period = str(new_file_period * 2)
        config_data['upload_period'] = upload_period
    return config_data

# Receive the form data as JSON and print it
@app.route('/save_config', methods=['POST'])
def save_config():
    try:
        config_data = request.get_json()
        print("Received JSON data:")
        print(config_data)
        config_data = check_config_values(config_data)
        print(config_data)
        update_config_file(config_data)
        
        return jsonify({"message": "Data received successfully"})
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 400



if __name__ == "__main__":
    try:
        # Create an empty queue
        led_status_queue = deque()
        led_status_queue.append(("settingUp", True))

        led_thread = threading.Thread(target=pulsate_led, args=(led_status_queue, status_queue,))  # red led loop
        led_thread.start()
        rtc = RTC.SDL_DS3231()

        # create and start threads
        data_thread = threading.Thread(target=read_write_loop, args=(rtc, led_status_queue, sensor_data_queue,))
        upload_thread = threading.Thread(target=upload_loop, args=(rtc, led_status_queue,))  # set RTC value and upload files to the internet
        internet_check_thread = threading.Thread(target=internet_check_loop, args=(led_status_queue,))  # check if the internet is available

        # Start all threads
        data_thread.start()
        upload_thread.start()
        internet_check_thread.start()

        # Use Waitress to serve the Flask app
        serve(app, host='0.0.0.0', port=5000)

        data_thread.join()
        upload_thread.join()
        internet_check_thread.join()
        led_thread.join()
    except Exception as e:  # other exceptions
        print(e)

