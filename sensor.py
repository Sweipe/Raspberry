import explorerhat
from gpiozero.pins.pigpio import PiGPIOFactory
import time

factory = PiGPIOFactory(host='raspberrypi.local')


import gpiozero
from gpiozero import DistanceSensor

echo_pin = 4
trig_pin = 18
sensor = DistanceSensor(echo=echo_pin, trigger=trig_pin, max_distance=4,pin_factory=factory)

while True:
    print('Distance: ',sensor.distance)
    #print('Hello')
    time.sleep(0.01)