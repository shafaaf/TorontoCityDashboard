import requests
from requests import session
import json
import io
import os
import sys
import time
import re
import hashlib

from elasticsearch import Elasticsearch
from HTMLParser import HTMLParser


class MyHTMLParser(HTMLParser):
	def __init__(self):
		self.reset()
		self.strict = False
		self.convert_charrefs = True
		self.fed = []

	def handle_data(self, data):
		self.fed.append(","+ data)
	def get_data(self):
		return ''.join(self.fed)


host = 'localhost'
port = 9200

es = Elasticsearch([{'host': host, 'port': port}])


dataType = "road_traffic"
startTimeStamp = 1483228800
endTimeStamp = 1483229700

timeInterval = 300

#log in to CVST

traffic_mapping = {
	"settings" : {
		"number_of_shards" : 10
	},
	"mappings" : {
		"MTOTraffic": {
			"_all": {"enabled": "false"},
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
					"type" : "string",
					"analyzer" : "standard" 
				},
				"delta" : {
					"type" : "float"
				},
				"location_geo_string" : {
					"type" : "string",
					"index" : "not_analyzed"
				}
			}
		}
	}
}

if es.indices.exists(index="mto_traffic"):
 	pass
else:
	es.indices.create(index='mto_traffic', ignore=400, body=traffic_mapping)



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
		 	co_ordinates = str(apiData[i]["lat"]) + "," + str(apiData[i]["longit"])
		 	myEntry['co-ordinates'] = co_ordinates
		 	parsedData = apiData[i]['description']

		 	parser = MyHTMLParser()

		 	parser.feed(parsedData)
		 	descData = parser.get_data()

		 	splitData = descData.split(",")

		 	myEntry["current_speed"] = re.findall(r'\d+\.\d+', splitData[3])[0]
		 	myEntry["free_flow"] = re.findall(r'\d+\.\d+', splitData[5])[0]

		 	direction = splitData[7]

		 	location_string = str(splitData[9]).strip() + str(direction)
		 	myEntry['location'] = location_string
		 	myEntry["delta"] = "{0:.2f}".format(float(myEntry['current_speed']) - float(myEntry['free_flow'])) 

		 	myEntry['location_geo_string'] = str(location_string) + "#" + str(co_ordinates)

		 	#generate a md5 hash for the id to avoid duplicates

		 	m = hashlib.md5()
		 	m.update(str(myEntry["timestamp"]).encode('utf-8'))
		 	m.update(str(location_string).encode('utf-8'))
		 	es_id = m.hexdigest()

		 	es.index(index='mto_traffic', doc_type = "MTOTraffic", id=es_id, body=myEntry)

		 	#print(str(myEntry))

		currentTimeStamp = currentTimeStamp + timeInterval
		fullTimeStampUrl = timeStampUrl + str(currentTimeStamp)



		if currentTimeStamp >= endTimeStamp:
			with open('MTOTrafficTimeStamp.txt', 'w') as f:
				f.write(str(currentTimeStamp))
			break

		print("Inserted data for: " + str(currentTimeStamp))