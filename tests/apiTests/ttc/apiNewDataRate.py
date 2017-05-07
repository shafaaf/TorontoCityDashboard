#############################################################
# Testing /ttc api's new data coming in rate
#############################################################

import requests
import json
import time

print "Will skip this one."
r = requests.get("http://portal.cvst.ca/api/0.1/ttc")
testJsonToPython = r.content
jsonToPython = json.loads(testJsonToPython)
print "Got an entry: {}".format(jsonToPython[0])
print "Entry's GPStime: {}".format(jsonToPython[0]["GPStime"])
print "Entry's timestamp: {}".format(jsonToPython[0]["timestamp"])
print "Entry's vehicle_id: {}\n".format(jsonToPython[0]["vehicle_id"])


#Find new fresh data to compare with
while(True):
	r1 = requests.get("http://portal.cvst.ca/api/0.1/ttc")
	testJsonToPython1 = r1.content
	if testJsonToPython1 != testJsonToPython:
		jsonToPython1 = json.loads(testJsonToPython1)
		print "\nFOUND first one to compare with:"
		print "First entry's GPStime: {}".format(jsonToPython1[0]["GPStime"])
		print "First entry's timestamp: {}".format(jsonToPython1[0]["timestamp"])
		print "First entry's vehicle_id: {}\n".format(jsonToPython1[0]["vehicle_id"])
		break
	else:
		print "Same content so keep checking"			

#Find the next new data and calculate time
startTime = time.time()
while (True):
	r2 = requests.get("http://portal.cvst.ca/api/0.1/ttc")
	testJsonToPython2 = r2.content
	if testJsonToPython2 != testJsonToPython1:
		jsonToPython2 = json.loads(testJsonToPython2)
		print "\nFOUND second one:"
		print "Second entry's GPStime: {}".format(jsonToPython2[0]["GPStime"])
		print "Second entry's timestamp: {}".format(jsonToPython2[0]["timestamp"])
		print "Second entry's vehicle_id: {}".format(jsonToPython2[0]["vehicle_id"])
		break
	else:
		print "Same content so keep checking"		

endTime = time.time()
duration = endTime - startTime
print "\nResult: Total time taken was {}".format(duration)

#Results: Around a minute
