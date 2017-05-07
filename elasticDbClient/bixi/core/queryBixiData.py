##############################################################
# Query bixi data from Elasticsearch
##############################################################

def queryBixiData(timeStamp, stationName):	
	# Make sure ES is up and running
	import requests
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
		print "Connected to elastic seach.."


	#Get station data at specific timestamp
	
	#timeStamp = 1422266401
	#stationName = "Jarvis St / Carleton St"
	query = {
				"query":
				{
					"match_phrase":  #match_phrase instead of match to get exact result. Match returns more results
					{
						
						"station_name": stationName				
					}		
				}		
			} 		
		

	results = es.search(index="bixi", doc_type = timeStamp, body=query)
	print "\n\nResults for stationName: {} at timeStamp: {} is:\n{}".format(stationName, timeStamp, results)
	print "\n\nFirst search result is: \n{}".format(results["hits"]["hits"][0])


#Example program showing how to use function above.
if __name__ == "__main__":
	timeStamp = 1422266401
	stationName = "Jarvis St / Carleton St"
	print "\nRunning example program with timeStamp = {}, stationName = {}:\n".format(timeStamp, stationName)
	queryBixiData(timeStamp, stationName)
