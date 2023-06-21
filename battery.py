import subprocess
import time
import datetime
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
    print("Battery voltage:", battery_voltage, "v")
    full_voltage = 4.1  # Replace with the voltage of a fully charged battery
    empty_voltage = 3.30  # Replace with the voltage of an empty battery

    battery_percentage = ((battery_voltage - empty_voltage) / (full_voltage - empty_voltage)) * 100 
    battery_percentage = battery_percentage if battery_percentage < 100 else 100 
    return battery_percentage


if __name__ == "__main__":
    while True:
        battery_level = round(compute_battery_level(),2)
        print(datetime.datetime.now(), "Battery Level:", battery_level, "%")
        time.sleep(1)
