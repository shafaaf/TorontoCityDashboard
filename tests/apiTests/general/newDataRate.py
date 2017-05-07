#############################################################
# Testing user input api's new data coming rate. 
# e.g user can pass in bixi,ttc etc and rate of new data 
# is measured
#############################################################

import requests
import json
import time

input = raw_input("Enter api url after http://portal.cvst.ca/api/0.1/ - For example: ttc to make request to http://portal.cvst.ca/api/0.1/ttc\n")
apiUrl = "http://portal.cvst.ca/api/0.1/" + input
print "Testing rate of new data coming in for {}".format(apiUrl)

print "Will skip this one."
r = requests.get(apiUrl)
testJsonToPython = r.content
jsonToPython = json.loads(testJsonToPython)
print "Got an entry: {}".format(jsonToPython[0])

#Find new fresh data to compare with
while(True):
	r1 = requests.get(apiUrl)
	testJsonToPython1 = r1.content
	if testJsonToPython1 != testJsonToPython:
		jsonToPython1 = json.loads(testJsonToPython1)
		print "\nFOUND first one to compare with:"
		print "Entry is: {}".format(jsonToPython1[0])
		break
	else:
		print "Same content so keep checking"			

#Find the next new data and calculate duration
startTime = time.time()
while (True):
	r2 = requests.get(apiUrl)
	testJsonToPython2 = r2.content
	if testJsonToPython2 != testJsonToPython1:
		jsonToPython2 = json.loads(testJsonToPython2)
		print "\nFOUND second one:"
		print "Entry is: {}".format(jsonToPython2[0])
		break
	else:
		print "Same content so keep checking"		

endTime = time.time()
duration = endTime - startTime
print "\nResult: Total time taken was {}".format(duration)

#Results: Depends on input
