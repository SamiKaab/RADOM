"""
File: rtc_test.py
Description: This script tests the DS3231 RTC by reading the time.
Author: Sami Kaab
Date: 2023-07-05
"""
try:
    import lib.SDL_DS3231 as RTC
    import time
    print("setting up RTC")
    rtc = RTC.SDL_DS3231()

    for i in range(10):
        timeStart = rtc.read_datetime()
        print(timeStart)
        time.sleep(1)
    print("OK")
except Exception as e:
    print(e)
    