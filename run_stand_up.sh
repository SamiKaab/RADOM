#!/bin/ash
sleep 30
cd /root/Firmware
source /root/Firmware/venv/bin/activate
python /root/Firmware/main_flask.py > /dev/null 2>&1 &
