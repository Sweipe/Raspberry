# made by Alex Luu

# For raspberry
from gpiozero.pins.pigpio import PiGPIOFactory

import time
from gpiozero import AngularServo
from gpiozero import Servo
from gpiozero import DistanceSensor
import gpiozero
import explorerhat
import board
import neopixel

# For MQTT
from paho.mqtt.enums import MQTTProtocolVersion
#import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import paho
import time
import os
import json
import random as rnd
import math
import uuid
#import websockets
#import threading
import numpy as np
import struct

#import mqtt_rpi.py

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

# Must have for using this pin factory, along with above commands
factory = PiGPIOFactory(host='raspberrypi.local')

# MQTT details
port = 8883
server = 'fcc9c4202a6349fe835152164aa95227.s1.eu.hivemq.cloud'
admin = 'origin'
password = 'password1A'

# Neopixel
pixels = neopixel.NeoPixel(board.D18, 16) # 16 LEDs
pixelmode = 'default'

# Servo
pan_gpio_pin=17
tilt_gpio_pin=10
pServo = AngularServo(pan_gpio_pin,min_angle=0,max_angle=90,pin_factory=factory)
tServo = AngularServo(tilt_gpio_pin,min_angle=0,max_angle=90,pin_factory=factory)
pServo.value = 0.5
tServo.value = 0.5

# Distance sensor
echo_pin=4
trig_pin=5
sensor=DistanceSensor(echo=echo_pin,trigger=trig_pin,max_distance=4,pin_factory=factory)

"""
tilt starts up at 0 degree, and horizontala at 90 degeree

limits -16.56 to 90 degrees with servo.angle

90 is looking 12degrees down
-16.56 is looking 45 degree up
"""

# Help variables
delay = 0.06        # Delay waiting for new distance measurements
is_running = True   # Boolean check, allows commands to start or stop
led_index=0         # 

def PixelsToLongArray():
    long_array = []
    for i in range(16):
        long_array += pixels[i]
    return long_array

def RotateByValue(pan,tilt):
    global pServo
    global tServo
    pServo.value = pan
    tServo.value = tilt
    #time.sleep(0.05)

def RotateByAngle(pan,tilt):
    global pServo
    global tServo
    pServo.angle = pan
    tServo.angle = tilt
    #time.sleep(0.05)

def NextPattern():
    global led_index
    if pixelmode == 'default':
        pixels[led_index] = (0,0,0)
        led_index += 1
        if led_index > 15:
            led_index = 0
        pixels[led_index] = (10,0,0)
    if pixelmode == 'blink':
        if led_index == 0:
            led_index = 1
        else:
            led_index = 0
        for i in range(16):
            if led_index == 1:
                if i%2==0:
                    pixels[i] = (0,50,0)
                else:
                    if i%2==0:
                    pixels[i] = (0,0,0)
            else:
                if i%2==0:
                    pixels[i] = (0,0,0)
                else:
                    if i%2==0:
                    pixels[i] = (0,50,0)
    
def BundleData():
    data_ = {
    'pan':pServo.angle,
    'tilt':tServo.angle,
    'distance':sensor.distance*100,
    'ledvalues':PixelsToLongArray()
    }
    return data_

def ToBytes(data):
    pack = struct.pack(
    "<fff48B",  # float32 float32 float32 48*unsigned char
        data['pan'],
        data['tilt'],
        data['distance'],
        *data['ledvalues']  # array
    )
    return pack

def on_connect(client, userdata, flags, rc, properties):
    print("on_connect callback: " + str(rc))
    if rc == 0:
        mqttc.subscribe('command',2)
        print ("connected OK")
        mqttc.connected_flag = True
        return

queue_msg = []
def on_message(client, obj, msg):
    global is_running
    global pixelmode
    print("msg from topic " + msg.topic + ": " + str(msg.payload))
    if(msg.topic=='command'):
        data = json.loads(msg.payload)
        print(data)
        if data['command'] == 'startscan':
            is_running = True
            queue_msg.append({"topic":'status',"payload":'Running'})
        elif data['command'] == 'stopscan':
            is_running = False
            queue_msg.append({"topic":'status',"payload":'Stopped'})
        elif data['command'] == 'changemode':
            #pixelmode = data['mode']
            if pixelmode == 'default':
                pixelmode == 'blink'
            elif pixelmode == 'blink':
                pixelmode == 'default'
    
def on_publish(client, obj, mid, rc, properties):
    print("on_publish callback: " + str(mid))
    
def on_subscribe(client, obj, mid, granted_qos, properties):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))
    
mqttc = mqtt.Client(client_id="dev5",callback_api_version=mqtt.CallbackAPIVersion.VERSION2,protocol=mqtt.MQTTv5)
# Assign event callbacks
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe

# Set will
mqttc.will_set('status','fell',qos=2,retain=True)

# enable TLS for secure connection
mqttc.tls_set(tls_version= paho.mqtt.client.ssl.PROTOCOL_TLS)

# provide credentials
mqttc.username_pw_set(admin, password)

# Connect
mqttc.connect(server, port, clean_start=True)
mqttc.connected_flag = False

#wait in loop
while not mqttc.connected_flag:
    time.sleep (0.05)
    mqttc.loop()
    
# Announce activation
mqttc.publish('status', 'awake',retain=True,qos=1)
mqttc.loop()

def ClearTheQueue():
    if len(mqttc._out_messages)<10 and len(queue_msg)>0:
        msg = queue_msg.pop(0)
        _retain = False
        if msg['topic'] == 'status' or msg['topic'] == 'action':
            _retain=True
        mqttc.publish(msg['topic'],msg['payload'],retain=_retain,qos=1)

while True:
    for p in range(90):
        for t in range(45,90):
            RotateByAngle(p,t)
            while not is_running:
                ClearTheQueue()
                time.sleep(delay)
                mqttc.loop()
            pServo.angle = p
            tServo.angle = t
            NextPattern()
            print('Distance: %s meter, pan: %s, tilt: %s' % (sensor.distance,pServo.angle,tServo.angle))
            data = ToBytes(BundleData())
            ClearTheQueue()
            while len(mqttc._out_messages)>=9:
                time.sleep(delay)
                mqttc.loop()
            mqttc.publish('data', data, retain=False, qos=1)
            mqttc.loop()
            time.sleep(delay)
    is_running = False
    mqttc.publish('action', data, retain=True, qos=1)