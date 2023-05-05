import lib.DFRobot_mmWave as human_presence
from lib.PiicoDev_VL53L1X import PiicoDev_VL53L1X
import lib.SDL_DS3231 as RTC

import time
from datetime import datetime, timedelta
import csv
import backup_to_drive as google_drive
import threading
import queue
import configparser
import requests
import RPi.GPIO as GPIO

RED_LED_PIN = 25  # BCM pin 25
WHITE_LED_PIN = 16  # BCM pin 16
FILE_HEADER = ["Date time", "Distance(mm)", "Human Present"]


def set_up_leds():
    """
    Set up the BCM pins for the red and white LEDs.

    This function initializes the BCM pin mode and sets up the specified pins for use as outputs
    for the red and white LEDs.

    Args:
        None.

    Returns:
        None.
    """
    # Set the BCM pin numbering mode
    GPIO.setmode(GPIO.BCM)

    # Set up the specified pins for use as outputs for the red and white LEDs
    GPIO.setup(RED_LED_PIN, GPIO.OUT)
    GPIO.setup(WHITE_LED_PIN, GPIO.OUT)


def solid(state, ledPin):
    """
    Turn an LED on or off.

    This function turns an LED on or off based on the value of the `state` argument. The BCM pin number
    of the LED to be turned on or off is specified by the `ledPin` argument.

    Args:
        state (bool): True to turn the LED on, False to turn it off.
        ledPin (int): The BCM pin number of the LED to be turned on or off.

    Returns:
        None.
    """
    # Update the state variable to HIGH or LOW depending on the value of `state`
    state = GPIO.HIGH if state else GPIO.LOW

    # Set the output of the specified LED to the value of `state`
    GPIO.output(ledPin, state)
 
def blink(ledPin, freq):
    """
    Blink an LED at a specified frequency.

    This function blinks an LED at a specified frequency, based on messages received from a shared queue.
    The status of the LED is updated based on the state of the `state` variable, which alternates between
    True and False every time the LED is turned on or off. 

    Args:
        ledPin (int): The BCM pin number of the LED to be blinked.
        freq (int): The initial frequency of the LED blink in Hz.

    Returns:
        None.
    """
    state = True

    # Continuously blink the LED
    while True:
        try:
            # Try to get the frequency from the queue without blocking
            [rcvdFreq, rcvdLedPin] = q.get(timeout=1/freq)

            # Check if the message is intended for this thread and update frequency if necessary
            if rcvdLedPin == ledPin:
                while rcvdFreq == 0:
                    # Turn off the LED and update state to False if frequency is 0
                    GPIO.output(ledPin, GPIO.LOW)
                    state = False
                    [rcvdFreq, rcvdLedPin] = q.get()
                freq = rcvdFreq
            else:
                # Put the message back into the queue if it is not intended for this thread
                q.put((rcvdFreq, rcvdLedPin))
        except queue.Empty:
            pass

        # Update the LED status based on the state variable
        state = GPIO.HIGH if state else GPIO.LOW
        GPIO.output(ledPin, state)
        state = False if state else True

def read_write_loop():
    """
    Continuously read sensor data and write it to a CSV file.

    This function reads sensor data from the human presence sensor and distance sensor, and stores
    it in a list. The data is then written to a CSV file with the specified file name every `WRITE_PERIOD`
    seconds.

    Returns:
        None.
    """
    # Initialize the list of data to be written to the CSV file and turn on the white LED to indicate data collection
    data = [FILE_HEADER]
    timeStart = rtc.read_datetime()
    q.put((1,WHITE_LED_PIN))

    # Continuously read sensor data and write it to a CSV file
    while True:
        # Read data from sensors
        now = rtc.read_datetime()
        hp = human_presence.read_presence(human_presence.HPD_GPIO_PIN)
        humanPresent = "yes" if hp == 1 else "no"
        distance = distSensor.read()

        # Append data to the list
        line = [now, distance, humanPresent]
        data.append(line)
        print("{now} {distance} {hp}".format(distance=distance, hp=humanPresent, now=now))

        # Write data to CSV file after set amount of time has elapsed
        elapsed = now - timeStart
        if elapsed > timedelta(seconds=WRITE_PERIOD):
            fileName = 'data//{id}_{now}_data.csv'.format(id=ID, now=timeStart)
            write_data_to_file(fileName, data)
            print("\nWrote data to file\n")

            # Reset data and time for the next write interval
            data = [data[0]]
            timeStart = rtc.read_datetime()

        # Wait for the specified sampling period before collecting more data
        time.sleep(SAMPLING_PERIOD)


def upload_loop():
    """
    Periodically upload the sensor data to Google Drive.

    This function checks for an internet connection and, if available, updates the real-time clock (RTC)
    module with the current time from the internet. It then backs up the sensor data to Google Drive.
    The status of the backup process is indicated using the red LED.

    Returns:
        None.
    """
    # Update RTC with the current time if internet connection is available
    if google_drive.is_internet_available():
        dt = get_time_from_internet()
        rtc.write_datetime(dt)
    else:
        # If internet connection is not available, turn on the red LED to indicate an error
        q.put((0,RED_LED_PIN))

    # Continuously check for an internet connection and backup data to Google Drive
    while True:
        # Check if internet connection is available
        if google_drive.is_internet_available():
            # If internet connection is available, turn on the red LED and update RTC with the current time
            q.put((20,RED_LED_PIN))
            dt = get_time_from_internet()
            rtc.write_datetime(dt)

            # Back up data to Google Drive and turn off the red LED to indicate success
            google_drive.backup_files()
            q.put((1,RED_LED_PIN))
        else:
            # If internet connection is not available, turn off the red LED and print a message to the console
            q.put((0,RED_LED_PIN))
            print("\nWill back up later\n")

        # Wait for the specified upload period before checking for an internet connection again
        time.sleep(UPLOAD_PERIOD)

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
    datetime_str = data['datetime']
    dt = datetime.fromisoformat(datetime_str)

    # Return the datetime object
    return dt

def write_data_to_file(fileName, data):
    """
    Write the data to a CSV file with the given file name.

    Args:
        fileName (str): The name of the file to write to.
        data (list): A list of data to write to the file.

    Returns:
        None.
    """
    with open(fileName, 'w', newline='') as f:
        # Create a CSV writer object
        writer = csv.writer(f)

        # Write the data to the CSV file
        writer.writerows(data)
      
if __name__ == "__main__":
    try:
        #init led
        set_up_leds()
        solid(True,RED_LED_PIN)
        
        # get user defined variable from config file
        config = configparser.ConfigParser()
        config.read('config.ini')
        SAMPLING_PERIOD = config.getint('DEFAULT', 'SAMPLING_PERIOD')
        WRITE_PERIOD = config.getint('DEFAULT', 'WRITE_PERIOD')
        UPLOAD_PERIOD = config.getint('DEFAULT', 'UPLOAD_PERIOD')
        ID = config.getint('DEFAULT', 'ID')


        # init sensors
        print("setting up HDP sensor")
        human_presence.init_hdp(human_presence.HPD_GPIO_PIN)
        print("setting up Distance sensor")
        distSensor = PiicoDev_VL53L1X() 
        print("setting up RTC")
        rtc = RTC.SDL_DS3231()
        
        # create queue for setting led blink frequency
        q = queue.Queue()
        
        # create and start threads
        data_thread = threading.Thread(target=read_write_loop)                      # read from sensors and write to file
        upload_thread = threading.Thread(target=upload_loop)                        # set RTC value and upload files to internet
        red_led_thread = threading.Thread(target=blink,args=[RED_LED_PIN,1])        # red led loop
        white_led_thread = threading.Thread(target=blink,args=[WHITE_LED_PIN,1])    #white led loop

        # Start all threads
        data_thread.start()
        upload_thread.start()
        red_led_thread.start()
        white_led_thread.start()
    
        data_thread.join()
        upload_thread.join()
        red_led_thread.join()
        white_led_thread.join()
        
    except KeyboardInterrupt: # User interruption
        GPIO.cleanup()
        
    except Exception as e:  # other exceptions
        print(e)
        GPIO.cleanup()
        
