##############################################################
# TTC Aggregations for busiest and least busy routes
##############################################################

def ttcBusyRoutesAggregations (startTimeStamp, endTimeStamp, order):
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

	print "\n\nQuerying ttcBusyRoutesAggregations for ttc starting from: {} to: {}, with order: {}\n".format(startTimeStamp, endTimeStamp, order)
	
	# Filters the query based on start and end time. Then does metric aggregations of avg, min, max
	query = {
				"query" : 
			    {
			        "bool" : 
			        {
			        	# Filtering on start and end time
			            "filter" :
			            [
			                
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
	            	# Making each bucket a unique route (i.e here is routeName field)
		        	"RouteBuckets":
		        	{
		        		"terms": 
			            {
			                "field": "routeName.keyword",
			                "size": 2147483646,
			                "order" : { "_count" : order }
			            }
		        	}     	
	            }
	        }  	

	# Getting results for min, max
	results = es.search(index="ttc", body=query, size="10000")
	#print "\n\nRaw results are:\n{}".format(results)


	# More filtering
	buckets = results["aggregations"]["RouteBuckets"]["buckets"]
	#print "\n\nbuckets are: {}".format(buckets)
		
	# Return all results
	myLength = len(buckets)
	print "\n\nnumberofbuckets/myLength is: {}".format(myLength)

	# Inserting results into array
	resultsArray = []
	for i in range(0, myLength):
		myEntry = {}
		myEntry["routeName"] = buckets[i]["key"]
		myEntry["value"] = buckets[i]["doc_count"]
		resultsArray.append(myEntry)

	#print "\n\nresultsArray is: {}".format(resultsArray)
	return resultsArray

#-------------------------------------------------------------------------------------------------------------------------

# Example program showing how to use function above.
if __name__ == "__main__":
	startTimeStamp = 1422266401
	endTimeStamp = 	 1422266401
	order = "asc" #asc #desc

	print "\nRunning example program for ttc with startTimeStamp = {}, endTimeStamp = {}, order = {}:\n".format(startTimeStamp, endTimeStamp, order)
	results = ttcBusyRoutesAggregations (startTimeStamp, endTimeStamp, order)

