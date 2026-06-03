from gpiozero.pins.pigpio import PiGPIOFactory

import time
from gpiozero import AngularServo
from gpiozero import Servo
from gpiozero import DistanceSensor
import gpiozero
import explorerhat
import board
import neopixel

pixels = neopixel.NeoPixel(board.D18, 16) # 16 LEDs

print("""
Two sg90 servos, one for vertical tilt and one for horizontal.
Tilt-servo has limitations 90 degrees with values 0 to 1. Possible wrongly assembled.
Therefore Pan-servo has limations 90 degree with values -1 to 1 with 0 roughly facing forward.

One Ultrasonic Sensor HC-04SR for measuring distance up to 400cm and one pixelring for displaying progress.
commands needed to run this:
sudo gpiod
sudo -E env PATH=$PATH python project.py

Press CTRL+C to exit.
""")

factory = PiGPIOFactory(host='raspberrypi.local')

max = 90
#gpio_pin = 18
pan_gpio_pin=17
tilt_gpio_pin=10
pServo = AngularServo(pan_gpio_pin,min_angle=0,max_angle=90,pin_factory=factory)
tServo = AngularServo(tilt_gpio_pin,min_angle=0,max_angle=90,pin_factory=factory)
pServo.value = 0.52
tServo.value = 0.52
#servo = Servo(18)


delay = 0.01

echo_pin=4
trig_pin=5
sensor=DistanceSensor(echo=echo_pin,trigger=trig_pin,max_distance=4,pin_factory=factory)
led_index=0


def RotateByValue(pan,tilt):
    pServo.value = pan
    tServo.value = tilt
    time.sleep(0.05)

def RotateByAngle(pan,tilt):
    pServo.angle = pan
    tServo.angle = tilt
    time.sleep(0.05)

def Progress():
    global led_index
    pixels[led_index] = (0,0,0)
    led_index += 1
    if led_index > 15:
        led_index = 0
    pixels[led_index] = (10,0,0)
    
while True:
    for i in range(90):
        pServo.angle = i
        pixels.fill((10,0,0))
        time.sleep(delay)
        pixels.fill((0,0,0))
        for t in range(45):
            tServo.angle = 45+t
            Progress()
            print('Distance: %s meter, pan: %s, tilt: %s' % (sensor.distance,pServo.angle,tServo.angle))
            time.sleep(delay)