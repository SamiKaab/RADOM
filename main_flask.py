import lib.human_presence as human_presence
from lib.PiicoDev_VL53L1X import PiicoDev_VL53L1X
import lib.SDL_DS3231 as RTC
import lib.full_color_led as led

import time
from datetime import datetime, timedelta
import csv
import backup_to_drive as google_drive
import threading
import configparser
import requests
import sys
import signal
import os
from flask import Flask, jsonify,request
from collections import deque

import battery

connected = False
uploading = False
recording = False
settingUp = True
FILE_HEADER = ["Date time", "Distance(mm)", "Human Present"]
# Create a flag to indicate if the threads should continue running
running = True

DATA_DIR = "data"



sensor_data_queue = deque(maxlen=10)

# Create an empty queue
my_queue = deque()

def signal_handler(sig, frame):
    # Set the running flag to False when Ctrl-C is pressed
    global running
    running = False
    shutdown_func = request.environ.get('werkzeug.server.shutdown')
    if shutdown_func is not None:
        shutdown_func()



signal.signal(signal.SIGINT, signal_handler)  # Register the Ctrl-C signal (SIGINT)
signal.signal(signal.SIGTERM, signal_handler)  


def read_write_loop():
    """
    Continuously read sensor data and write it to a CSV file.

    This function reads sensor data from the human presence sensor and distance sensor, and stores
    it in a list. The data is then written to a CSV file with the specified file name every `WRITE_PERIOD`
    seconds.

    Returns:
        None.
    """
    global running


    # Initialize the list of data to be written to the CSV file and turn on the white LED to indicate data collection
    data = [FILE_HEADER]
    lastWriteTime = rtc.read_datetime()
    lastNewFileTime = rtc.read_datetime()
    fileName = os.path.join(DATA_DIR,f"{ID}_{lastNewFileTime}") 

    # Continuously read sensor data and write it to a CSV file
    while running:
        if device_should_record():
            recording = True
            my_queue.append(("recording", recording))

            # Read data from sensors
            now = rtc.read_datetime()
            hp = human_presence.read_presence()
            # hp = "yes" if hp else "no"
            distance = distSensor.read()
            battery_level = round(battery.compute_battery_level(),2)
            # Append data to the list
            line = [now, distance, hp]
            data.append(line)
            graph_data = [now, distance, hp, battery_level]
            sensor_data_queue.append(graph_data)

            #print("{now} {distance} {hp}".format(distance=distance, hp=humanPresent, now=now))

            elapsed = now - lastNewFileTime
            if elapsed > timedelta(seconds=NEW_FILE_PERIOD):
                write_data_to_file(fileName, data)
                data = [FILE_HEADER]
                lastWriteTime = now
                os.rename(fileName,f"{fileName}.csv")
                fileName = os .path.join(DATA_DIR,f"{ID}_{now}")
                lastNewFileTime = now
                
            # Write data to CSV file after set amount of time has elapsed
            elapsed = now - lastWriteTime
            if elapsed > timedelta(seconds=WRITE_PERIOD):
                write_data_to_file(fileName, data)
                #print("\nWrote data to file\n")

                # Reset data and time for the next write interval
                data = []
                lastWriteTime = now

            # Wait for the specified sampling period before collecting more data
            time.sleep(SAMPLING_PERIOD)
        else:
            recording = False
            my_queue.append(("recording", recording))

            #print(f"recording will wake in {seconds_until_wake()}")
            time.sleep(SAMPLING_PERIOD)
    recording = False
    my_queue.append(("recording", recording))

    

def internet_check_loop():
    global running
    while running:
        try:
            print("internet_check_loop")
            connected = google_drive.is_internet_available()
            my_queue.append(("connected", connected))
        except:
            pass

def upload_loop():
    """
    Periodically upload the sensor data to Google Drive.

    This function checks for an internet connection and, if available, updates the real-time clock (RTC)
    module with the current time from the internet. It then backs up the sensor data to Google Drive.
    The status of the backup process is indicated using the red LED.

    Returns:
        None.
    """
    global running

    # Update RTC with the current time if internet connection is available
    if google_drive.is_internet_available():
        dt = get_time_from_internet()
        rtc.write_datetime(dt)
    # else:
        # If internet connection is not available, turn on the red LED to indicate an error
        #print("no internet")
        

    # Continuously check for an internet connection and backup data to Google Drive
    
    while running:
        internet = google_drive.is_internet_available()
        if internet:
                dt = get_time_from_internet()
                rtc.write_datetime(dt)
        if device_should_record():
            # Check if internet connection is available
            if internet:
                uploading = True
                my_queue.append(("uploading", uploading))

                # connected = True

                # Back up data to Google Drive and turn off the red LED to indicate success
                file_list = [file for file in os.listdir(DATA_DIR) if file.endswith(".csv")]
                try:
                    google_drive.backup_files(file_list)
                except:
                    print("problem encountered while uploading")            
                uploading = False
                my_queue.append(("uploading", uploading))

            else:
                # If internet connection is not available, turn off the red LED and #print a message to the console
                #print("\nWill back up later\n")
                # connected = False
                uploading = False
                my_queue.append(("uploading", uploading))
            # Wait for the specified upload period before checking for an internet connection again
            time.sleep(UPLOAD_PERIOD)
        
        else:
            #print(f"upload will wake in {seconds_until_wake()}")
            time.sleep(UPLOAD_PERIOD)
    uploading = False
    my_queue.append(("uploading", uploading))
    # connected = False

def get_time_from_internet():
    """
    Retrieve the current date and time from the internet using the worldtimeapi.org API.

    Returns:
        A datetime object representing the current date and time.
    """
    # Define the URL of the API and specify the timezone to retrieve the time for
    url = 'http://worldtimeapi.org/api/timezone/Australia/Brisbane'  # or any other timezone you want to get the time for

    # Send a GET request to the API and retrieve the response data
    response = requests.get(url)
    data = response.json()

    # Extract the datetime string from the response data and convert it to a datetime object
    datetime_str = data['datetime'].split("+")[0]
    dt = datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S.%f")


    # Return the datetime object
    return dt

def write_data_to_file(fileName, data):
    """
    Write the data to a CSV file with the given file name.

    If the file already exists, the data will be appended to it.

    Args:
        fileName (str): The name of the file to write to.
        data (list): A list of data to write to the file.

    Returns:
        None.
    """
    mode = 'a' if os.path.exists(fileName) else 'w'
    with open(fileName, mode, newline='') as f:
        # Create a CSV writer object
        writer = csv.writer(f)

        # Write the data to the CSV file
        writer.writerows(data)

def device_should_record():
    current_time = rtc.read_datetime().time()
    start = datetime.strptime(WAKE_AT, "%H:%M").time()
    end = datetime.strptime(SLEEP_AT, "%H:%M").time()

    if start <= end:
        return start <= current_time <= end
    else:
        return start <= current_time or current_time <= end  
    
def seconds_until_wake():
    now = rtc.read_datetime()
    wake_time_today = now.replace(hour=int(WAKE_AT.split(':')[0]), minute=int(WAKE_AT.split(':')[1]), second=0, microsecond=0)
    
    if now < wake_time_today:
        delta = wake_time_today - now
    else:
        wake_time_tomorrow = wake_time_today + timedelta(days=1)
        delta = wake_time_tomorrow - now

    return int(delta.total_seconds())

# Function to pulsate the LED with a specified frequency and color
def pulsate_led():
    global running
    global_var_dict = {
        "connected" : 0,
        "uploading" : 0,
        "recording" : 0,
        "settingUp" : 0,
        "running" : 0
        }

    max_intensity = 255
    intensity = 0
    direction = 1
    while running:
        while my_queue:
            key, value = my_queue.popleft()
            global_var_dict[key] = value
            print(f"got {key}:{value}")

        if global_var_dict["recording"] and not global_var_dict["connected"]:
            # green
            frequency = 0.5
            red = 0
            green = 255
            blue = 0
        elif global_var_dict["recording"] and global_var_dict["connected"] :
            # blue
            if uploading:
                frequency = 20
                red = 0
                green = 255
                blue = 255
            else:
                frequency = 0.5
                red = 0
                green = 0
                blue = 255
        elif not global_var_dict["recording"] and not global_var_dict["settingUp"] :
            # purple
            frequency = 0.1
            red = 255
            green = 51
            blue = 255
        elif global_var_dict["settingUp"] :
            # yellow
            frequency = 0.5
            red = 255
            green = 170
            blue = 0
        else:
            # red
            frequency = 0.01
            red = 255
            green = 0
            blue = 0
        
        period = 1.0 / frequency
        if intensity < max_intensity and direction == 1:
            intensity += 1
        elif intensity >= max_intensity and direction == 1:
            direction = 0
            intensity-=1
        elif intensity > 0 and direction == 0:
            intensity -=1
        elif intensity <= 0 and direction == 0:
            direction = 1
            intensity += 1
            
        # for intensity in range(0, max_intensity + 1):
        led.set_led_color(red * intensity // max_intensity, green * intensity // max_intensity, blue * intensity // max_intensity)
        time.sleep(period / (2 * max_intensity))

        # for intensity in range(max_intensity, -1, -1):
        #     led.set_led_color(red * intensity // max_intensity, green * intensity // max_intensity, blue * intensity // max_intensity)
        #     time.sleep(period / (2 * max_intensity))
    led.set_led_color(255,0,0)

app = Flask(__name__)


@app.route('/sensor-data', methods=['GET'])
def get_sensor_data():
    # Check if there is data in the queue
    if len(sensor_data_queue):
        # Get the latest data from the queue
        data = sensor_data_queue.popleft()
        # Create a dictionary with the sensor data
        sensor_data = {
            'message' : "ok",
            'id' : ID,
            'fs': SAMPLING_PERIOD,
            'wp': WRITE_PERIOD,
            'nfp': NEW_FILE_PERIOD,
            'ufs': UPLOAD_PERIOD,
            'wa': WAKE_AT,
            'sa': SLEEP_AT,
            'datetime': data[0],
            'distance': data[1],
            'human_presence': data[2],
            'battery_level': data[3]
        }
        return jsonify(sensor_data)
    else:
        return jsonify({'message': 'none'})


if __name__ == "__main__":
    try:
        my_queue.append(("settingUp", True))

        led_thread = threading.Thread(target=pulsate_led)        # red led loop
        led_thread.start()
        print(1)
        # get user defined variable from config file
        config = configparser.ConfigParser()
        config.read('config.ini')
        SAMPLING_PERIOD = config.getint('DEFAULT', 'SAMPLING_PERIOD')
        WRITE_PERIOD = config.getint('DEFAULT', 'WRITE_PERIOD')
        NEW_FILE_PERIOD = config.getint('DEFAULT', 'NEW_FILE_PERIOD')
        UPLOAD_PERIOD = config.getint('DEFAULT', 'UPLOAD_PERIOD')
        ID = config.get('DEFAULT', 'ID')
        WAKE_AT = config.get('DEFAULT', 'WAKE_AT')
        SLEEP_AT = config.get('DEFAULT', 'SLEEP_AT')
        print(2)
        


        # init sensors
        #print("setting up HDP sensor")
        human_presence.init_hdp()
        #print("setting up Distance sensor")
        distSensor = PiicoDev_VL53L1X() 
        #print("setting up RTC")
        rtc = RTC.SDL_DS3231()
        
        
        # create and start threads
        data_thread = threading.Thread(target=read_write_loop)                      # read from sensors and write to file
        upload_thread = threading.Thread(target=upload_loop)                        # set RTC value and upload files to internet
        internet_check_thread = threading.Thread(target=internet_check_loop)
        # Start all threads
        data_thread.start()
        upload_thread.start()
        internet_check_thread.start()
        
        settingUp = False
        my_queue.append(("settingUp", False))

        app.run(host='0.0.0.0', port=5000)
        while running:
            time.sleep(1)


        # Set running flag to False and wait for threads to finish
        running = False
        data_thread.join()
        upload_thread.join()
        led_thread.join()
        internet_check_thread.join()
        
        led.set_led_color(0,0,0)
        
    except Exception as e:  # other exceptions
        led.set_led_color(255,0,0)
        #print(e)
        
        
