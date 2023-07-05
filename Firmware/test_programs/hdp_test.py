"""
File: hdp_test.py
Description: This script tests the DFRobot Human Presence Detection board by reading the HPD GPIO pin.
Author: Sami Kaab
Date: 2023-07-05
"""

try:
    import lib.human_presence as human_presence
    import time

    human_presence.init_hdp()
    for i in range(10):
        hp = human_presence.read_presence()
        time.sleep(1)
        print(hp)
    print("OK")
except Exception as e:
    print(e)