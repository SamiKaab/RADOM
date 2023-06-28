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



# Setting up the Omega2 Pro

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
We can now install the necessary Omega2 and python packages. First update list of available packages:
```sh
opkg update
```
Install required Omega2 packages
```sh
opkg install git git-http ca-bundle python3 python3-pip pyOnionGpio
```
Install this package to create virtual environments 
```sh
pip3 install virtualenv
```
```sh
cp /usr/lib/python2.7/onionGpio.py /usr/lib/python3.6/
```
Modify the lines in onionGpio.py where there is a print statment to add brackets:  
`print "some string"` -> `print("some string")`  
Clone the repository and create a virtual environemnt inside it
```sh
git clone https://github.com/SamiKaab/Be-Up-Standing
cd Be-Up-Standing
virtualenv venv
```

Activate the virtual environment and install the required python packages:

```sh
source venv/bin/activate
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
the package `webbrowser` cannot be used on the omega.  
In order for the program to run on boot the following line needs to be added to `/etc/rc.local` right before `exit 0`:
```sh
/root/Firmware/run_stand_up.sh &
```

```sh
mv lib/flow.py venv/lib/python3.6/site-packages/google_auth_oauthlib/flow.py
```



# Setting up a google drive API
The data recorded is uploaded to a google drive using the google drive api. For the program to use the api it is necessary to generate a credentials file.
You can find instructions on how to set up a google drive api [here](https://developers.google.com/drive/api/quickstart/python).  
Since we are using a headless device it is not possible for us to generate tokens which are necessary when using a normal google account and require a webbrowser based authentification which we cannot perform. For this reason make sure to link a google service account to the project.


# Usage
The Omega2 Pro should now be ready. Turn off and on the device using the slide switch on the side. The program should start automatically. 

|**Recording without internet access**|**Recording with internet access**|**Uploading data to google drive**|**Device sleeping**|
|:---:|:---:|:---:|:---:|
|![](https://placehold.co/40x10/08FF30/08FF30)|![blue](https://placehold.co/40x10/1589F0/1589F0)|![blue](https://placehold.co/10x10/00ffff/00ffff)|![blue](https://placehold.co/50x10/ff33ff/ff33ff)|
|Green fading in and out at 1 second intervals|Blue fading in and out at 1 second intervals|Light blue flashing|purple fading in and out slowly|
