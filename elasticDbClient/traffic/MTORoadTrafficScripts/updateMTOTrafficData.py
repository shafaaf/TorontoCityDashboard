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


#################################################################
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
#################################################################

host = 'localhost'
port = 9200

es = Elasticsearch([{'host': host, 'port': port}])

timeInterval = 900
apiCalls = 1 # Number of api calls

with open('MTOTrafficTimeStamp.txt', 'r') as f:
	startTimeStamp = int(f.read())

endTimeStamp = time.time()

username = 'jhlk7272'
password = 'jhl9616'

values = {'username': username, 'password': password}
cvstLoginUrl = "http://portal.cvst.ca/login"

timeStampUrl = "http://portal.cvst.ca/history/TRAFFIC_FLOW/"

fullTimeStampUrl = timeStampUrl + str(startTimeStamp)
currentTimeStamp = startTimeStamp

headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0' }

c = requests.session()
r = c.post(cvstLoginUrl, data=values)

while True:

	while True:
		try:
			r = c.get(fullTimeStampUrl, headers=headers)
			break
		except Exception as e:
			print "Disconnect from server"
			print "sleep 30s"
			time.sleep(30)


	result = r.content

	api = json.loads(result)

	apiData = api['result']

	apiDataLength = len(apiData)

	bulk_insert_data = []

	print "\nAdding in data for timestamp {}:\n".format(currentTimeStamp)

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

	 	es.index(index='mto_traffic', doc_type = "MTOTraffic", id=es_id, body=myEntry, request_timeout=50)

	 	#print(str(myEntry))

	#es.bulk_index('mto_traffic',"MTORoadTraffic",bulk_insert_data)

	currentTimeStamp = currentTimeStamp + timeInterval
	fullTimeStampUrl = timeStampUrl + str(currentTimeStamp)
	apiCalls = apiCalls + 1

	# Update file to reflect till what timestamp have values
	with open('MTOTrafficTimeStamp.txt', 'w') as f:
		f.write(str(currentTimeStamp))


	if currentTimeStamp >= endTimeStamp:
		with open('weatherTimeStamp.txt', 'w') as f:
			f.write(str(currentTimeStamp))
		break
