#############################################################
# /ttc api extraction
#############################################################

import requests
import json

r = requests.get("http://portal.cvst.ca/api/0.1/ttc")
#print r.status_code
#print r.headers
#print r.content

#jsonData = '{"name": "Frank", "age": 39}'
#jsonToPython = json.loads(jsonData)
#print jsonToPython

testJsonToPython = r.content
jsonToPython = json.loads(testJsonToPython)

#Gets raw data
#print "\njsonToPython is:  ", jsonToPython

print "\nFirst entry: ", jsonToPython[0]
print "\nFirst entry's GPStime: ", jsonToPython[0]["GPStime"]
print "First entry's coordinates: ", jsonToPython[0]["coordinates"]
