##############################################################

# Store bixi data from unix timestamp 1422266401 for every
# 300 seconds (5 mins) interval till endTimeStamp specified below.
# Then writes to elasticSearchTimeStamp.txt file the timestamp
# from which to continue putting in.
# Run updateBixiData.py afterwards to store till current time.


# Logging in to cvst portal using credentials
# from api: /bixi/?timestamp=blahblah

# Right now storing into a bixi index with each timestamp as type
# and id as station_name. Each doc has a station's info. 

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






# Access by first logging in to cvst portal, and then access the 
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

# Use data at this timestamp as it is the earliest timestamp with data found
currentTimeStamp = 1422266401
# Store data till this timestamp
endTimeStamp = 1422267301
# Make full url
fullBixiTimeStampUrl = bixiTimeStampUrl + str(currentTimeStamp)
# Number of api calls
apiCalls = 1
# Time interval for getting data -> 300 seconds (5 mins)
timeInterval = 300


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
			#Use station name as document id. IMP
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
		currentTimeStamp = currentTimeStamp + timeInterval
		fullBixiTimeStampUrl = bixiTimeStampUrl + str(currentTimeStamp)
		apiCalls = apiCalls + 1
		
		# Right now just puttng certain timestamps, and write to file the timestamp till which need to store again
		if currentTimeStamp == endTimeStamp:
			print "\nWriting to file: bixiTimeStamp.txt the timeStamp: {} from which need to update again later on...\n".format(currentTimeStamp)
			with open('bixiTimeStamp.txt', 'w') as f:
				f.write(str(currentTimeStamp))
			break
