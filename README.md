This project aims to monitor the use of standing desk by measuring the height of the desk and whether someone is present or not.
This project utilises a Raspberry Pi 4 to read data from a human presence sensor and a distance sensor and store it in a CSV file. The data is periodically uploaded to Google Drive.

# Required material
- Raspberry Pi 4 model b
- [DFRobot_mmWave module](https://www.dfrobot.com/product-2282.html)
- [PiicoDev_VL53L1X module](https://www.sparkfun.com/products/14722)
- [SDL_DS3231 module](https://www.jaycar.com.au/rtc-clock-module-for-raspberry-pi/p/XC9044?pos=1&queryId=f5734bdf10cb6c5024d07c37201f1d5b&sort=relevance&searchText=rtc)
- LEDs (red and white)
- Resistors (appropriate for the LEDs used)
- Jumper wires
  

# Raspberry Pi Set Up
1. Download and install the Raspberry Pi Imager from the [official website](https://www.raspberrypi.com/software/).
2. Insert an SD card into your computer's SD card reader.
3. Open Raspberry Pi Imager and select the "Choose OS" option. From the list of options, choose the Raspbian Lite version.
4. Select the "Choose SD Card" option and select the SD card you inserted.
5. Under the "Advanced Options" section, check the box next to "Enable SSH" to enable SSH on the Raspberry Pi.
6. Under the "Advanced Options" section, select "Wireless LAN" and enter your network name (SSID) and password to configure WiFi on the Raspberry Pi.
7. Click on "Write" and wait for the flashing process to complete.

Once the process is finish insert the sd card into the Raspberry Pi and switch it on. You can interact with the Raspberry Pi either via ssh using a program like putty or the serial extension in vscode (what I use) or conenct the Raspberry Pi to a monitor (prior to boot) and a key board.

Verify that the Raspberry Pi is connected to internet:
```sh
ping duckduckgo.com
``` 
Update the Rapsberry Pi install git and clone this project:
```sh
sudo apt-get update && sudo apt-get install git
git clone https://github.com/SamiKaab/Be-Up-Standing
```
Python should come pre-installed. You can check by running :
```sh
python3 --version
```
if it is not already installed run:
```sh
sudo apt-get install python3
```
install the requried libraries:
```sh
cd Be-Up-Standing
pip3 install -r requirements.txt
```
in order to for the program to run on but a service routine needs to be created:
```sh
sudo nano /etc/systemd/system/beupstanding-boot.service
```
and copy the following lines:
```sh
[Unit]
Description=Be upstanding python script
After=multi-user.target

[Service]
Type=idle
WorkingDirectory=/home/pi/Be-Up-Standing
ExecStart=/usr/bin/python3 /home/pi/Be-Up-Standing/main.py

[Install]
WantedBy=multi-user.target
```
Press `Ctrl-S` and `Ctrl-X` so save and close the file.  
Finally enable the service routine:
```sh
 sudo systemctl enable beupstanding-boot.service
```

# Setting up a google drive API
The data recorded is uploaded to a google drive using the google drive api. For the program to use the api is is necessary to create credentials and generate a `token.json` file. 
You can find instructions on how to set up a google drive api [here](https://developers.google.com/drive/api/quickstart/python)   
Because we are using the raspberry pi in headless mode, it is not possible to generate the token there. It must first be created by running the `get_credentials()` function in [backup_to_drive.py](/backup_to_drive.py) and then copying the `token.json` file (or its content) to the Raspberry Pi.

# Usage
The Raspberry Pi should now be ready. Before rebooting the device (`sudo reboot`), you may want to modify the variables stored in [config.ini](/config.ini).
