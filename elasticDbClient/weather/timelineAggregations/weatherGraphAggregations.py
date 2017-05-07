##############################################################
# Weather Timeline graph Aggregations
# Field is like temp, humidity etc
# Aggtype is like max, min avg
##############################################################

def weatherGraphAggregations (locations, field, aggType, startTimeStamp, endTimeStamp):	
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


	print "\n\nQuerying weatherGraphAggregations for weather at locations: {}, field = {}, aggType = {}, starting from: {} to: {}\n".format(locations, field, aggType, startTimeStamp, endTimeStamp)

	# Filters the query. Then does bucket aggregation term where every bucket is a unique timestamp, and then does a aggType(avg, max, min)
	# for each bucket
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
			        "weatherTimestampBuckets": 
			        {
			            "terms": 
			            {
			                "field": "timestamp",
			                "size": 2147483646,
			                "order": {"_term": "asc"}
			            },

			            "aggs":
			            {
			                "weatherAggregationType":
			                {
			                    aggType:
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

	# IMP - Getting more results than expected since start and end TimeStamp is measure against all docs. 
	# And there are may be duplicates of timestamps even in different types for weather.

	filteredResults = results["aggregations"]["weatherTimestampBuckets"]["buckets"]
	#print "\n\n\nFiltered results are:\n{}".format(filteredResults)

	finalResults = []
	filteredResultsLength = len(filteredResults)

	# Compile buckets' avg/max/min into array
	for i in range(0, filteredResultsLength):
		myEntry = {}
		myEntry["timestamp"] = filteredResults[i]["key"]
		myEntry[field] = filteredResults[i]["weatherAggregationType"]["value"]
		finalResults.append(myEntry)


	#print "\n\n\nfinalResults are:\n{}".format(finalResults)
	#print "\nlength of finalResults: {}".format(len(finalResults))
	print "\n\nCompleted query. Returning resutlts now."
	return finalResults

#-------------------------------------------------------------------------------------------------------------------------

# Example program showing how to use function above.
if __name__ == "__main__":
	locations = ['mono', 'bradfordwestgwillimbury'] #["bradfordwestgwillimbury", "newtecumseth"] #["newtecumseth"] #["mono", "caledon"] #["markham", "toronto"]
	field = "temp_c"
	aggType = "max"	# min, max, avgs
	startTimeStamp = 1467165600
	endTimeStamp = 	 1468165600 

	print "\nRunning example program for weather with locations = {}, field = {}, aggType = {}, startTimeStamp = {}, endTimeStamp = {}:\n".format(locations, field, aggType, startTimeStamp, endTimeStamp)
	results = weatherGraphAggregations (locations, field, aggType, startTimeStamp, endTimeStamp)