#############################################################
# /bixi api extraction
#############################################################

import requests
import json

r = requests.get("http://portal.cvst.ca/api/0.1/bixi")

testJsonToPython = r.content
jsonToPython = json.loads(testJsonToPython)

#Gets raw data
#print "\njsonToPython is:  ", jsonToPython

print "\nFirst entry: {}\n".format(jsonToPython[0])
print "First entry's bikes: {}".format(jsonToPython[0]["bikes"])
print "First entry's id: {}".format(jsonToPython[0]["id"])
print "First entry's timestamp: {}".format(jsonToPython[0]["timestamp"])
print "length of array is: {}".format(len(jsonToPython))