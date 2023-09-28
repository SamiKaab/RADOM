import requests
from datetime import datetime, timedelta
import os
import time
import configparser
import backup_to_drive as google_drive
from shared_resources import FILE_HEADER, ROOT_DIR, DATA_DIR, CONFIG_FILE,stop_event, lock, device_should_record,LOG_FILE,DEVICE_ID

import logging

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

def upload_loop(rtc, status_queue):
    """
    Periodically upload the sensor data to Google Drive.

    This function checks for an internet connection and, if available, updates the real-time clock (RTC)
    module with the current time from the internet. It then backs up the sensor data to Google Drive.
    The status of the backup process is indicated using the red LED.

    Returns:
        None.
    """
    
    # set up logging
    logging.basicConfig(filename= LOG_FILE , level=logging.DEBUG, format='%(asctime)s %(message)s')
    logging.info('upload thread started')

    with lock:
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)
        UPLOAD_PERIOD = config.getint('DEFAULT', 'UPLOAD_PERIOD')
        WAKE_AT = config.get('DEFAULT', 'WAKE_AT')
        SLEEP_AT = config.get('DEFAULT', 'SLEEP_AT')
        ID = config.get('DEFAULT', 'ID')
    

    # Update RTC with the current time if internet connection is available
    if google_drive.is_internet_available():
        dt = get_time_from_internet()
        rtc.write_datetime(dt)
    # else:
        # If internet connection is not available, turn on the red LED to indicate an error
        #print("no internet")
        

    # Continuously check for an internet connection and backup data to Google Drive
    last_upload_try = datetime.now()
    stop = False
    while True:
        if stop_event.is_set():
            stop = True
        elif stop:
            stop = False
            config = configparser.ConfigParser()
            config.read(CONFIG_FILE)
            UPLOAD_PERIOD = config.getint('DEFAULT', 'UPLOAD_PERIOD')
            WAKE_AT = config.get('DEFAULT', 'WAKE_AT')
            SLEEP_AT = config.get('DEFAULT', 'SLEEP_AT')
            ID = config.get('DEFAULT', 'ID')
            
        if (rtc.read_datetime() - last_upload_try).total_seconds() > UPLOAD_PERIOD and not stop:
            last_upload_try = rtc.read_datetime()
            internet = google_drive.is_internet_available()
            if internet:
                    dt = get_time_from_internet()
                    rtc.write_datetime(dt)
            if device_should_record(WAKE_AT, SLEEP_AT, rtc):
                # Check if internet connection is available
                if internet:
                    status_queue.append(("uploading", True))
                    # Back up data to Google Drive and turn off the red LED to indicate success
                    # file_list = [file for file in os.listdir(DATA_DIR) if file.endswith(".csv")]
                    try:
                        google_drive.upload(DEVICE_ID)
                    except Exception as e:
                        print(f"problem encountered while uploading:\n{e}")            
                    status_queue.append(("uploading", False))

                else:
                    status_queue.append(("uploading", False))
    
