"""
File: full_color_led_test.py
Description: This script sets the GPIO pin for PWM and defines functions to set the LED color using PWM and pulsate the LED with a specified frequency and color.
Author: Sami Kaab
Date: 2023-07-05
"""

import time
import os

# Set the GPIO pin for PWM
os.system("omega2-ctrl gpiomux set uart2 pwm23")

# Define the path to the LED device file
led_device = '/dev/ledchain2'

"""Set the LED color using PWM

Arguments: red, green, blue -- color values (0-255)
"""
def set_led_color(red, green, blue):
    # Convert color values to hexadecimal string
    color_code = bytearray([red, green, blue]).hex()

    # Write the color code to the LED device file
    with open(led_device, 'wb') as f:
        f.write(bytes.fromhex(color_code))

"""Pulsate the LED with a specified frequency and color

Args:
    frequency (float): frequency in Hz (0.1-10 Hz
    red (int): red color value (0-255)
    green (int): green color value (0-255)
    blue (int): blue color value (0-255)
"""
def pulsate_led(frequency, red, green, blue):
    period = 1.0 / frequency
    max_intensity = 255

    while True:
        for intensity in range(0, max_intensity + 1):
            set_led_color(red * intensity // max_intensity, green * intensity // max_intensity, blue * intensity // max_intensity)
            time.sleep(period / (2 * max_intensity))

        for intensity in range(max_intensity, -1, -1):
            set_led_color(red * intensity // max_intensity, green * intensity // max_intensity, blue * intensity // max_intensity)
            time.sleep(period / (2 * max_intensity))

try:
    # Example: Pulsate the LED at a frequency of 2 Hz with the specified color (221, 51, 255)
    pulsate_led(0.5, 255, 170, 0)
    # 221, 51, 255
    # 255,170,0
except KeyboardInterrupt:
    set_led_color(0,0,0)
