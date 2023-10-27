
import lib.full_color_led as led
from shared_resources import FILE_HEADER, DATA_DIR, CONFIG_FILE,stop_event, lock,LOG_FILE, CONFIG_FILE
import time
# import logging
import configparser
# Function to pulsate the LED with a specified frequency and color
def pulsate_led(led_status_queue, status_queue):
    # logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    # logging.info("Pulsate LED thread started")    
    color = [0, 0, 0]

    colors = []
    red = [255,0,0]
    blue = [0,0,255]
    green = [0,255,0]
    light_blue = [0,255,255]
    purple = [255,51,255]
    yellow = [255,170,0]
    global_var_dict = {
        "connected" : 0,
        "uploading" : 0,
        "recording" : 0,
        "settingUp" : 0,
        "stop_event" : 0,
        "led_intensity" : 100
        }
    i = 0
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
            global_var_dict[key] = int(value)
            max_intensity = int(255 * global_var_dict["led_intensity"]/100)

        if not stop_event.is_set() and stop:
            stop = False
            with lock:
                config = configparser.ConfigParser()
                config.read(CONFIG_FILE)
                LED_INTENSITY = config.getint('DEFAULT', 'LED_INTENSITY') 
                max_intensity = int(255 * LED_INTENSITY/100)
 
        if global_var_dict["uploading"]:
            frequency = 20
            colors = [light_blue]
            if status != "Uploading":
                status = "Uploading"
        elif stop_event.is_set():
            stop = True
            # red
            frequency = 0.5
            colors = [red]
            if global_var_dict["connected"]:
                colors.append(blue)
            if status != "Not Recording":
                status = "Not Recording"
        
        elif global_var_dict["recording"]:
            # green
            frequency = 0.5
            colors = [green]
            if global_var_dict["connected"]:
                colors.append(blue)
            if status != "Recording":
                status = "Recording"

   
        elif not global_var_dict["recording"] and not global_var_dict["settingUp"] :
            # purple
            frequency = 0.5
            colors = [purple]
            if global_var_dict["connected"]:
                colors.append(blue)
            if status != "Sleeping":
                status = "Sleeping"
        elif global_var_dict["settingUp"] :
            # yellow
            frequency = 0.5
            colors = [yellow]
            if status != "Setting Up":
                status = "Setting Up"
            
        else:
            # red
            frequency = 0.01
            colors = [red]
        
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
            i+=1
        
        i = i%len(colors)
        color = colors[i]
        r = color[0]
        g = color[1]
        b = color[2]
        r = int(intensity * r * max_intensity / 255)
        g = int(intensity * g * max_intensity / 255)
        b = int(intensity * b * max_intensity / 255)
        led.set_led_color(r, g, b)
        time.sleep(period/(2*nb_steps))

        # for intensity in range(max_intensity, -1, -1):
        #     led.set_led_color(red * intensity // max_intensity, green * intensity // max_intensity, blue * intensity // max_intensity)
        #     time.sleep(period / (2 * max_intensity))
    led.set_led_color(0,0,0)
    print("Pulsate LED thread stopped")
