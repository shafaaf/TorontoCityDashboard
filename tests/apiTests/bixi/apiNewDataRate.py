#############################################################
# Testing /bixi api's new data coming rate
#############################################################

import requests
import json
import time

print "Testing rate of new data coming in for /bixi:"
print "Will skip this one."
r = requests.get("http://portal.cvst.ca/api/0.1/bixi")
testJsonToPython = r.content
jsonToPython = json.loads(testJsonToPython)
print "Got an entry: {}".format(jsonToPython[0])
print "Entry's bikes: {}".format(jsonToPython[0]["bikes"])
print "Entry's id: {}".format(jsonToPython[0]["id"])
print "Entry's timestamp: {}\n".format(jsonToPython[0]["timestamp"])

#Find new fresh data to compare with
while(True):
	r1 = requests.get("http://portal.cvst.ca/api/0.1/bixi")
	testJsonToPython1 = r1.content
	if testJsonToPython1 != testJsonToPython:
		jsonToPython1 = json.loads(testJsonToPython1)
		print "\nFOUND first one to compare with:"
		print "First entry's bikes: {}".format(jsonToPython1[0]["bikes"])
		print "First entry's id: {}".format(jsonToPython1[0]["id"])
		print "First entry's timestamp: {}\n".format(jsonToPython1[0]["timestamp"])
		break
	else:
		print "Same content so keep checking"			

#Find the next new data and calculate time
startTime = time.time()
while (True):
	r2 = requests.get("http://portal.cvst.ca/api/0.1/bixi")
	testJsonToPython2 = r2.content
	if testJsonToPython2 != testJsonToPython1:
		jsonToPython2 = json.loads(testJsonToPython2)
		print "\nFOUND second one:"
		print "Second entry's bikes: {}".format(jsonToPython2[0]["bikes"])
		print "Second entry's id: {}".format(jsonToPython2[0]["id"])
		print "Second entry's timestamp: {}".format(jsonToPython2[0]["timestamp"])
		break
	else:
		print "Same content so keep checking"		

endTime = time.time()
duration = endTime - startTime
print "\nResult: Total time taken was {}".format(duration)

#Results: Around 299 seconds, or 5 minutes
