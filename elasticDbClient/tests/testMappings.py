import requests
import json

# Make sure ES is up and running
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


myMappings = {
			    "mappings" : 
			    {
			        "1467165600" : 
			        {
			            "properties" : 
			            {
			                "locationId" : 
			                { 
			                	"type" : "text",
			                	"fielddata": "true" 
			                }
			            }
			        }
			    }
			}
es.indices.create(index='test', body = myMappings)

# 1st entry
timestamp = 1467165600
locationId = "thegta"
myEntry = {}
myEntry["locationId"] = locationId	#default- "type" : "text"
myEntry["location"] = "the GTA" #default- "type" : "text"
myEntry["timestamp"] = timestamp #default- "type" : "long"
es.index(index='test', doc_type = timestamp, id = locationId, body = myEntry)


# 2nd entry
timestamp = 999999999
locationId = "orlandoFlorida"
myEntry = {}
myEntry["locationId"] = locationId	#default- "type" : "text"
myEntry["location"] = "Orlando Florida" #default- "type" : "text"
myEntry["timestamp"] = timestamp #default- "type" : "long"
es.index(index='test', doc_type = timestamp, id = locationId, body = myEntry)
