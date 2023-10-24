import threading
from datetime import datetime
# Lock for synchronization
lock = threading.Lock()

connected = False
uploading = False
recording = False
settingUp = True
# Create a flag to indicate if the threads should continue stop_event
stop_event = threading.Event()
ROOT_DIR = "/root/Firmware"
TEMP_DIR = "temp"
DATA_DIR = "data"
FILE_HEADER = ["Date time", "Distance(mm)", "Human Present"]
CONFIG_FILE = "config.ini"
LOG_FILE = "/root/Firmware/logs/standup.log"
DEVICE_ID ='A17E'

def device_should_record(WAKE_AT, SLEEP_AT, rtc):
    current_time = rtc.read_datetime().time()
    start = datetime.strptime(WAKE_AT, "%H:%M").time()
    end = datetime.strptime(SLEEP_AT, "%H:%M").time()

    if start <= end:
        return start <= current_time <= end
    else:
        return start <= current_time or current_time <= end  
    
