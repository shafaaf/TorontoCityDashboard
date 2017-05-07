##############################################################

# Store weather data from unix timestamp 1467165601
# for every 3600 seconds
# Using type as the timestamp in the api field to avoid 
# duplicate entries

##############################################################

import requests
import json

# Make sure ES is up and running
res = requests.get('http://localhost:9200')
print "\nElastic search GET request:\n{}".format(res.content)

#Connect to our elastic search cluster first
host = 'localhost'
port = 9200
from elasticsearch import Elasticsearch
es = Elasticsearch([{'host': host, 'port': port}], timeout=30, max_retries=10, retry_on_timeout=True)
if not es.ping():
    raise ValueError("Connection failed")
else:
	print "Connected to elastic search..\n"


# ES Mappings and index being made

# Need a timeStampDateSearchable field of type date
# to make daily, weekly, monthly reports
myMappings = {
			    "mappings" : 
			    {
			        "_default_" : 
			        {
			        	"_all":       
			        	{ 
			        		"enabled": "false"  
			        	},
			            "properties" : 
			            {
			                "timestampDateSearchable" : 
			                { 
			                	"type" : "date",
			                	"format": "epoch_second" 
			                }
			            }
			        }
			    }
			}

# Create index			
es.indices.create(index='weather', body = myMappings)

# Parameters needed to get api data
weatherTimeStampUrl = "http://portal.cvst.ca/api/0.1/weather?timestamp="
currentTimeStamp = 1467165601 # Use data at this timestamp as it is the earliest timestamp with data found
fullWeatherTimeStampUrl = weatherTimeStampUrl + str(currentTimeStamp) # Make full url
timeInterval = 3600 # Time interval for getting data -> 3600 seconds (1 hour)

# Get data from weather api
for apiCalls in range(0,3):
	print "\n\nCount: {} -> Now trying to access public api at: {}  ...".format(apiCalls, fullWeatherTimeStampUrl)
	r = requests.get(fullWeatherTimeStampUrl)
	print "Response status code: {}".format(r.status_code)
	# Todo: need to check if status code is 4xx, in which case may need to try again

	apiData = json.loads(r.content)
	apiDataLength = len(apiData)
	print "\nAdding in weather data for timestamp {}..".format(currentTimeStamp)

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

		#Own fields
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

# Saving next timestamp to start storing into ES again
print "\nWriting to file: weatherTimeStamp.txt the timeStamp: {} from which need to update again later on...\n".format(currentTimeStamp)
with open('weatherTimeStamp.txt', 'w') as f:
	f.write(str(currentTimeStamp))
