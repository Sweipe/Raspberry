from gpiozero.pins.pigpio import PiGPIOFactory

import time
from gpiozero import AngularServo
from gpiozero import Servo
import gpiozero
import explorerhat

print("""
Two sg90 servos, one for vertical tilt and one for horizontal.
Tilt-servo has limitations 90 degrees with values 0 to 1. Possible wrongly assembled.
Therefore Pan-servo has limations 90 degree with values -1 to 1 with 0 roughly facing forward.
commands for running the code without jitter:
sudo gpiod
...the rest is handled by python.

Press CTRL+C to exit.

""")                                                                                                                    

factory = PiGPIOFactory(host='raspberrypi.local')

max = 90
servo = AngularServo(18,min_angle=0,max_angle=max,pin_factory=factory)
#servo = Servo(18)

threshold = 2.5
#delay = 0.025
delay = 1

def rotate(time):
    sleep_time = time-0.02
    explorerhat.output.one.on()
    time.sleep(time)
    explorerhat.output.one.off()
    time.sleep(sleep_time)
    
while True:
    #V2  = explorerhat.analog.one.read()
    #V1 = V - V2
    #R2 = V2*(R1/V1)
    #print('  {0:5.2f} volts   {1:5.2f} ohms'.format(round(V2,2), round(R2,2)))

    """servo.value = 0.5
    break
    time.sleep(10)
    servo.max()
    break"""
    for i in range(max):
        servo.angle = i
        time.sleep(0.05)
    for i in range(max):
        servo.angle = max-i
        time.sleep(0.05)
    #servo.value = 1
    #time.sleep(5)
    """servo.value = 1
    time.sleep(10)"""