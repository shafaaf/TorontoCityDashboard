##############################################################
# Usage of bixies
##############################################################

def bixiUsageInterval(stationName, startTimeStamp, endTimeStamp):	
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
		print "Connected to elastic search.."

	print "\n\nQuerying for usage of bixies every 5 mins at stationName: {}, starting from: {} to: {}\n".format(stationName, startTimeStamp, endTimeStamp)

	query = {
				"sort" : 
				[
			        {
			        	"time_stamp" : 
			        	{
			        		"order" : "asc"
			        	}
			        }
			    ],

				"query":
				{
					"bool": 
			        {
			            "must": 
			            {
			                "match_phrase": 
							{
								"station_name": stationName
							}  
			            },      

			            "filter":
			            [
				            {
				                "range" : 
				                {
				                    "time_stamp" : 
				                    { 
				                    	"gte" : startTimeStamp,
				                    	"lte" : endTimeStamp			                    
				                    }
				                }
				            }
			            ]
			        }	
				}		
			} 		
		
	
	# Getting results
	results = es.search(index="bixiusage", doc_type = "interval", body=query, size="10000", filter_path = ['hits.hits._source.station_name' , 'hits.hits._source.time_stamp', 'hits.hits._source.delta'])
	print "\nRaw results are:\n{}".format(results)

	filteredResults = results["hits"]["hits"]
	print "\nFiltered results are:\n{}".format(filteredResults)

	resultLength = len(filteredResults)
	print "\nNumber of results are: {}".format(resultLength)


	# Return formatted results
	results = []
	for i in filteredResults:
		results.append(i["_source"])
	
	print "\n\nFinal formatted results are:\n{}".format(results)
	print "\nNumber of results for final formatted results are: {}".format(len(results))

	return results

#-------------------------------------------------------------------------------------------------------------------------


# Example program showing how to use function above.
if __name__ == "__main__":
	stationName = "Bay St / College St"
	startTimeStamp = 1422306001
	endTimeStamp = 	1422309601

	print "\nRunning example program with stationName = {}, startTimeStamp = {}, endTimeStamp = {}:\n".format(stationName, startTimeStamp, endTimeStamp)
	results = bixiUsageInterval(stationName, startTimeStamp, endTimeStamp)

