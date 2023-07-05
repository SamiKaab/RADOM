This project aims to monitor the use of standing desk by measuring the height of the desk and whether someone is present or not.
This project utilises a Raspberry Pi 4 to read data from a human presence sensor and a distance sensor and store it in a CSV file. The data is periodically uploaded to Google Drive.



# Omega2 Pro Set Up

Verify that the Omega2 Pro is connected to internet:
```sh
ping duckduckgo.com
``` 
This project aims to monitor the use of standing desk by measuring the height of the desk and whether someone is present or not.
This project utilises a Raspberry Pi 4 to read data from a human presence sensor and a distance sensor and store it in a CSV file. The data is periodically uploaded to Google Drive.

# Required material
- Omega2 Pro
- [DFRobot_mmWave module](https://www.dfrobot.com/product-2282.html)
- [PiicoDev_VL53L1X module](https://www.sparkfun.com/products/14722)
- [SDL_DS3231 module](https://www.jaycar.com.au/rtc-clock-module-for-raspberry-pi/p/XC9044?pos=1&queryId=f5734bdf10cb6c5024d07c37201f1d5b&sort=relevance&searchText=rtc)
- Jumper wires
  



Verify that the Omega2 Pro is connected to internet:
```sh
ping duckduckgo.com
``` 
Update the Rapsberry Pi install git and clone this project:
```sh
git clone https://github.com/SamiKaab/Be-Up-Standing
```
```sh
cd Be-Up-Standing
pip3 install -r requirements.txt
```
in order to for the program to run on but a service routine needs to be created:
and copy the following lines:


# Setting up a google drive API
The data recorded is uploaded to a google drive using the google drive api. For the program to use the api is is necessary to create credentials.
You can find instructions on how to set up a google drive api [here](https://developers.google.com/drive/api/quickstart/python). Make sure to link a google service account to the project. Since we are using a headless device it is not possible for us to generate tokens which are necessary when using a normal google account a require a webbrowser based authentification which we cannot perform. This is the reason why a service account is required.

# Usage
The Raspberry Pi should now be ready. Before rebooting the device (`sudo reboot`), you may want to modify the variables stored in [config.ini](/config.ini).


Follow the Omega2 Pro [getting started tutorial](https://onion.io/omega2-pro-get-started/)
update list of available packages
```sh
opkg update
```
install required packages
```sh
opkg install git git-http ca-bundle python3 python3-pip pyOnionGpio
```
install package to create virtual environments 
```sh
pip3 install virtualenv
```
```sh
cp /usr/lib/python2.7/onionGpio.py /usr/lib/python3.6/
```
Modify the lines in onionGpio.py where there is a print statment to add brackets
create a folder and creat a virtual environemnt inside it
```sh
mkdir /root/beUpStandingFirmware
```
```sh
cd /root/beUpStandingFirmware
```
```sh
git clone https://github.com/SamiKaab/Be-Up-Standing
```

```
virtualenv venv
```

activate the virtual environment

```
source venv/bin/activate
```

```
mkdir /root/temp
export TMPDIR=/root/temp
pip install -r requirements
```
in `venv/lib/python3.6/site-packages/google_auth_oauthlib/flow.py` comment out the lines:  
```py 
import webbrowser
```
and 
```py
if open_browser:   
    webbrowser.open(auth_url, new=1, autoraise=True)
```
the package webbrowser cannot be used on the omega

# Setting up a google drive API
The data recorded is uploaded to a google drive using the google drive api. For the program to use the api is is necessary to create credentials and generate a `token.json` file. 
You can find instructions on how to set up a google drive api [here](https://developers.google.com/drive/api/quickstart/python)   
Because we are using the raspberry pi in headless mode, it is not possible to generate the token there. It must first be created by running the `get_credentials()` function in [backup_to_drive.py](/backup_to_drive.py) and then copying the `token.json` file (or its content) to the Raspberry Pi.

# Usage
The Raspberry Pi should now be ready. Before rebooting the device (`sudo reboot`), you may want to modify the variables stored in [config.ini](/config.ini).



Follow the Omega2 Pro [getting started tutorial](https://onion.io/omega2-pro-get-started/)
update list of available packages
```sh
opkg update
```
install required packages
```sh
opkg install git git-http ca-bundle python3 python3-pip pyOnionGpio
```
install package to create virtual environments 
```sh
pip3 install virtualenv
```

```sh
cp /usr/lib/python2.7/onionGpio.py /usr/lib/python3.6/
```
Modify the lines in onionGpio.py where there is a print statment to add brackets
create a folder and creat a virtual environemnt inside it
```sh
mkdir /root/beUpStandingFirmware
```
```sh
cd /root/beUpStandingFirmware
```
```sh
virtualenv venv
source venv/bin/activate
```
```
pip install -r requirements.txt
```
in `venv/lib/python3.6/site-packages/google_auth_oauthlib/flow.py` comment out the lines:
```py
import webbrowser
```
and 
```py
if open_browser:   
    webbrowser.open(auth_url, new=1, autoraise=True)
```
the package webbrowser cannot be used on the omega