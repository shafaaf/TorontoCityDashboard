##############################################################

# Store ttc data from unix timestamp 1422266401
# for every 60 seconds
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
es.indices.create(index='ttc', body = myMappings)


# Access by first logging in to cvst portal, and then access the 
# restricted data: /ttc?timestamp=blahbhah api
from requests import session
import json
username = 'jhlk7272'
password = 'jhl9616'
values = {'username': username,
          'password': password}


# Parameters needed to get api data
cvstLoginUrl = "http://portal.cvst.ca/login"
ttcTimeStampUrl = "http://portal.cvst.ca/api/0.1/ttc?timestamp="
currentTimeStamp = 1422266401 # Use data at this timestamp as it is the earliest timestamp with data found
fullTTCTimeStampUrl = ttcTimeStampUrl + str(currentTimeStamp) # Make full url
timeInterval = 300 # Time interval for getting data -> 300 seconds (5 minutes)

# Bulk data to store in ES using bulk api
bulkData = []

# Create session to send cookies
with session() as c:
	print "\n\nGoing to cvst portal to login for first time..."
	r = c.post(cvstLoginUrl, data=values)
	# Todo: Need a check here to see if logged in properly or not to cvst portal.

	# Go through array of data entries. For this script - access first 3
	for apiCalls in range(0,3):
		print "\n\nCount: {} -> Now trying to access api at: {}  ...".format(apiCalls, fullTTCTimeStampUrl)
		r = c.get(fullTTCTimeStampUrl)
		print "Response status code: {}".format(r.status_code)
		# Todo: need to check if status code is 4xx, in which case may need to try again

		apiData = json.loads(r.content)
		apiDataLength = len(apiData)
		print "\nAdding in TTC data for timestamp {}..".format(currentTimeStamp)

	#----------------------------------------------------------------------------------------------------------------------------

		# Looping though array of vehicle_ids for current timestamp
		for i in range(0, apiDataLength):
			# Use vehicle_id as document id
			myVehicleId = apiData[i]["vehicle_id"]

			# Get other data for this timestamp and this vehicle.
			# Putting in as same order as seen in api
			myEntry = {}

			# Making route name easier to search for by lowercasing and removing spaces
			myRouteName = apiData[i]["route_name"]
			myRouteName = myRouteName.lower()
			myRouteName = myRouteName.replace(" ", "")
			myEntry["routeName"] = myRouteName

			# Own fields
			myEntry["timestampDateSearchable"] = apiData[i]["timestamp"] # To seach as a datetype in report generator		

			# Their fields
			myEntry["GPStime"] = apiData[i]["GPStime"]
			
			myEntry["coordinates"] = []
			myEntry["coordinates"].append(apiData[i]["coordinates"][0])
			myEntry["coordinates"].append(apiData[i]["coordinates"][1])

			myEntry["dateTime"] = apiData[i]["dateTime"]
			myEntry["dirTag"] = apiData[i]["dirTag"]
			myEntry["heading"] = apiData[i]["heading"]
			myEntry["last_update"] = apiData[i]["last_update"]
			myEntry["predictable"] = apiData[i]["predictable"]
			myEntry["routeNumber"] = apiData[i]["routeNumber"]
			myEntry["route_name"] = apiData[i]["route_name"]
			myEntry["timestamp"] = apiData[i]["timestamp"]
			myEntry["vehicle_id"] = apiData[i]["vehicle_id"]
			
			#print "myEntry is:\n {}".format(myEntry)

			# Setting up bulk
			# Original Code: bulkHead = {"index":{"_index":"ttc", "_type":"cot"}} #Looks this this
			bulkHead = {}
			bulkHead["index"] = {}
			
			 # Add in index
			bulkHead["index"]["_index"] = "ttc"
			
			# Add in type
			myDocType = apiData[i]["timestamp"] # correct
			#myDocType = currentTimeStamp # testing
			bulkHead["index"]["_type"] = myDocType
			
			# Formatting bulkData
			bulkData.append(bulkHead)
			bulkData.append(myEntry)
			#es.index(index='ttc', doc_type = myDocType, id = myVehicleId, body = myEntry, request_timeout=30) #old

	#----------------------------------------------------------------------------------------------------------------------------

		# Editing parameters to get next timestamp
		currentTimeStamp = currentTimeStamp + timeInterval
		fullTTCTimeStampUrl = ttcTimeStampUrl + str(currentTimeStamp)

	# Bulk indexing to ES
	print "Bulk indexing now..."
	print "Bulk latest head is: {}".format(bulkHead)
	#print "Bulk data is: {}".format(bulkData)
	
	res = es.bulk(index = 'ttc', body = bulkData, refresh = True, request_timeout=10000)
	bulkData = []

	# Saving next timestamp to start storing into ES again
	print "\nWriting to file: ttcTimeStamp.txt the timeStamp: {} from which need to update again later on...\n".format(currentTimeStamp)
	with open('ttcTimeStamp.txt', 'w') as f:
		f.write(str(currentTimeStamp))
