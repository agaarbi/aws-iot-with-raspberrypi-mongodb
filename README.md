# aws-iot-with-raspberrypi-mongodb
Connecting Raspberry Pi with AWS IoT Core and storing data locally in MongoDB

* Used aws-iot-device-sdk-python https://github.com/aws/aws-iot-device-sdk-python
* For code base, "basicPubSubAsync" is used from sample
* Add Device in AWS IoT-Core
  * Manage > All devices > Thing > Create things
  * Create single thing
  * Named device (i.e. RaspberryPi-testing")
  * Auto-generate a new certificate (recommended)
  * Create Policy, name the policy and enter "*" in fields to allow all access (i.e. RaspberryPi-testing-policy)
  * Download keys and certificates in folder (i.e. "secure") and ignore the same from git-repo if public
  * Go to settings and copy "End Point" and paste in "host"

# MongoDB
* pip install pymongo
* install and start mongodb on local machine (RaspberryPi)
  * https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-ubuntu/
  * sudo systemctl start mongod
  * sudo systemctl status mongod
  * sudo systemctl stop mongod

# Testing the code
* Test Device in AWS IoT-Core
  * Test > MQTT test Client
  * Subscribe to a topic "sdk/test/Pub"
  * Publish to topic "sdk/test/Sub"
    * Send "message" : "color", and it will return White, in any other case it will return unknown query
    * Same will be written in local mongodb database, use MongoDB Compass and connect to local db
    * 