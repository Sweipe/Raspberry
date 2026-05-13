import explorerhat
from gpiozero.pins.pigpio import PiGPIOFactory
import time

factory = PiGPIOFactory(host='raspberrypi.local')


import gpiozero
from gpiozero import DistanceSensor

echo_pin = 7
trig_pin= 12
sensor = DistanceSensor(echo=echo_pin, trigger=trig_pin)

while True:
    print('Distance: ',sensor.distance*100)
    sleep(1)