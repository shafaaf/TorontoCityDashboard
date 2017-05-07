import requests
from requests import session
import json
import io
import sys
import time
import datetime
import re
import hashlib

from elasticsearch import Elasticsearch

host = 'localhost'
port = 9200

es = Elasticsearch([{'host:' : host, 'port': port}])

traffic_mapping = {
	"settings" : {
		"number_of_shards" : 10
	},
	"mappings" : {
		"TomTomTraffic" : {
			"_all" : {
				"enabled": "alse"
			},
			"properties" : {
				"timestamp": {
					"type" : "date",
					"format" : "epoch_second"
				},
				"free_flow": {
					"type" : "float"
				},
				"average_speed": {
					"type" : "float"
				},
				"start_location": {
					"type" : "geo_point"
				},
				"end_location": {
					"type" : "geo_point"
				},
				"elaborated_data_id": {
					"type" : "string",
					"index" : "not_analyzed"
				},
				"travel_time": {
					"type" : "float"
				},
				"delta": {
					"type" : "float"
				},
				"eid_geo_string" : {
					"type" : "string",
					"index" : "not_analyzed"
				},
				"flow" : {
					"type" : "float"
				},
				"density" : {
					"type" : "float"
				}
			}
		}
	}
}

if es.indices.exists(index="tomtom_traffic"):
	pass
#	es.indices.put_mapping(index="road_traffic", doc_type="TomTom", body=traffic_mapping)
else:
	es.indices.create(index="tomtom_traffic", body=traffic_mapping)
#es.indices.put_mapping(index="TomTomTraffic", doc_type="TomTomTraffic", body=traffic_mapping)

username = 'jhlk7272'
password = 'jhl9616'

values = {'username': username, 'password': password}
cvstLoginUrl = "http://portal.cvst.ca/login"

nonFreeFlowUrl = "http://portal.cvst.ca/api/0.1/tomtom/hdf/nonfreeflow/linkupdate"
freeFlowUrl = "http://portal.cvst.ca/api/0.1/tomtom/hdf/freeflow"

#fullTimeStampUrl = timeStampUrl + str(startTimeStamp)
#currentTimeStamp = startTimeStamp

with session() as c:

	#log into cvst
	r = c.post(cvstLoginUrl, data=values)

	#First grab all the free flow speed data
	freeFlowSpeeds = {}
	r = c.get(freeFlowUrl)
	result = r.content
	free_flow_api = json.loads(result)
	ff_api_length = len(free_flow_api)

	for i in range(0,ff_api_length):
		eID = str(free_flow_api[i]["elaboratedDataID"])
		freeFlowSpeeds[eID] = str(free_flow_api[i]["freeFlowSpeed"])

	#loop constantly for tomtom	
	while True:
		#Grab the actual data with regards to avg_speed 
		r = c.get(nonFreeFlowUrl)
		result = r.content

		apiData = json.loads(result)

		nf_api_length = len(apiData)

		for j in range(0, nf_api_length):

			myEntry = {}
			pub_timeStamp = str(apiData[j]["publicationTime"])

			dt = datetime.datetime.strptime(pub_timeStamp, '%a, %d %b %Y %H:%M:%S -0000')

			myEntry["timestamp"] = str(int((dt - datetime.datetime(1970,1,1)).total_seconds()))

			myEntry["start_location"] = apiData[j]["coordinates"][0]
			myEntry["end_location"] = apiData[j]["coordinates"][1]

			myEntry["average_speed"] = str(apiData[j]["averageSpeed"])
			
			entry_ID = str(apiData[j]["elaboratedDataID"])

			myEntry["free_flow"] = freeFlowSpeeds[entry_ID]
			myEntry["elaborated_data_id"] = entry_ID

			myEntry["travel_time"] = str(apiData[j]["travelTime"])
			myEntry["delta"] = "{0:.2f}".format(float(myEntry['average_speed'])- float(myEntry['free_flow']))
			myEntry['eid_geo_string'] = entry_ID + "#" + str(apiData[j]["coordinates"][0][0]) + "," + str(apiData[j]["coordinates"][0][1]) + "#" + str(apiData[j]["coordinates"][1][0]) + "," + str(apiData[j]["coordinates"][1][1])

			#Use a MD5 hash in order to create the ids to avoid duplication. 
			#EID of the data point

			m = hashlib.md5()
			m.update(str(pub_timeStamp).encode('utf-8'))
			m.update(str(entry_ID).encode('utf-8'))
			es_id = m.hexdigest()

			es.index(index='tomtom_traffic', doc_type="TomTomTraffic", id=es_id, body=myEntry)

		print "Inserted data for publication time:" + myEntry['timestamp']

		time.sleep(1800)
			