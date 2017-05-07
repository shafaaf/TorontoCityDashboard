##############################################################
# Weather Avg Max Min Aggregations
# Field is like temp, humidity etc
##############################################################

def weatherOverallAggregations (locations, field, startTimeStamp, endTimeStamp):	
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


	print "\n\nQuerying weatherOverallAggregations for weather at locations: {}, field = {}, starting from: {} to: {}\n".format(locations, field, startTimeStamp, endTimeStamp)
	
	# Filters the query. Then does metric aggregations of avg, min, max for the fields specified
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
		        	"weatherOverallMinAggregation" : 
		        	{ 
		        		"min" : 
		        		{ 
		        			"field" : field 
		        		} 
		        	},
		        	"weatherOverallMaxAggregation" : 
		        	{ 
		        		"max" : 
		        		{ 
		        			"field" : field 
		        		} 
		        	},
		        	"weatherOverallAvgAggregation" : 
		        	{ 
		        		"avg" : 
		        		{ 
		        			"field" : field 
		        		} 
		        	}		        	
	            }
	        }  	
					
	# Getting results for min, max
	results = es.search(index="weather", body=query, size="10000")
	#print "\n\nRaw results are:\n{}".format(results)
	
	filteredResults = results["aggregations"]
	#print "\n\nfilteredResults are: \n{}".format(filteredResults)

	#Extracting min, max
	overallMin = filteredResults["weatherOverallMinAggregation"]["value"]
	overallMax = filteredResults["weatherOverallMaxAggregation"]["value"]
	overallAvg = filteredResults["weatherOverallAvgAggregation"]["value"]
	
	#Putting results into dictionary
	finalResults = {}
	finalResults["min"] = overallMin
	finalResults["max"] = overallMax
	finalResults["avg"] = overallAvg

	#print "\n\nfinalResults for max, min are:\n{}".format(finalResults)
	return finalResults

#-------------------------------------------------------------------------------------------------------------------------

# Example program showing how to use function above.
if __name__ == "__main__":
	locations = ['burlington', 'mississauga']#["bradfordwestgwillimbury", "newtecumseth"] #["newtecumseth"] #["mono", "caledon"] #["markham", "toronto"]
	field = "temp_c"
	startTimeStamp = 1467633600
	endTimeStamp = 	 1467633600 #1467165600 #1467345600

	print "\nRunning example program for weather with locations = {}, field = {}, startTimeStamp = {}, endTimeStamp = {}:\n".format(locations, field, startTimeStamp, endTimeStamp)
	results = weatherOverallAggregations (locations, field, startTimeStamp, endTimeStamp)