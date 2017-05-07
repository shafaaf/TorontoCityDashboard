##############################################################

# Update weather data till latest value
# Run this after running storeWeatherData.py

##############################################################

# Function to round down
def roundDown(num, divisor):
    lower3600 = num - (num%divisor)
    return (lower3600 + 1)

##############################################################

import sys

# Make sure ES is up and running
import requests
res = requests.get('http://localhost:9200')
print "\nElastic search GET request:\n{}".format(res.content)


# Connect to our elastic search cluster first
host = 'localhost'
port = 9200
from elasticsearch import Elasticsearch
# http://stackoverflow.com/questions/25908484/how-to-fix-read-timed-out-in-elasticsearch
es = Elasticsearch([{'host': host, 'port': port}], timeout=30, max_retries=10, retry_on_timeout=True)
if not es.ping():
    raise ValueError("Connection failed")
else:
	print "Connected to elastic search..\n"



#Get current timestamp value from where need to store again
with open('weatherTimeStamp.txt', 'r') as f:
	currentTimeStamp = int(f.read())
print "\ncurrentTimeStamp from which need to store: {}".format(currentTimeStamp)


# Get ending timestamp till which ES will store - present time formatted
import time
endTimeStamp = time.time()
endTimeStampRoundedDown = roundDown(endTimeStamp, 3600)
print "\nraw endTimeStamp is: {}".format(endTimeStamp)
print "endTimeStampRoundedDown to nearest 3601 is: {}".format(endTimeStampRoundedDown)

#----------------------------------------------------------------------------------------------------------------------------

# Log in to cvst portal, and then access the 
# restricted data:
from requests import session
import json
username = 'jhlk7272'
password = 'jhl9616'
values = {'username': username,
          'password': password}

# Parameters needed to login and get api data
cvstLoginUrl = "http://portal.cvst.ca/login"
weatherTimeStampUrl = "http://portal.cvst.ca/api/0.1/weather?timestamp="
fullWeatherTimeStampUrl = weatherTimeStampUrl + str(currentTimeStamp) # Make full url
apiCalls = 1 # Number of api calls
timeInterval = 3600


# Create session to send cookies
s = requests.session()
print "\n\nGoing to cvst portal to login for first time..."
r = s.post(cvstLoginUrl, data=values)
# Todo: Need a check here to see if logged in properly or not to cvst portal.

headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0' }

# Go through timstamps from start until reach the one to break on which is present time formatted
while True:
	print "\nCount: {} -> Now trying to access private api at: {}  ...".format(apiCalls, fullWeatherTimeStampUrl)
	
	# Try CVST api again if get error	
	while True:
		try:			
			r = s.get(fullWeatherTimeStampUrl, headers=headers)
			print "Response status code: {}".format(r.status_code)
			break
		except Exception as e: # catch *all* exceptions
			print("Oops!  Some weird error.")
			print str(e)
			print "Response status code: {}".format(r.status_code)
			print("Trying again...")

	# Todo: need to check if status code is 4xx, in which case may
	# need to authenticate again.

	apiData = json.loads(r.content)
	apiDataLength = len(apiData)
	print "\nAdding in data for timestamp {}:\n".format(currentTimeStamp)

#----------------------------------------------------------------------------------------------------------------------------
	
	# Looping though array of locations for current timestamp
	for i in range(0, apiDataLength):
		# Use locationId as document id. This is location with lowercases and no spaces 
		location = apiData[i]["location"]
		locationId = location.lower()
		locationId = locationId.replace(" ", "")
		#print "locationId after change is: {}".format(locationId)

		# Putting in as same order as seen in api
		myEntry = {}

		#Putting in unique identifier for each location in each timestamp
		myEntry["locationId"] = locationId
		# Putting in wind_mph, relative_humidity separately as easier to search, aggregate altogether
		myEntry["windMph"] = float(apiData[i]["current_observation"]["wind_mph"])
		myEntry["relativeHumidity"] = float(apiData[i]["current_observation"]["relative_humidity"][:-1]) #to remove the %
		myEntry["timestampDateSearchable"] = apiData[i]["timestamp"] # To seach as a datetype in report generator		

		

		#current_observation data
		myEntry["current_observation"] = {}
		myEntry["current_observation"]["observation_time"] = apiData[i]["current_observation"]["observation_time"]
		myEntry["current_observation"]["relative_humidity"] = apiData[i]["current_observation"]["relative_humidity"]
		myEntry["current_observation"]["temp_c"] = apiData[i]["current_observation"]["temp_c"]
		myEntry["current_observation"]["temperature_string"] = apiData[i]["current_observation"]["temperature_string"]
		myEntry["current_observation"]["timestamp"] = apiData[i]["current_observation"]["timestamp"]
		myEntry["current_observation"]["visibility_mi"] = apiData[i]["current_observation"]["visibility_mi"]
		myEntry["current_observation"]["weather"] = apiData[i]["current_observation"]["weather"]
		myEntry["current_observation"]["wind_dir"] = apiData[i]["current_observation"]["wind_dir"]
		myEntry["current_observation"]["wind_mph"] = apiData[i]["current_observation"]["wind_mph"]
		myEntry["current_observation"]["wind_string"] = apiData[i]["current_observation"]["wind_string"]

		#display_location data
		myEntry["display_location"] = {}
		myEntry["display_location"]["full"] = apiData[i]["display_location"]["full"]
		myEntry["display_location"]["latitude"] = apiData[i]["display_location"]["latitude"]
		myEntry["display_location"]["longitude"] = apiData[i]["display_location"]["longitude"]

		#other data
		myEntry["id"] = apiData[i]["id"]
		myEntry["location"] = apiData[i]["location"]

		#observation_location
		myEntry["observation_location"] = {}
		myEntry["observation_location"]["full"] = apiData[i]["observation_location"]["full"]
		myEntry["observation_location"]["latitude"] = apiData[i]["observation_location"]["latitude"]
		myEntry["observation_location"]["longitude"] = apiData[i]["observation_location"]["longitude"]

		#other data
		myEntry["temp_c"] = apiData[i]["temp_c"]
		myEntry["timestamp"] = apiData[i]["timestamp"]

		#print "myEntry is:\n {}".format(myEntry)

		# Store in ES with type as the timestamp field not NOT the current timestamp.
		# This done to prevent duplicates
		myDocType = apiData[i]["timestamp"]
		es.index(index='weather', doc_type = myDocType, id = locationId, body = myEntry, request_timeout=10000)		
#----------------------------------------------------------------------------------------------------------------------------

	#Editing parameters to get next timestamp
	currentTimeStamp = currentTimeStamp + timeInterval
	fullWeatherTimeStampUrl = weatherTimeStampUrl + str(currentTimeStamp)
	apiCalls = apiCalls + 1
	
	# Update file to reflect till what timestamp have values
	if(apiCalls%10 == 0):
		with open('weatherTimeStamp.txt', 'w') as f:
			f.write(str(currentTimeStamp))

	# Will write till latest timestamp at that point when script first ran.
	# So later on run this script again to get the latest data till current time
	if currentTimeStamp >= endTimeStamp:
		print "\nWriting to file: elasticSearchTimeStamp.txt the timeStamp: {} from which need to update again later on...\n".format(currentTimeStamp)
		with open('weatherTimeStamp.txt', 'w') as f:
			f.write(str(currentTimeStamp))
		break

