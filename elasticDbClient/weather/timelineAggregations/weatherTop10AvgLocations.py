##############################################################
# weatherTop10AvgLocations
# Field is like temp, humidity etc
# aggtype decides if top10highest or lowest
	# asc means lowest
	# desc means highest
##############################################################

def weatherTop10AvgLocations (locations, field, aggType, startTimeStamp, endTimeStamp):	
	# Make sure ES is up and running
	import requests
	res = requests.get('http://localhost:9200')
	#print "\nElastic search GET request:\n{}".format(res.content)


	#Connect to our elastic search cluster first
	host = 'localhost'
	port = 9200
	from elasticsearch import Elasticsearch
	es = Elasticsearch([{'host': host, 'port': port}])
	if not es.ping():
	    raise ValueError("Connection failed")
	else:
		print "Connected to elastic search.."


	print "\n\nQuerying weatherTop10AvgLocations for weather at locations: {}, field = {}, aggType = {}, starting from: {} to: {}\n".format(locations, field, aggType, startTimeStamp, endTimeStamp)

	# Note: Using locationId.keyword for aggregations.
	
	# Filters the query. Then does bucket terms aggregation where every bucket is a unique locationid (using dot keyword), 
	# then sorts each bucket by aggType (asc,desc in this case) and then does an avg for each bucket.
	query = {

				"query" : 
			    {
			        "bool" : 
			        {
			            "filter" :
			            [
			                {
			                    "terms" : 
			                    { 
			                        "locationId" : locations
			                    }
			                },
			                {
			                    "range" : 
			                    {
			                        "timestamp" :
			                        { 
			                            "gte" : startTimeStamp,
			                            "lte" : endTimeStamp                                
			                        }
			                    }
			                }
			            ]    
			        }
			    },

			    "aggregations":
			    {
			        "FieldBuckets": 
			        {
			            "terms": 
			            {
			                "field": "locationId.keyword",
			                "size": 2147483646,
			                "order": {"weatherAggregationType": aggType}
			            },

			            "aggs":
			            {
			                "weatherAggregationType":
			                {
			                    "avg":
			                    {
			                        "field": field
			                    }
			                }
			            }
			        }
			    }	
			}	
	
	# Getting results
	results = es.search(index="weather", body=query, size="10000")
	#print "\n\n\nRaw results are:\n{}".format(results)

	# More filtering
	buckets = results["aggregations"]["FieldBuckets"]["buckets"]
	#print "\n\nbuckets are: {}".format(buckets)


	# Handling case of less than 10 results
	bucketsLength = len(buckets)
	if bucketsLength < 10:
		myLength = bucketsLength
	else:
		myLength = 10

	#print "\n\nmyLength is: {}".format(myLength)

	resultsArray = []
	for i in range(0, myLength):
		myEntry = {}
		myEntry["location"] = buckets[i]["key"]
		myEntry[field] = buckets[i]["weatherAggregationType"]["value"]
		resultsArray.append(myEntry)

	#print "\n\nresultsArray is: {}".format(resultsArray)
	return resultsArray
#-------------------------------------------------------------------------------------------------------------------------

# Example program showing how to use function above.
if __name__ == "__main__":
	locations = ['aurora', 'mississauga', 'burlington','haltonhills']#["bradfordwestgwillimbury", "newtecumseth"] #["newtecumseth"] #["mono", "caledon"] #["markham", "toronto"]
	field = "relativeHumidity" #temp_c, windMph, relativeHumidity
	aggType = "desc"	# asc, desc
	startTimeStamp = 1467608400
	endTimeStamp = 	 1467608400   #1467345600 #1467165600 

	print "\nRunning example program for weather with locations = {}, field = {}, aggType = {}, startTimeStamp = {}, endTimeStamp = {}:\n".format(locations, field, aggType, startTimeStamp, endTimeStamp)
	results = weatherTop10AvgLocations (locations, field, aggType, startTimeStamp, endTimeStamp)
