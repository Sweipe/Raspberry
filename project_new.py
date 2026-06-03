from gpiozero.pins.pigpio import PiGPIOFactory

import time
from gpiozero import AngularServo
from gpiozero import Servo
from gpiozero import DistanceSensor
import gpiozero
import explorerhat
import board
import neopixel

import paho.mqtt.client as mqtt
import paho
import time
import os
import json
import random as rnd
import math

port = 8883
server = 'fcc9c4202a6349fe835152164aa95227.s1.eu.hivemq.cloud'
admin = 'origin'
password = 'password1A'

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

# time delay for servo movement
delay = 0.06

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
    
# Define event callbacks
def on_connect(client, userdata, flags, rc):
    print("on_connect callback: " + str(rc))
    if rc == 0:
        mqttc.connected_flag = True
        print ("connected OK")
        return

is_running = True

def on_message(client, obj, msg):
    print("msg from topic " + msg.topic + ": " + str(msg.payload))
    if(msg.topic=='commands'):
        data = json.loads(msg.payload)
        print(data)
        if data['command'] == 'start':
            is_running = True
            pass
        if data['command'] == 'stop':
            is_running = False
            pass
        if data['command'] == 'changemode':
            pass
        # do something
        pass
    
def on_publish(client, obj, mid):
    print("on_publish callback: " + str(mid))
    
def on_subscribe(client, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))
    
mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
# Assign event callbacks
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe
topic = 'mytopic'

# enable TLS for secure connection
mqttc.tls_set(tls_version= paho.mqtt.client.ssl.PROTOCOL_TLS)

# provide credentials
mqttc.username_pw_set(admin, password)

# Connect
mqttc.connect(server, port)
mqttc.connected_flag = False

#wait in loop
while not mqttc.connected_flag:
    mqttc.loop()
    time.sleep (1)

mqttc.subscribe('commands', 2)
mqttc.loop_start()
    
while True:
    for i in range(90):
        pServo.angle = i
        pixels.fill((10,0,0))
        time.sleep(delay)
        pixels.fill((0,0,0))
        for t in range(45):
            while not is_running:
                time.sleep(delay)
            tServo.angle = 45+t
            Progress()
            print('Distance: %s meter, pan: %s, tilt: %s' % (sensor.distance,pServo.angle,tServo.angle))
            data = {
                'pan':pServo.angle,
                'tilt':tServo.angle, 
                'distance':sensor.distance,
                'pixelcommand':'one',
                'led':led_index,
                #'led':math.floor(rnd.random()*16),
                'color':'red'
            }
            mqttc.publish('data', json.dumps(data), retain=False)
            time.sleep(delay)