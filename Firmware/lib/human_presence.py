
import lib.onionGpio as onionGpio
from lib.DFRobot_mmWave import *


HPD_GPIO_PIN = 2

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

def init_hdp():
    setup_hpd(0,0,0,1)
    gpioObject  = onionGpio.OnionGpio(HPD_GPIO_PIN)
    status  = gpioObject.setInputDirection()
def read_presence():
    gpioObject  = onionGpio.OnionGpio(HPD_GPIO_PIN)
    return int(gpioObject.getValue())

if __name__ == "__main__":
    init_hdp()
    while True:
        print(read_presence())
        time.sleep(1)
        