##############################################################
# weatherTop10SnapshotAggregations
# Field is like temp, humidity etc
# aggtype decides if top10highest or lowest
	# asc means lowest
	# desc means highest

# Note this gets the top 10 bucket values. So there could be 
# multiple docs in a bucket but this just returns 1, and then
# goes into next bucket
##############################################################

def weatherTop10SnapshotAggregations (locations, field, aggType, startTimeStamp, endTimeStamp):	
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


	print "\n\nQuerying weatherTop10SnapshotAggregations for weather at locations: {}, field = {}, aggType = {}, starting from: {} to: {}\n".format(locations, field, aggType, startTimeStamp, endTimeStamp)

	# Filters the query. Then does bucket terms aggregation where every bucket is a unique field e.g temp, humidity windMph value,
	#  and then does a aggType (avg, max, or min) for each bucket to get first appropriate document in the bucket
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
			                "field": field,
			                "size": 2147483646,
			                "order": 
			                {"_term": aggType}
			            },
			             "aggregations": 
			             {
			                "hits": 
			                {

			                    "top_hits": 
			                    { 
			                    	"size": 1
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

	#Ranked values
	# 1st array index to get which bucket and 2nd array index to which which doc in that bucket
	# rank1 = buckets[0]["hits"]["hits"]["hits"][0]["_source"][field]	
	# print "\n\nrank1 is: {}".format(rank1)
	# rank2 = buckets[1]["hits"]["hits"]["hits"][0]["_source"][field]
	# print "rank2 is: {}".format(rank2)
	
	#Handling case of less than 10 results
	bucketsLength = len(buckets)
	if bucketsLength < 10:
		myLength = bucketsLength
	else:
		myLength = 10

	print "myLength is: {}".format(myLength)

	resultsArray = []
	for i in range(0, myLength):
		myEntry = {}
		myEntry["location"] = buckets[i]["hits"]["hits"]["hits"][0]["_source"]["location"]
		myEntry["timestamp"] = buckets[i]["hits"]["hits"]["hits"][0]["_source"]["timestamp"]
		myEntry[field] = buckets[i]["hits"]["hits"]["hits"][0]["_source"][field]
		resultsArray.append(myEntry)

	#print "\n\nresultsArray is: {}".format(resultsArray)
	# print "\nlocation0 is: {}".format(resultsArray[0]["location"])
	# print "\nlocation1 is: {}".format(resultsArray[1]["location"])

	return resultsArray

#-------------------------------------------------------------------------------------------------------------------------

# Example program showing how to use function above.
if __name__ == "__main__":
	locations = ['aurora', 'mississauga', 'burlington', 'haltonhills']#["bradfordwestgwillimbury", "newtecumseth"] #["newtecumseth"] #["mono", "caledon"] #["markham", "toronto"]
	field = "temp_c" #temp_c, windMph, relativeHumidity
	aggType = "desc"	# asc, desc
	startTimeStamp = 1467540001
	endTimeStamp = 	 1467540001   #1467345600 #1467165600 

	print "\nRunning example program for weather with locations = {}, field = {}, aggType = {}, startTimeStamp = {}, endTimeStamp = {}:\n".format(locations, field, aggType, startTimeStamp, endTimeStamp)
	results = weatherTop10SnapshotAggregations (locations, field, aggType, startTimeStamp, endTimeStamp)
