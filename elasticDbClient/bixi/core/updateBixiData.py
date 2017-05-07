##############################################################

# Update bixi data till latest value
# Run this after running storeAllBixiData.py
# Keeps writing to elasticSearchTimeStamp.txt file to make sure 
# ES has till which timestamp's data

##############################################################


#Function to round down
def roundDown(num, divisor):
    lower300 = num - (num%divisor)
    return (lower300 + 1)

##############################################################


# Make sure ES is up and running
import requests
res = requests.get('http://localhost:9200')
print "\nElastic search GET request:\n{}".format(res.content)


#Connect to our elastic search cluster first
host = 'localhost'
port = 9200
from elasticsearch import Elasticsearch
es = Elasticsearch([{'host': host, 'port': port}])
if not es.ping():
    raise ValueError("Connection failed")
else:
	print "Connected to elastic search..\n"




#Get current timestamp value from where need to store again
with open('bixiTimeStamp.txt', 'r') as f:
	currentTimeStamp = int(f.read())
print "\ncurrentTimeStamp from which need to store {}".format(currentTimeStamp)



#Get ending timestamp till which ES will store
import time
endTimeStamp = time.time()
endTimeStampRoundedDown = roundDown(endTimeStamp, 300)
print "\nraw endTimeStamp is: {}".format(endTimeStamp)
print "endTimeStampRoundedDown to nearest 301 is: {}".format(endTimeStampRoundedDown)



# Log in to cvst portal, and then access the 
# restricted data: /bixi?timestamp=blahbhah api
from requests import session
import json
username = 'jhlk7272'
password = 'jhl9616'
values = {'username': username,
          'password': password}

# Parameters needed to login and get api data
cvstLoginUrl = "http://portal.cvst.ca/login"
bixiTimeStampUrl = "http://portal.cvst.ca/api/0.1/bixi?timestamp="
# Make full url
fullBixiTimeStampUrl = bixiTimeStampUrl + str(currentTimeStamp)
# Number of api calls
apiCalls = 1


#Create session to send cookies
with session() as c:
	print "\n\nGoing to cvst portal to login for first time..."
	r = c.post(cvstLoginUrl, data=values)
	# print r.content
	# Todo: Need a check here to see if logged in properly or not to cvst portal.

	#Go through timstamps from start until reach the one to break on
	while True:
		print "\nCount: {} -> Now trying to access private api at: {}  ...".format(apiCalls, fullBixiTimeStampUrl)
		r = c.get(fullBixiTimeStampUrl)
		print "Response status code: {}".format(r.status_code)
		# Todo: need to check if status code is 4xx, in which case may
		# need to authenticate again.

		#Looping though array of stations for current timestamp
		apiData = json.loads(r.content)
		apiDataLength = len(apiData)
		print "\nAdding in data for timestamp {}:\n".format(currentTimeStamp)

		for i in range(0, apiDataLength):
			#Use station name is document id. IMP
			station_name = apiData[i]["station_name"]
			
			#Get api data for this timestamp and this station and store into elastic search
			myEntry = {}
			myEntry["bikes"] = apiData[i]["bikes"]			
			
			myEntry["coordinates"] = []
			myEntry["coordinates"].append(apiData[i]["coordinates"][0])
			myEntry["coordinates"].append(apiData[i]["coordinates"][1])
			
			myEntry["date_time"] = apiData[i]["date_time"]
			myEntry["empty_docks"] = apiData[i]["empty_docks"]
			myEntry["id"] = apiData[i]["id"]
			myEntry["installed"] = apiData[i]["installed"]
			myEntry["last_seen"] = apiData[i]["last_seen"]
			myEntry["last_update"] = apiData[i]["last_update"]
			myEntry["station_name"] = apiData[i]["station_name"]
			myEntry["terminalName"] = apiData[i]["terminalName"]
			myEntry["timestamp"] = apiData[i]["timestamp"]

			#Store in ES
			es.index(index='bixi', doc_type = currentTimeStamp, id = station_name, body = myEntry)
			#print "Sucessfully added in data for station_name: {}".format(station_name)
		
		#Editing parameters to get next timestamp
		currentTimeStamp = currentTimeStamp + 300
		fullBixiTimeStampUrl = bixiTimeStampUrl + str(currentTimeStamp)
		apiCalls = apiCalls + 1
		
		#Update file to reflect will what timestamp have values
		if(apiCalls%10 == 0):
			with open('bixiTimeStamp.txt', 'w') as f:
				f.write(str(currentTimeStamp))

		
		# Will write till latest timestamp at that point when script first ran.
		# Todo: Writing to file at the very end, so need to figure out proper internal, 
		#  update file after like 50 api calls for now. Also do at end
		if currentTimeStamp == endTimeStamp:
			print "\nWriting to file: elasticSearchTimeStamp.txt the timeStamp: {} from which need to update again later on...\n".format(currentTimeStamp)
			with open('bixiTimeStamp.txt', 'w') as f:
				f.write(str(currentTimeStamp))
			break

