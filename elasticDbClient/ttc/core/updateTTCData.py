##############################################################

# Update ttc data till latest value
# Run this after running storeTTCData.py

##############################################################

# Function to round down
def roundDown(num, divisor):
    lower300 = num - (num%divisor)
    return (lower300 + 1)

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
es = Elasticsearch([{'host': host, 'port': port}], timeout=30, max_retries=10, retry_on_timeout=True)
if not es.ping():
    raise ValueError("Connection failed")
else:
	print "Connected to elastic search..\n"

# Mappings already made in storeTTC script so do not need that here

# Get current timestamp value from where need to store again
with open('ttcTimeStamp.txt', 'r') as f:
	currentTimeStamp = int(f.read())
print "\ncurrentTimeStamp from which need to store: {}".format(currentTimeStamp)


# Get ending timestamp till which ES will store - present time formatted
import time
endTimeStamp = time.time()
endTimeStampRoundedDown = roundDown(endTimeStamp, 300) # 5 min interval
print "\nraw endTimeStamp is: {}".format(endTimeStamp)
print "endTimeStampRoundedDown to nearest 301 is: {}".format(endTimeStampRoundedDown)

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
ttcTimeStampUrl = "http://portal.cvst.ca/api/0.1/ttc?timestamp="
fullTTCTimeStampUrl = ttcTimeStampUrl + str(currentTimeStamp) # Make full url
apiCalls = 1 # Number of api calls made
timeInterval = 300 # 5 mins, even though actual TTC data refreshes every 1 minute

# Bulk data to store in ES using bulk api
bulkData = []

# Create session to send cookies
s = requests.session()
print "\n\nGoing to cvst portal to login for first time..."
r = s.post(cvstLoginUrl, data=values)
# Todo: Need a check here to see if logged in properly or not to cvst portal.

headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0' }

# Go through timstamps from start until reach the one to break on which is present time formatted
while True:
	print "\nCount: {} -> Now trying to access private api at: {}  ...".format(apiCalls, fullTTCTimeStampUrl)

	# Try CVST api again if get some exception
	while True:
		try:			
			r = s.get(fullTTCTimeStampUrl, headers=headers)
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
	print "\nAdding in TTC data for timestamp {}:\n".format(currentTimeStamp)

#----------------------------------------------------------------------------------------------------------------------------

	# Looping though array of vehicles for current timestamp
	for i in range(0, apiDataLength):
		# Use vehicle_id as document id - Not being used
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


		# Setting up bulk
		# Original Code: bulkHead = {"index":{"_index":"ttc", "_type":"cot"}} #Looks this this
		bulkHead = {}
		bulkHead["index"] = {}

		 # Add in index
		bulkHead["index"]["_index"] = "ttc"

		# Add in type
		myDocType = apiData[i]["timestamp"] # Correct
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
	apiCalls = apiCalls + 1	

	# Store to Elastic Search after getting data from a lot of api calls
	if(apiCalls%100 == 0):
		# Bulk indexing to ES
		print "Bulk indexing now ..."
		print "Bulk latest head is: {}".format(bulkHead)
		#print "Bulk data is: {}".format(bulkData)
		
		res = es.bulk(index = 'ttc', body = bulkData, refresh = True, request_timeout=10000)
		bulkData = []
		print "Bulking complete till timestamp: {}".format(currentTimeStamp - timeInterval)
		
		# Update file to reflect till what timestamp have TTC data. Start updating from this timestamp again
		with open('ttcTimeStamp.txt', 'w') as f:
			f.write(str(currentTimeStamp))
	
	# Finished storing till the time user started script
	if currentTimeStamp >= endTimeStamp:
		# Bulk indexing whatever left to ES
		print "Reached current time and so bulk indexing whatever left now ..."
		print "Bulk latest head is: {}".format(bulkHead)
		#print "Bulk data is: {}".format(bulkData)
		
		res = es.bulk(index = 'ttc', body = bulkData, refresh = True, request_timeout=10000)
		bulkData = []
		print "Bulking complete till timestamp: {}".format(currentTimeStamp)

		
		# Will write till latest timestamp at that point when script first ran.
		# So later on run this script again to get the latest data till current time
		print "\nWriting to file: ttcTimeStamp.txt the timeStamp: {} from which need to update again later on...\n".format(currentTimeStamp)
		with open('ttcTimeStamp.txt', 'w') as f:
			f.write(str(currentTimeStamp))
		break