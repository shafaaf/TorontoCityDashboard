##############################################################
# test
##############################################################

def ttcTest (startTimeStamp, endTimeStamp):
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


	print "\n\nQuerying ttcTest for ttc starting from: {} to: {}\n".format(startTimeStamp, endTimeStamp)
	
	# Filters the query based on start and end time.
	query = {
				"query" : 
			    {
			        "bool" : 
			        {
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
			    }	            
	        }  	

	# Getting results for min, max
	results = es.search(index="ttc", doc_type = startTimeStamp, body=query, size="10000")
	#print "\n\nRaw results are:\n{}".format(results)


	filteredResults = results["hits"]["hits"]
	print "\n\n\n\n\n\n\n filteredResults is: {}".format(filteredResults)
	filteredResultsLength = len(filteredResults)
	print "\n\n filteredResultsLength is: {}".format(filteredResultsLength)
	return

#-------------------------------------------------------------------------------------------------------------------------

# Example program showing how to use function above.
if __name__ == "__main__":
	startTimeStamp = 1422266401
	endTimeStamp = 	 1422266401

	print "\nRunning example program for ttc with startTimeStamp = {}, endTimeStamp = {}:\n".format(startTimeStamp, endTimeStamp)
	results = ttcTest (startTimeStamp, endTimeStamp)
