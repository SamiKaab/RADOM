This project aims to monitor the use of standing desk by measuring the height of the desk and whether someone is present or not.
This project utilises a Omega2 Pro to read data from a human presence sensor and a distance sensor and, store it in a CSV file. The data is periodically uploaded to Google Drive.



# Required material
- [Omega2 Pro](https://onion.io/store/omega2-pro/)
- [DFRobot_mmWave module](https://www.dfrobot.com/product-2282.html)
- [PiicoDev_VL53L1X module](https://www.sparkfun.com/products/14722)
- [SDL_DS3231 module](https://www.jaycar.com.au/rtc-clock-module-for-raspberry-pi/p/XC9044?pos=1&queryId=f5734bdf10cb6c5024d07c37201f1d5b&sort=relevance&searchText=rtc)
- Jumper wires
  

<!-- Verify that the Omega2 Pro is connected to internet:
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
and copy the following lines: -->


# wiring scematic
<!--embed image center a resized with original ratio: Documentation/Wiring_Diagram.png-->
<p align="center">
  <img src="Documentation/Wiring_Diagram.png" width="400">
</p>

# Setting up the Omega2 Pro

```sh
wifisetup add -ssid BadLuck -encr psk2 -password trc5X2pl52X51
```
Follow the Omega2 Pro [getting started tutorial](https://onion.io/omega2-pro-get-started/). Once you have done that check that the Omega2 is able to connect to internet using the following command:
```sh
ping duckduckgo.com
```
You should get a similar output to this:
```
Pinging duckduckgo.com [20.43.111.112] with 32 bytes of data:
Reply from 20.43.111.112: bytes=32 time=18ms TTL=113
Reply from 20.43.111.112: bytes=32 time=18ms TTL=113
Reply from 20.43.111.112: bytes=32 time=18ms TTL=113
Reply from 20.43.111.112: bytes=32 time=18ms TTL=113

Ping statistics for 20.43.111.112:
    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss),
Approximate round trip times in milli-seconds:
    Minimum = 18ms, Maximum = 18ms, Average = 18ms
```
We first need to install git and ca-bundle in order to be able to clone the repository:
```sh
opkg update && opkg install git git-http ca-bundle
```
We can now install the necessary Omega2 and python packages. Clone the Firmware folder in the repository from the root folder:
```sh
git clone --depth 1 --filter=blob:none https://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@github.com/SamiKaab/Be-Up-Standing && mv ./Be-Up-Standing/Firmware . && rm -r Be-Up-Standing
```
then navigate to the Firmware folder and run the setup script:
```sh
cd Firmware && source ./shell_scripts/set_up.sh
```
this script will install the necessary packages and set up the Omega2 to run the program on startup.  
Next run the omega_rename script:
```sh
source ./shell_scripts/omega_rename.sh
```
This script will amongst other things change the default wifi name and password of the omega as well as the device's password.
The device should now be ready for use. just restart the device.
```

# Setting up a google drive API
The data recorded is uploaded to a google drive using the google drive api. For the program to use the api it is necessary to generate a credentials file.
You can find instructions on how to set up a google drive api [here](https://developers.google.com/drive/api/quickstart/python).  
Since we are using a headless device it is not possible for us to generate tokens which are necessary when using a normal google account and require a webbrowser based authentification which we cannot perform. For this reason make sure to link a google service account to the project.
Once you have generated the credentials file, copy it to the Firmware folder on the Omega2 Pro and rename it "credentials.json".

