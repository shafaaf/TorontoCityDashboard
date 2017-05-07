import requests
from requests import session
import json
import io
import os
import sys
import time
import re

from elasticsearch import Elasticsearch
from myparser import MyHTMLParser

host = 'localhost'
port = 9200

es = Elasticsearch([{'host': host, 'port': port}])


dataType = "road_traffic"
startTimeStamp = 1486237000
endTimeStamp = 1489355000

timeInterval = 300

#log in to CVST

traffic_mapping = {
	"settings" : {
		"number_of_shards" : 3
	},
	"mappings" : {
		"traffic_flow": {
			"properties": {
				"timestamp" : {
					"type" : "date",
					"format": "yyyy-MM-dd HH:mm:ss"
				}, 
				"co-ordinates" : {
					"type" : "geo_point"
				}, 
				"current_speed" : {
					"type" : "float"
				},
				"free_flow" : {
					"type" : "float"
				},
				"location" : {
					"type" : "string"
				},
				"delta" : {
					"type" : "float"
				}
			}
		}
	}
}

if es.indices.exists(index="road_traffic"):
 	pass
else:
	es.indices.create(index='road_traffic', ignore=400, body=traffic_mapping)



username = 'jhlk7272'
password = 'jhl9616'

values = {'username': username, 'password': password}
cvstLoginUrl = "http://portal.cvst.ca/login"

timeStampUrl = "http://portal.cvst.ca/history/TRAFFIC_FLOW/"

fullTimeStampUrl = timeStampUrl + str(startTimeStamp)
currentTimeStamp = startTimeStamp

with session() as c:

	#log into cvst
	r = c.post(cvstLoginUrl, data=values)

	while True:

		r = c.get(fullTimeStampUrl)

		result = r.content

		api = json.loads(result)

		apiData = api['result']

		apiDataLength = len(apiData)

		for i in range(0, apiDataLength):

		 	myEntry = {}
		 	myEntry["timestamp"] = apiData[i]["time"]
		 	myEntry["co-ordinates"] = str(apiData[i]["lat"]) + "," + str(apiData[i]["longit"])

		 	parsedData = apiData[i]['description']

		 	parser = MyHTMLParser()

		 	parser.feed(parsedData)
		 	descData = parser.get_data()

		 	splitData = descData.split(",")

		 	myEntry["current_speed"] = re.findall(r'\d+\.\d+', splitData[3])[0]
		 	myEntry["free_flow"] = re.findall(r'\d+\.\d+', splitData[5])[0]

		 	myEntry["location"] = str(splitData[9])

		 	myEntry["delta"] = "{0:.2f}".format(float(myEntry['current_speed']) - float(myEntry['free_flow'])) 

		 	mydocType = str(apiData[i]["time"])

		 	es.index(index='road_traffic', doc_type = mydocType, body=myEntry)

		 	#print(str(myEntry))

		currentTimeStamp = currentTimeStamp + timeInterval
		fullTimeStampUrl = timeStampUrl + str(currentTimeStamp)

		if currentTimeStamp >= endTimeStamp:
			break


