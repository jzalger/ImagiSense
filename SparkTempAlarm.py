"""
SparkTempAlarm.py
J. Zalger, March 2015

SparkTempAlarm uses a simple Spark Core based temperature sensor to adjust the temperature of a Nest
thermostat when the measured temperature falls below a set threshold.

The Spark Core is a Wifi Enabled ARM microcontroller which uses a simple cloud based API for communication.
The Spark.publish() call opens a Server Side Event (SSE) HTTP stream with JSON encoded temperature events.

Nest is a Wifi connected learning thermostat which allows temperature control through its associate API.
SparkTempAlarm connects to the Nest and issues a request to increase the temperature by a specified delta.
"""
__version__ = 0.1

from sseclient import SSEClient
import json
import nest
import imsCredentials   # File containing authentication details for Spark Device and Nest
import smtplib

# Spark Core Stream Configuration
streamURL = 'https://api.spark.io/v1/devices/' + imsCredentials.deviceID + '/events/temperature?access_token=' + imsCredentials.token

# Nest API Configuration
napi = nest.Nest(imsCredentials.nestUsername, imsCredentials.nestPassword)
nlt = napi.structures[0].devices[0]

# Set Alarm temperature, and the amount to raise by if alarm is triggered
minTemp = 10.0
alarmTempDelta = 2.0
tempAlarm = False


def activateHeat(tempDelta, thermostat):
    """Raise the temperature by tempDelta on thermostat"""
    currentTemp = thermostat.temperature
    newTemp = currentTemp + tempDelta
    thermostat.temperature = newTemp
    sendAlarmEmail(currentTemp, minTemp, newTemp)
    print "Adjusting temperature from %s to %s" % (currentTemp, newTemp)


def sendAlarmEmail(currentTemp, alarmTemp, newTemp):
    """Send an email alert for the low temp warning"""
    session = smtplib.SMTP('smtp.gmail.com', 587)
    session.ehlo()
    session.starttls()
    session.login(imsCredentials.gmailUser, imsCredentials.gmailPass)

    headers = "\r\n".join(["from: " + imsCredentials.gmailUser,
                           "subject: Temperature Alarm Activated",
                           "to: " + imsCredentials.alarmEmail,
                           "mime-version: 1.0",
                           "content-type: text/html"])
    emailBody = "<h1>A temperature alarm has been activated.</h1>The measured temperature is <b>%s degrees</b>, exceeding the threashold" \
                " of %s degrees. The temperature has now been set to <b>%s degrees</b>." % (currentTemp, alarmTemp, newTemp)
    content = headers + "\r\n\r\n" + emailBody
    session.sendmail(imsCredentials.gmailUser, imsCredentials.alarmEmail, content)
    print "Sent alert email to %s" % imsCredentials.alarmEmail

# Open Spark Core Publish Stream
messages = SSEClient(streamURL)

for msg in messages:
    if 'data' in msg.data:
        package = json.loads(msg.data)
        temp = float(package['data'])
        if temp < minTemp and tempAlarm is False:
            tempAlarm = True
            activateHeat(alarmTempDelta, nlt)
        elif temp > minTemp and tempAlarm is True:
            # Reset the alarm if temperature out of warning zone
            tempAlarm = False