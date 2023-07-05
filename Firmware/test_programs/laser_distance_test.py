"""
File: laser_distance_test.py
Description: This script tests the PiicoDev VL53L1X Time-of-Flight Distance Sensor by reading the distance.
Author: Sami Kaab
Date: 2023-07-05
"""
try:
    from lib.PiicoDev_VL53L1X import PiicoDev_VL53L1X
    from time import sleep

    distSensor = PiicoDev_VL53L1X() 
    for i in range(10):
        distance = distSensor.read()
        print(distance)
        sleep(1)
    print("OK")

except Exception as e:
    print(e)
