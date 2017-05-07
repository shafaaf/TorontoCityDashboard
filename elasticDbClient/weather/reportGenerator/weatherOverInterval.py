##############################################################

# weatherOverInterval

##############################################################

def weatherOverInterval (locations, interval, startTimeStamp, endTimeStamp):	
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


	print "\n\nQuerying weatherOverInterval for weather at locations: {}, interval = {}, starting from: {} to: {}\n".format(locations, interval, startTimeStamp, endTimeStamp)

	# Filters the query. 
	# Uses Date Histogram Aggregation to make interval reports and calculate avg, min, max over each interval for temp, humidity, wind
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
			        "weatherOverTimeInterval": 
			        {
			            "date_histogram": 
			            {
			                "field": "timestampDateSearchable",
			                "format" : "yyyy-MM-dd'T'HH:mm",#"yyyy-MM-dd"
			                "interval": interval
			            },
			            "aggs":
			            {
			                "avgTempForInterval":
			                {
			                    "avg":
			                    {
			                        "field": "temp_c"
			                    }
			                },
			                "minTempForInterval":
			                {
			                    "min":
			                    {
			                        "field": "temp_c"
			                    }
			                },
			                "maxTempForInterval":
			                {
			                    "max":
			                    {
			                        "field": "temp_c"
			                    }
			                },


			                "avgWindMphForInterval":
			                {
			                    "avg":
			                    {
			                        "field": "windMph"
			                    }
			                },
			                "minWindMphForInterval":
			                {
			                    "min":
			                    {
			                        "field": "windMph"
			                    }
			                },
			                "maxWindMphForInterval":
			                {
			                    "max":
			                    {
			                        "field": "windMph"
			                    }
			                },


			                "avgRelativeHumidityForInterval":
			                {
			                    "avg":
			                    {
			                        "field": "relativeHumidity"
			                    }
			                },
			                "minRelativeHumidityForInterval":
			                {
			                    "min":
			                    {
			                        "field": "relativeHumidity"
			                    }
			                },
			                "maxRelativeHumidityForInterval":
			                {
			                    "max":
			                    {
			                        "field": "relativeHumidity"
			                    }
			                },
			            }			            
			        }
			    }	
			}	
	
	# Getting results
	results = es.search(index="weather", body=query, size="10000")
	#print "\n\n\nRaw results are:\n{}".format(results)

	filteredResults = results["aggregations"]["weatherOverTimeInterval"]["buckets"]
	#print "\n\nfilteredResults results are:\n{}".format(filteredResults)

	# Format data
	finalResults = []
	filteredResultsLength = len(filteredResults)

	for i in range(0, filteredResultsLength):
		myEntry = {}
		myEntry["date"] = filteredResults[i]["key_as_string"]

		myEntry["temp"] = {}
		myEntry["temp"]["avg"] = filteredResults[i]["avgTempForInterval"]["value"]
		myEntry["temp"]["min"] = filteredResults[i]["minTempForInterval"]["value"]
		myEntry["temp"]["max"] = filteredResults[i]["maxTempForInterval"]["value"]

		myEntry["windMph"] = {}
		myEntry["windMph"]["avg"] = filteredResults[i]["avgWindMphForInterval"]["value"]
		myEntry["windMph"]["min"] = filteredResults[i]["minWindMphForInterval"]["value"]
		myEntry["windMph"]["max"] = filteredResults[i]["maxWindMphForInterval"]["value"]

		myEntry["relativeHumidity"] = {}
		myEntry["relativeHumidity"]["avg"] = filteredResults[i]["avgRelativeHumidityForInterval"]["value"]
		myEntry["relativeHumidity"]["min"] = filteredResults[i]["minRelativeHumidityForInterval"]["value"]
		myEntry["relativeHumidity"]["max"] = filteredResults[i]["maxRelativeHumidityForInterval"]["value"]

		finalResults.append(myEntry)

	#print "\n\nfinalResults are:\n{}".format(finalResults)
	return finalResults

#-------------------------------------------------------------------------------------------------------------------------

# Example program showing how to use function above.
if __name__ == "__main__":
	locations = ['bradfordwestgwillimbury', 'newtecumseth', 'mono', 'toronto'] #["bradfordwestgwillimbury", "newtecumseth"] #["newtecumseth"] #["mono", "caledon"] #["markham", "toronto"]
	interval = "month" # year, month, week, day, hour, 5m
 
	startTimeStamp = 1467165600
	endTimeStamp = 	 1470009600 #1467165600 #1470009600

	print "\nRunning example program for weather with locations = {}, interval = {}, startTimeStamp = {}, endTimeStamp = {}:\n".format(locations, interval, startTimeStamp, endTimeStamp)
	results = weatherOverInterval (locations, interval, startTimeStamp, endTimeStamp)
