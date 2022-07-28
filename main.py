'''
/*
 * Copyright 2010-2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License").
 * You may not use this file except in compliance with the License.
 * A copy of the License is located at
 *
 *  http://aws.amazon.com/apache2.0
 *
 * or in the "license" file accompanying this file. This file is distributed
 * on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
 * express or implied. See the License for the specific language governing
 * permissions and limitations under the License.
 */
 '''
# used aws-iot-device-sdk-python
# from "basicPubSubAsync" sample

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import logging
import time
import config # global constants for receiving message and flag
import json
from pymongo import MongoClient
import datetime
import argparse


# General message notification callback
def customOnMessage(message):
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    # parse payload:
    parsedMessage = json.loads(message.payload)
    # response preparation
    if parsedMessage["message"] == 'color':
        config.responseMessage = "White"
    else:
        config.responseMessage = "unknown query"
    # printing results
    print("--------------")
    print("query is of : " + parsedMessage["message"])
    print("Returning result on topic:" + topic_pub)
    print("--------------\n\n")

    # setting flag for publish
    config.queryReceived = True

    # writing data to local mongodb
    # Connect to mongodb localhost and create database collection for IoT
    uri = "mongodb://localhost:27017"
    client = MongoClient(uri)
    # database and collection code goes here
    db = client.iot_data
    coll = db.queries_answers
    now = datetime.datetime.now()
    docs = [
        # {"query": parsedMessage["message"], "response": config.responseMessage}
        {"query": parsedMessage["message"], "response": config.responseMessage, "time": now}
    ]
    result = coll.insert_many(docs)
    print(result.inserted_ids)
    # Close the connection to MongoDB when you're done.
    client.close()


# Suback callback
def customSubackCallback(mid, data):
    print("Received SUBACK packet id: ")
    print(mid)
    print("Granted QoS: ")
    print(data)
    print("++++++++++++++\n\n")


# Puback callback
def customPubackCallback(mid):
    print("Received PUBACK packet id: ")
    print(mid)
    print("++++++++++++++\n\n")


"""
# Read in command-line parameters
parser = argparse.ArgumentParser()
parser.add_argument("-e", "--endpoint", action="store", required=True, dest="host", help="Your AWS IoT custom endpoint")
parser.add_argument("-r", "--rootCA", action="store", required=True, dest="rootCAPath", help="Root CA file path")
parser.add_argument("-c", "--cert", action="store", dest="certificatePath", help="Certificate file path")
parser.add_argument("-k", "--key", action="store", dest="privateKeyPath", help="Private key file path")
parser.add_argument("-p", "--port", action="store", dest="port", type=int, help="Port number override")
parser.add_argument("-w", "--websocket", action="store_true", dest="useWebsocket", default=False,
                    help="Use MQTT over WebSocket")
parser.add_argument("-id", "--clientId", action="store", dest="clientId", default="basicPubSub",
                    help="Targeted client id")
parser.add_argument("-t", "--topic", action="store", dest="topic", default="sdk/test/Python", help="Targeted topic")

args = parser.parse_args()
host = args.host
rootCAPath = args.rootCAPath
certificatePath = args.certificatePath
privateKeyPath = args.privateKeyPath
port = args.port
useWebsocket = args.useWebsocket
clientId = args.clientId
topic = args.topic
"""

# replaced above parser with fixed values for code debugging in pycharm
host = "a4xe72lr2lks9-ats.iot.us-east-1.amazonaws.com"
rootCAPath = "secure/AmazonRootCA1.pem"
certificatePath = "secure/certificate.pem.crt"
privateKeyPath = "secure/private.pem.key"
port = 0
useWebsocket = False
clientId = "basicPubSub"
topic_sub = "sdk/test/Sub" # note that sub will be Pub in MQTT test client
topic_pub = "sdk/test/Pub" # note that pub will be Sub in MQTT test client
#topic = "sdk/test/IoT_testing"
mode = "both"
defaultMessage = "Hello World!"

if useWebsocket and certificatePath and privateKeyPath:
    print("X.509 cert authentication and WebSocket are mutual exclusive. Please pick one.")
    exit(2)

if not useWebsocket and (not certificatePath or not privateKeyPath):
    print("Missing credentials for authentication.")
    exit(2)

# Port defaults
if useWebsocket and not port:  # When no port override for WebSocket, default to 443
    port = 443
if not useWebsocket and not port:  # When no port override for non-WebSocket, default to 8883
    port = 8883

# Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

# Init AWSIoTMQTTClient
myAWSIoTMQTTClient = None
if useWebsocket:
    myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId, useWebsocket=True)
    myAWSIoTMQTTClient.configureEndpoint(host, port)
    myAWSIoTMQTTClient.configureCredentials(rootCAPath)
else:
    myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId)
    myAWSIoTMQTTClient.configureEndpoint(host, port)
    myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTClient connection configuration
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
myAWSIoTMQTTClient.onMessage = customOnMessage

# Connect and subscribe to AWS IoT
myAWSIoTMQTTClient.connect()
# Note that we are not putting a message callback here. We are using the general message notification callback.
myAWSIoTMQTTClient.subscribeAsync(topic_sub, 1, ackCallback=customSubackCallback)
time.sleep(2)

# Publish to the same topic in a loop forever
loopCount = 0
while True:
    message = {}
    message['message'] = defaultMessage
    message['sequence'] = loopCount
    messageJson = json.dumps(message)
    if config.queryReceived:
        myAWSIoTMQTTClient.publishAsync(topic_pub, config.responseMessage, 1, ackCallback=customPubackCallback)
        print("Sent message = " + config.responseMessage)
    config.queryReceived = False
    loopCount += 1
    time.sleep(1)
