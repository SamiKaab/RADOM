"""
File: battery.py
Description: This script retrieves the battery voltage level from the power-dock2 command and calculates the battery percentage based on the voltage range. It continuously prints the battery voltage and percentage level until interrupted.
Author: Sami Kaab
Date: 2023-07-05
"""

import subprocess
import time

def get_battery_voltage():
    result = subprocess.check_output(['power-dock2'])
    output = result.decode('utf-8')
    lines = output.split('\n')
    for line in lines:
        if line.startswith('Battery Voltage Level'):
            battery_voltage = float(line.split(': ')[1].split(' ')[0])
            return battery_voltage
        
def compute_battery_level():
    battery_voltage = get_battery_voltage()
    full_voltage = 4.1  # Replace with the voltage of a fully charged battery
    empty_voltage = 2.7  # Replace with the voltage of an empty battery

    battery_percentage = ((battery_voltage - empty_voltage) / (full_voltage - empty_voltage)) * 100 
    battery_percentage = battery_percentage if battery_percentage < 100 else 100 
    return battery_percentage

if __name__ == "__main__":
    while True:
        battery_level = round(compute_battery_level(),2)
        print(get_battery_voltage())
        print("Battery Level:", battery_level, "%")
        time.sleep(1)
