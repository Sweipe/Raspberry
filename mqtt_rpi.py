#!/usr/bin/python
from paho.mqtt.enums import MQTTProtocolVersion
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import paho
import time
import os
import json
import random as rnd
import math
import uuid
import websockets
import threading
import numpy as np
# import logging
# logging.basicConfig(level=logging.DEBUG)

port = 8884
server = 'fcc9c4202a6349fe835152164aa95227.s1.eu.hivemq.cloud'
admin = 'origin2'
password = 'password1A'
data_sent = False
before = 0
ontheways = 0

# Define event callbacks
def on_connect(client, userdata, flags, rc, properties):
    print("on_connect callback: " + str(rc))
    if rc == 0:
        mqttc.connected_flag = True
        print ("connected OK")
        return
        
def on_disconnect(client, userdata, flags, rc, properties):
    print("disconnected: " + str(rc))
    
def on_message(client, obj, msg):
    # global data_sent
    # data_sent=True
    #print("msg from topic " + msg.topic + ": " + str(msg.payload))
    if(msg.topic=='commands'):
        data = json.loads(msg.payload)
        #print(data)
        if data['command'] == 'start':
            pass
        if data['command'] == 'stop':
            pass
        if data['command'] == 'changemode':
            pass
        # do something
        pass
    #print(data_sent)
    
def on_publish(client, obj, mid, rc, properties):
    print(f"on_publish callback: {str(mid)}, delay: {time.time()-before} seconds")
    
    
def on_subscribe(client, obj, mid, granted_qos, properties):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))
    
def on_log(client, userdata, level, buf):
    print(level, buf)
    
#str(uuid.uuid4()
mqttc = mqtt.Client(client_id="dev5",callback_api_version=mqtt.CallbackAPIVersion.VERSION2,transport='websockets',protocol=mqtt.MQTTv5)
mqttc.ws_set_options(path="/mqtt")
# Assign event callbacks
#mqttc.enable_logger()

mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe
mqttc.on_disconnect = on_disconnect
#mqttc.on_log = on_log
#topic = 'mytopic'

# enable TLS for secure connection
mqttc.tls_set(tls_version= paho.mqtt.client.ssl.PROTOCOL_TLS)

# provide credentials
mqttc.username_pw_set(admin, password)
#mqttc.max_inflight_messages_set(1000)
mqttc.max_inflight_messages_set(10)
mqttc.max_queued_messages_set(2000)
print(mqttc.max_inflight_messages,mqttc.max_queued_messages)

# Set will
mqttc.will_set('status','fell',qos=2,retain=True)

# Connect
# connect_properties = mqtt.Properties(mqtt.PacketTypes.CONNECT)
# connect_properties.ReceiveMaximum = 10
#mqttc.connect_async(server, port,clean_start=True,keepalive=60)
mqttc.connect(server, port, clean_start=True)
mqttc.connected_flag = False

#sem = threading.BoundedSemaphore(10)

#wait in loop
#mqttc.loop_start()
while not mqttc.is_connected():
    time.sleep(1)
    mqttc.loop()
#mqttc.loop_stop()

def new_data(i):
    data_ = {
    'pan':rnd.random()*90,
    'tilt':rnd.random()*45,
    'distance':rnd.random()*400,
    }
    ledvalues = []
    for i in range(16*3):
        ledvalues.append(math.floor(rnd.random()*256))
    data_['ledvalues'] = ledvalues
    #print(data_)
    return data_

import struct
def new_bytes(data):
    pack = struct.pack(
    #"<fffBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB>",
    "<fff48B",
        data['pan'],
        data['tilt'],
        data['distance'],
        *data['ledvalues']
    )
    return pack

before = time.time()
infos=[]
#quit()
msgs=[]
iterations = 5000

mqttc.publish('status', 'awake',qos=1)
#quit()
mqttc.loop_start()
while not mqttc.is_connected():
    time.sleep(0.001)
for i in range(1000):
    
    # method 1, send one and one
    time.sleep(0.06)
    #mqttc.publish('data', json.dumps(new_data(i)),qos=1)
    mqttc.publish('data', new_bytes(new_data(i)),qos=1)
    while len(mqttc._out_messages)>5:
        #mqttc.loop()
        time.sleep(0.001)
        
    # method 2, send in "batches" aka array of payload(s)
    # time.sleep(0.06)
    # msgs.append(new_data(i))
    # if(len(msgs)>=30 or i>=iterations-1):
        # info = mqttc.publish('data', json.dumps(msgs),qos=2)
        # msgs=[]
        
    #mqttc.loop()
    
while len(mqttc._out_messages) > 0 or mqttc._inflight_messages > 0:
    #mqttc.loop()
    time.sleep(0.001)
print("Time taken:",time.time()-before)
mqttc.publish('status', 'asleep',qos=1,retain=True)
# print("Waiting for publish")
# for info in infos:
    # info.wait_for_publish()

print("It took %s seconds", (time.time()-before))

mqttc.loop_stop()
mqttc.disconnect()
while mqttc.is_connected():
    time.sleep(0.001)
print("Connection done")