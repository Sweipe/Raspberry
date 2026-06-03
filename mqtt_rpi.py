#!/usr/bin/python
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

# Define event callbacks
def on_connect(client, userdata, flags, rc):
    print("on_connect callback: " + str(rc))
    if rc == 0:
        mqttc.connected_flag = True
        print ("connected OK")
        return
    
def on_message(client, obj, msg):
    print("msg from topic " + msg.topic + ": " + str(msg.payload))
    if(msg.topic=='commands'):
        data = json.loads(msg.payload)
        print(data)
        if data['command'] == 'start':
            pass
        if data['command'] == 'stop':
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
    
# Start subscribe, with QoS level 0
#mqttc.subscribe('data', 1)
mqttc.subscribe('commands', 2)
#time.sleep (1)

##### OPTION 1 #####
# start the network loop, do something, disconnect, and stop the loop
mqttc.loop_start()
#simulate raspberry
for i in range(1,1000):
    time.sleep(0.1)
    data = {
    'pan':rnd.random()*90,
    'tilt':rnd.random()*45, 
    'distance':rnd.random()*400,
    'pixelcommand':'one',
    'led':i,
    #'led':math.floor(rnd.random()*16),
    'color':'yellow'
}
    mqttc.publish('data', json.dumps(data), retain=False)

#mqttc.disconnect()
#mqttc.loop_stop()

##### OPTION 2 #####
# loop forever, implement the callbacks to do something
#mqttc.loop_forever()