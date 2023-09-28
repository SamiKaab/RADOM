
import lib.full_color_led as led
from shared_resources import FILE_HEADER, DATA_DIR, CONFIG_FILE,stop_event, lock,LOG_FILE, CONFIG_FILE
import time
import logging
import configparser
# Function to pulsate the LED with a specified frequency and color
def pulsate_led(led_status_queue, status_queue):
    # INITIATE LOGGING
    logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    logging.info("Pulsate LED thread started")    
    
    global_var_dict = {
        "connected" : 0,
        "uploading" : 0,
        "recording" : 0,
        "settingUp" : 0,
        "stop_event" : 0
        }

    max_intensity = 255
    intensity = 0
    direction = 1
    stop = False
    lastStatus = "Setting Up"
    status = "Setting Up"
    while True:
        if lastStatus != status:
            status_queue.append(status)
        while led_status_queue:
            key, value = led_status_queue.popleft()
            global_var_dict[key] = value
            logging.info("Pulsate LED thread received: " + str(key) + " " + str(value))

        if not stop_event.is_set() and stop:
            stop = False
            with lock:
                config = configparser.ConfigParser()
                config.read(CONFIG_FILE)
                LED_INTENSITY = config.getint('DEFAULT', 'LED_INTENSITY') 
                max_intensity = int(255 * LED_INTENSITY/100)
        if stop_event.is_set():
            stop = True
            # red
            frequency = 0.5
            red = 255
            green = 0
            blue = 0
            if status != "Not Recording":
                status = "Not Recording"
        
        elif global_var_dict["recording"] and not global_var_dict["connected"]:
            # green
            frequency = 0.5
            red = 0
            green = 255
            blue = 0
            if status != "Recording with no internet":
                status = "Recording with no internet"

        elif global_var_dict["recording"] and global_var_dict["connected"] :
            # blue
            if global_var_dict["uploading"]:
                frequency = 20
                red = 0
                green = 255
                blue = 255
                if status != "Uploading":
                    status = "Uploading"
            else:
                frequency = 0.5
                red = 0
                green = 0
                blue = 255
                if status != "Recording with internet":
                    status = "Recording with internet"
        elif not global_var_dict["recording"] and not global_var_dict["settingUp"] :
            # purple
            frequency = 0.1
            red = 255
            green = 51
            blue = 255
            if status != "Sleeping":
                status = "Sleeping"
        elif global_var_dict["settingUp"] :
            # yellow
            frequency = 0.5
            red = 255
            green = 170
            blue = 0
            if status != "Setting Up":
                status = "Setting Up"
            
        else:
            # red
            frequency = 0.01
            red = 255
            green = 0
            blue = 0
        
        period = 1.0 / frequency
        nb_steps = 100
        step = 1/nb_steps
        if intensity < 1-step and direction == 1:
            intensity += step
        elif intensity > 1 - step and direction == 1:
            direction = 0
            intensity-=step
        elif intensity > step and direction == 0:
            intensity -=step
        elif intensity < step and direction == 0:
            direction = 1
            intensity += step
        
        red = int(intensity * red * max_intensity / 255)
        green = int(intensity * green * max_intensity / 255)
        blue = int(intensity * blue * max_intensity / 255)
        led.set_led_color(red, green, blue)
        time.sleep(period/(2*nb_steps))

        # for intensity in range(max_intensity, -1, -1):
        #     led.set_led_color(red * intensity // max_intensity, green * intensity // max_intensity, blue * intensity // max_intensity)
        #     time.sleep(period / (2 * max_intensity))
    led.set_led_color(0,0,0)
    print("Pulsate LED thread stopped")
