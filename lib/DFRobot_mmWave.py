import  serial, time 
import  RPi.GPIO as GPIO


HPD_GPIO_PIN = 23

def setup_hpd(appear_latency, disappear_latency, start_distance, stop_distance):
    """Function to setup DFRobot Human Presence Detection board on UART 1

    Args:
        appear_latency (int): Sensor output delay when human is detected (s)
        disappear_latency (int): Sensor output delay when human is no longer detected (s)
        start_distance (int): Distance from sensor to start detection (m)
        stop_distance (int): Distance from sensor to stop detection (m)
    """
    # Setup the DFRobot HPD Sensor, after setting up the data will be read as the Pin value on Pin x
    HPD = mmWave_HPD(UART_ID=1, baudrate=115200)
    HPD.hpd_factory_reset()         # Factory reset to remove any previous settings
    HPD.hpd_output_latency(appear_latency,disappear_latency)     # Set output latency to 0
    HPD.hpd_set_distance(start_distance,stop_distance)       # Set detection distance to between 0 and 2m

def init_hdp(gpio_pin_number):
    setup_hpd(0,0,0,1)
    GPIO.setmode(GPIO.BCM) 
    GPIO.setup(gpio_pin_number, GPIO.IN) 

def read_presence(gpio_pin_number):
    return GPIO.input(gpio_pin_number)

class mmWave_HPD(object):
    """DFRobot mmWave Radar Library for the Raspberry Pi Pico ported from the Arduino Library from DFRobot

    Args:
        UART_ID (int, optional): Desired Pico UART Channel. Defaults to 1.
        baudrate (int, optional): Desired baudrate, sensor expects 115200. Defaults to 115200.
    """
    def __init__(self, UART_ID = 1, baudrate = 115200):
        """
        Initialises mmWave chip at ``UART_ID`` at ``baudrate``.

        Args:
            UART_ID (int, optional): _description_. Defaults to 1.
            baudrate (int, optional): _description_. Defaults to 115200.
        """
        self.UART_ID = UART_ID
        self.baudrate = baudrate
        self._init_sensor()

    def _init_sensor(self):
        """Creates the UART Object to create a communication channel with the HPD Sensor
        """
        self.hpd  =  serial.Serial(port  =  "/dev/serial0" , baudrate = 115200 , timeout = 2 )
        if  (self.hpd.isOpen()  ==  False):
            self.hpd. open ()                                       # check and open Serial0
        self.hpd.flushInput()                                       # clear the UART Input buffer
        self.hpd.flushOutput()
        print("HPD Sensor Initialised")

    def hpd_set_distance(self, min_distance, max_distance):
        """Sets the HPD sensor output delay time

        Args:
            hpd (obj): The UART object for the HPD Sensor
            min_distance (int): The desired minimum distance for ranging (metres)
            max_distance (int): The desired maximum distance for ranging (metres)
        """
        
        self.hpd.write(b'sensorStop')
        time.sleep(1)

        self.hpd.write(b'detRangeCfg -1 %d %d' % (min_distance/0.15, max_distance/0.15))
        time.sleep(1)

        self.hpd.write(b'saveCfg 0x45670123 0xCDEF89AB 0x956128C6 0xDF54AC89')
        time.sleep(1)

        self.hpd.write(b'sensorStart')
        time.sleep(1)

        

    def hpd_factory_reset(self):
        """Restore the HPD sensor current configuration to the factory settings.

        Args:
            hpd (obj): The UART object for the HPD Sensor
        """

        self.hpd.write(b'sensorStop')
        time.sleep(1)

        self.hpd.write(b'factoryReset 0x45670123 0xCDEF89AB 0x956128C6 0xDF54AC89')
        time.sleep(1)

        self.hpd.write(b'saveCfg 0x45670123 0xCDEF89AB 0x956128C6 0xDF54AC89')
        time.sleep(1)

        self.hpd.write(b'sensorStart')
        time.sleep(1)


    def hpd_output_latency(self, delay_appear, delay_disappear):
        """Sets the HPD sensor output delay time

        Args:
            hpd (obj): The UART object for the HPD Sensor
            delay_appear (int): When a target is detected, delay the output time of sensing result, range: 0~1638.375, unit: s
            delay_disappear (int): When the target is no longer detected, delay the output time of sensing result, range: 0~1638.375, unit: s
        """

        delay_appear = delay_appear * 1000 / 25 # No clue what this / 25 does, taken directly from the Arduino library
        delay_appear = delay_disappear * 1000 / 25

        self.hpd.write(b'sensorStop')
        time.sleep(1)

        self.hpd.write(b"outputLatency -1 %d %d" % (delay_appear , delay_disappear))
        time.sleep(1)

        self.hpd.write(b'saveCfg 0x45670123 0xCDEF89AB 0x956128C6 0xDF54AC89')
        time.sleep(1)

        self.hpd.write(b'sensorStart')
        time.sleep(1)


    def hpd_detect_presensce(self):
        """Receive response from HPD Sensor and check if presence is detected

        Returns:
            bool: Presence of human in range of sensor
        """
        presence = self.hpd.readline()
        if presence != str("None"):
            presence = presence.decode()
            if len(presence) > 7:
                if presence[7] == str(1):
                    return True
                else:
                    return False
        