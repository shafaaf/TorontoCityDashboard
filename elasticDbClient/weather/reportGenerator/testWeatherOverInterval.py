##############################################################

# testWeatherOverInterval

##############################################################

def testWeatherOverInterval (locations, startTimeStamp, endTimeStamp):	
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


	print "\n\nQuerying testWeatherOverInterval for weather at locations: {}, starting from: {} to: {}\n".format(locations, startTimeStamp, endTimeStamp)

	# Filters and returns results for specific month to test.
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
			    "aggs":
	            {
	                "weatherAvg":
	                {
	                    "avg":
	                    {
	                        "field": "relativeHumidity"
	                    }
	                },
	                "weatherMin":
	                {
	                    "min":
	                    {
	                        "field": "relativeHumidity"
	                    }
	                },
	                "weatherMax":
	                {
	                    "max":
	                    {
	                        "field": "relativeHumidity"
	                    }
	                }
	            }	
			}	
	
	# Getting results
	results = es.search(index="weather", body=query, size="10000")
	print "\n\n\nRaw results are:\n{}".format(results)

	resultLength = len(results["hits"]["hits"])
	print "\n\n\nresultLength are:\n{}".format(resultLength)

	return results

#-------------------------------------------------------------------------------------------------------------------------

# Example program showing how to use function above.
if __name__ == "__main__":
	locations = ['bradfordwestgwillimbury', 'newtecumseth', 'mono', 'caledon'] #["bradfordwestgwillimbury", "newtecumseth"] #["newtecumseth"] #["mono", "caledon"] #["markham", "toronto"]
	startTimeStamp = 1468108800
	endTimeStamp = 	 1468195199 

	print "\nRunning example program for weather with locations = {}, startTimeStamp = {}, endTimeStamp = {}:\n".format(locations, startTimeStamp, endTimeStamp)
	results = testWeatherOverInterval (locations, startTimeStamp, endTimeStamp)
