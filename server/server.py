import os.path
import tornado.ioloop
import tornado.web
import tornado.httpserver
import requests
import json
import time
import datetime

from tornado.options import define, options
from elasticsearch import Elasticsearch

from backend.MTOTraffic import MTOTrafficQueryHandler, MTOTrafficHeatMapHandler
from backend.TomTomTraffic import TomTomTrafficQueryHandler, TomTomTrafficHeatMapHandler

#------------------------------------------- Helper functions -------------------------------------------------------------

# Todo: decide on using +1 or not for start and end times

# Rounds down start time to lower side (3600 for weather)
def roundDown(num, divisor):
	lower3600 = num - (num%divisor)
	return int(lower3600)

# Rounds up end time to higher side (3600 for weather)
import math
def roundUp(x):
	result =  int(math.ceil(x / 3600.0)) * 3600
	return int(result)

#------------------------------------------ Server Application --------------------------------------------------------

# Todo: Put in configuration file
define("port", type=int, default=8080)

class Application(tornado.web.Application):
	def __init__(self):
		base_dir = os.path.dirname(__file__)
		settings = {
		  #"cookie_secret": options.cookie_secret,
		  "static_path": os.path.join(base_dir, "static"),
		  "template_path": os.path.join(base_dir, "templates"),
		  "debug": True,
		}

		print "Running Tornado server on port 8080..."

		# Full documentation of API is in README
		tornado.web.Application.__init__(self, [
			# Webpages
  			tornado.web.url(r"/", HomeHandler, name="main"),
  			tornado.web.url(r"/Forms", FormHandler, name="forms"),
  			
  			# Latest data at startup
  			tornado.web.url(r"/latestWeather", latestWeather, name="latestWeather"),
  			tornado.web.url(r"/latestTTC", latestTTC, name="latestTTC"),
  			tornado.web.url(r"/latestBixi", latestBixi, name="latestBixi"),
  			tornado.web.url(r"/latestRoads", latestRoads, name="latestRoads"),
  			
  			
  			# Specific data for snapshots
  			tornado.web.url(r"/userSelectedTimeTTCData", userSelectedTimeTTCData, name="userSelectedTimeTTCData"),
  			tornado.web.url(r"/userSelectedTimeBixiData", userSelectedTimeBixiData, name="userSelectedTimeBixiData"),
  			tornado.web.url(r"/userSelectedTimeRoadData", userSelectedTimeRoadData, name="userSelectedTimeRoadData"),
  			
  			
  			# Aggregation submit data on timeline
  			tornado.web.url(r"/weatherAggregation", weatherAggregation, name="weatherAggregation"),
  			tornado.web.url(r"/ttcAggregation", ttcAggregation, name="ttcAggregation"),
  			
  			
  			# Report generator - Todo:  Connect to Spark
  			tornado.web.url(r"/bixiReportsHandler", bixiReportsHandler, name="bixiReportsHandler"),
  			tornado.web.url(r"/weatherReportsHandler", weatherReportsHandler, name="weatherReportsHandler"),

  			# Handlers for road traffic
  			tornado.web.url(r"/MTOTraffic", MTOTrafficQueryHandler),
  			tornado.web.url(r"/MTOTraffic/HeatMap", MTOTrafficHeatMapHandler),
  			tornado.web.url(r"/TomTomTraffic", TomTomTrafficQueryHandler),
  			tornado.web.url(r"/TomTomTraffic/HeatMap", TomTomTrafficHeatMapHandler),

  		], **settings)

#-------------------------------------- Handlers for web pages -----------------------

class HomeHandler(tornado.web.RequestHandler):
	def get(self):
		self.render("main.html")

class FormHandler(tornado.web.RequestHandler):
	def get(self):
		self.render("forms.html")

#-------------------------------------- Handlers for latest data ---------------------

# To return latest weather data
class latestWeather(tornado.web.RequestHandler):
	def post(self):
		print "Request at latestWeather"
		# Get data from CVST Apis
		r = requests.get("http://portal.cvst.ca/api/0.1/weather")
		weatherData = json.loads(r.content)
		self.write(json.dumps(weatherData))

# To return latest TTC data
class latestTTC(tornado.web.RequestHandler):
	def post(self):
		print "Request at latestTTC"
		# Get data from CVST Apis
		r = requests.get("http://portal.cvst.ca/api/0.1/ttc")
		ttcData = json.loads(r.content)
		self.write(json.dumps(ttcData))

# To return latest Bixi data
class latestBixi(tornado.web.RequestHandler):
	def post(self):
		print "Request at latestBixi"
		# Get data from CVST Apis
		r = requests.get("http://portal.cvst.ca/api/0.1/bixi")
		bixiData = json.loads(r.content)
		self.write(json.dumps(bixiData))

# To return latest Roads data for road incidents, twitter reports
class latestRoads(tornado.web.RequestHandler):
	def post(self):
		print "Request at latestRoads"
		# Get data from CVST Apis
		returnResults = {}
		# Road incidents
		r = requests.get("http://portal.cvst.ca/realtime/ROAD_INC")
		roadIncidentsData = json.loads(r.content)
		returnResults["roadIncidents"] = roadIncidentsData
		# Twitter Reports
		r = requests.get("http://portal.cvst.ca/realtime/TWITTER_INC")
		twitterData = json.loads(r.content)
		returnResults["twitter"] = twitterData		

		self.write(json.dumps(returnResults))

#------------------------------------- Handlers for specific data for snapshots ----------

# To return user specified time TTC data
class userSelectedTimeTTCData(tornado.web.RequestHandler):
	def post(self):
		print "Request at userSelectedTimeTTCData"
		
		# Formatting
		startDateTime = self.get_argument('startDateTime', True)
		print "startDateTime is: {}".format(startDateTime)

		startDateTime = time.mktime(datetime.datetime.strptime(startDateTime, "%Y/%m/%d %I:%M %p").timetuple())

		startDateTime = int(startDateTime)
		startDateTime = startDateTime + 1

		if startDateTime < 	1422266401:
			startDateTime = 1422266401
			print "startDate is too early and so set to min: {}".format(startDateTime)

		print "\nConverted start time is: {}".format(startDateTime)

		# http://portal.cvst.ca/api/0.1/ttc?timestamp=1422266401
		ttcTimeStampApiUrl = "http://portal.cvst.ca/api/0.1/ttc?timestamp=" + str(startDateTime)

		# Get data from CVST Apis
		from requests import session
		import json
		cvstLoginUrl = "http://portal.cvst.ca/login"
		username = 'Shafaaf'
		password = 'ldrt4thb'
		values = {
					'username': username,
		          	'password': password
		          }
		with session() as c:
			r = c.post(cvstLoginUrl, data=values)
			print "\n\nNow trying to access private api at: {}  ...".format(ttcTimeStampApiUrl)
			r = c.get(ttcTimeStampApiUrl)
			ttcData = json.loads(r.content)
			self.write(json.dumps(ttcData))

#----------------------------------------------------

# To return user specified time Bixi data
class userSelectedTimeBixiData(tornado.web.RequestHandler):
	def post(self):
		print "Request at userSelectedTimeBixiData"
		
		# Formatting
		startDateTime = self.get_argument('startDateTime', True)
		print "startDateTime is: {}".format(startDateTime)

		startDateTime = time.mktime(datetime.datetime.strptime(startDateTime, "%Y/%m/%d %I:%M %p").timetuple())

		startDateTime = int(startDateTime)
		startDateTime = startDateTime + 1

		if startDateTime < 	1422266401:
			startDateTime = 1422266401
			print "startDate is too early and so set to min: {}".format(startDateTime)

		print "\nConverted start time is: {}".format(startDateTime)

		# http://portal.cvst.ca/api/0.1/bixi?timestamp=1422266401
		bixiTimeStampApiUrl = "http://portal.cvst.ca/api/0.1/bixi?timestamp=" + str(startDateTime)

		# Get data from CVST Apis
		from requests import session
		import json
		cvstLoginUrl = "http://portal.cvst.ca/login"
		username = 'Shafaaf'
		password = 'ldrt4thb'
		values = {
					'username': username,
		          	'password': password
		          }
		with session() as c:
			r = c.post(cvstLoginUrl, data=values)
			print "\n\nNow trying to access private api at: {}  ...".format(bixiTimeStampApiUrl)
			r = c.get(bixiTimeStampApiUrl)
			bixiData = json.loads(r.content)
			self.write(json.dumps(bixiData))

#----------------------------------------------------

# To return user specified time road data
class userSelectedTimeRoadData(tornado.web.RequestHandler):
	def post(self):
		print "Request at userSelectedTimeRoadData"
		
		# Formatting
		startDateTime = self.get_argument('startDateTime', True)
		print "startDateTime is: {}".format(startDateTime)

		startDateTime = time.mktime(datetime.datetime.strptime(startDateTime, "%Y/%m/%d %I:%M %p").timetuple())

		startDateTime = int(startDateTime)
		startDateTime = startDateTime + 1

		if startDateTime < 	1422266401:
			startDateTime = 1422266401
			print "startDate is too early and so set to min: {}".format(startDateTime)

		print "\nConverted start time is: {}".format(startDateTime)

		# Get data from CVST Apis
		returnResults = {}
		from requests import session
		import json
		cvstLoginUrl = "http://portal.cvst.ca/login"
		username = 'Shafaaf'
		password = 'ldrt4thb'
		values = {
					'username': username,
		          	'password': password
		          }
		# Todo: Some do not give back data, so return error for thise. I think some date in 2016
		with session() as c:
			r = c.post(cvstLoginUrl, data=values)

			# Road incidents
			roadIncidentsUrl = "http://portal.cvst.ca/history/ROAD_INC/" + str(startDateTime)
			print "Accessing api at: {}".format(roadIncidentsUrl)
			r = c.get(roadIncidentsUrl)
			#print "r.content is: {}".format(r.content)
			roadIncidentsData = json.loads(r.content)
			returnResults["roadIncidents"] = roadIncidentsData
			
			# Twitter Reports
			twitterReportsUrl = "http://portal.cvst.ca/history/TWITTER_INC/" + str(startDateTime)
			print "accessing api at: {}".format(twitterReportsUrl)
			r = c.get(twitterReportsUrl)
			twitterData = json.loads(r.content)
			returnResults["twitter"] = twitterData		

			self.write(json.dumps(returnResults))


#------------------------------------- Handlers for aggregation data -------

# All types of weather aggregtions routed here
class weatherAggregation(tornado.web.RequestHandler):
	def post(self):
		print "Request at weatherAggregation"
		
		#Extract arguments sent form client	
		chosenLocations = self.request.arguments["chosenLocations"][0]
		aggType = self.get_argument('aggType', True) #aggType includes avg, min, max
		field = self.get_argument('field', True) #field includes temp, humidity, windmph
		stringStartDateTime = self.get_argument('stringStartDateTime', True)
		stringDateEndTime = self.get_argument('stringDateEndTime', True)
		category = self.request.arguments["category"][0]	#category decides if avg, max, min over region in graph or single value

		#Convert times to unix times
		startTime =  time.mktime(datetime.datetime.strptime(stringStartDateTime, "%Y/%m/%d %I:%M %p").timetuple())
		endTime =  time.mktime(datetime.datetime.strptime(stringDateEndTime, "%Y/%m/%d %I:%M %p").timetuple())

			
		# Verify aguments by printing
		# print "\n"
		# print "chosenLocations: {}".format(chosenLocations)
		# print "aggType: {}".format(aggType)
		# print "stringStartDateTime: {}".format(stringStartDateTime)
		# print "stringDateEndTime: {}".format(stringDateEndTime)
		# print "startTime: {}".format(startTime)
		# print "endTime: {}".format(endTime)
		# print "filtered category is: {}".format(category)
		

		# Formatted args to ES - Always print this here to test until final stage

		# Locations
		print "\n\nFinal list of formatted args to ES:"
		chosenLocations = json.loads(chosenLocations)
		locations = chosenLocations["locations"]
		locations = [str(x) for x in locations]
		locations = [x.lower() for x in locations]
		locations = [x.replace(" ", "") for x in locations]		
		print "locations is: {}".format(locations)
		
		#field and aggType
		print "field is: {}".format(field)
		print "aggType is: {}".format(aggType)

		# Round off start and end times for weather data
		startTimeRoundedDown = roundDown(startTime, 3600)
		print "startTimeRoundedDown is: {}".format(startTimeRoundedDown)
		endTimeRoundedUp = roundUp(endTime)
		print "endTimeRoundedUp is: {}".format(endTimeRoundedUp)

		#Category which decides if graph or singleValue
		category = json.loads(category)
		category = category["category"]
		print "category is: {}".format(category)

		# Get data from Elastic Search
		import sys
		sys.path.insert(0, '../elasticDbClient/weather/timelineAggregations/')

#-------------------------------------------------------------------------
		# For graphs of avg, max, min
		if category == "graph":
			print "\n\n\n==Doing for graph for {}...".format(aggType)
			from weatherGraphAggregations import weatherGraphAggregations
			results = weatherGraphAggregations(locations, field, aggType, startTimeRoundedDown, endTimeRoundedUp)		
			self.write(json.dumps(results))

#--------------------------------------------------------------------------
		
		# For top 10 snapshots or top 10 avg locations by field
		elif category == "top10":
			print "\n\n\n==Doing top10 for aggType: {}...".format(aggType)
			
			if aggType == "top10HighestSnapshots":
				sample = "top10HighestSnapshots"
				aggType = "desc"

			elif aggType == "top10LowestSnapshots":
				sample = "top10LowestSnapshots"
				aggType = "asc"

			elif aggType == "top10HighestAvgLocations":
				sample = "top10HighestAvgLocations"
				aggType = "desc"

			elif aggType == "top10LowestAvgLocations":
				sample = "top10LowestAvgLocations"
				aggType = "asc"

			else:
				print "WEIRD case in overall case"


			if	sample == "top10HighestSnapshots" or sample == "top10LowestSnapshots" :
				print "top10Snapshots query and changed aggType is: {}".format(aggType)
				from weatherTop10SnapshotAggregations import weatherTop10SnapshotAggregations
				results = weatherTop10SnapshotAggregations(locations, field, aggType, startTimeRoundedDown, endTimeRoundedUp)
				self.write(json.dumps(results))
			
			elif sample == "top10HighestAvgLocations" or sample == "top10LowestAvgLocations" :
				print "top10AvgLocations query and changed aggType is: {}".format(aggType)
				from weatherTop10AvgLocations import weatherTop10AvgLocations
				results = weatherTop10AvgLocations(locations, field, aggType, startTimeRoundedDown, endTimeRoundedUp)
				self.write(json.dumps(results))

			else:
				print "Weird case in aggTypez"
				self.write(json.dumps("weird"))

#--------------------------------------------------------------------------
		# For overall single value of avg, max, min
		elif category == "overalls":
			print "\n\n\n==Doing for overalls of avg, max, min..."
			from weatherOverallAggregations import weatherOverallAggregations
			results = weatherOverallAggregations(locations, field, startTimeRoundedDown, endTimeRoundedUp)		
			self.write(json.dumps(results))

		else:
			print "weird category. WRONG"

#----------------------------------------------------------------------------------------------------------------------

# All types of ttc aggregtions routed here
class ttcAggregation(tornado.web.RequestHandler):
	def post(self):
		print "Request at ttcAggregation"

		# Extract arguments from client side
		aggType = self.get_argument('aggType', True) #aggType includes avg, min, max
		stringStartDateTime = self.get_argument('stringStartDateTime', True)
		stringDateEndTime = self.get_argument('stringDateEndTime', True)

		#Convert times to unix times
		startTime =  time.mktime(datetime.datetime.strptime(stringStartDateTime, "%Y/%m/%d %I:%M %p").timetuple())
		endTime =  time.mktime(datetime.datetime.strptime(stringDateEndTime, "%Y/%m/%d %I:%M %p").timetuple())

		#test - Todo: Remove this 
		# startTime = startTime + 1
		# endTime = endTime + 1

		print "\n\nFinal list of formatted TTC args to ES:"
		print "aggType is: {}".format(aggType)
		print "startTime is: {}".format(startTime)
		print "endTime is: {}".format(endTime)

		# Get data from Elastic Search
		import sys
		sys.path.insert(0, '../elasticDbClient/ttc/timelineAggregations/')

		if aggType == "mostBusy":
			print "===Doing for most busy"
			order = "desc"
			from ttcBusyRoutesAggregations import ttcBusyRoutesAggregations
			results = ttcBusyRoutesAggregations(startTime, endTime, order)
		
		elif aggType == "leastBusy":
			print "===Doing for least busy"
			order = "asc"
			from ttcBusyRoutesAggregations import ttcBusyRoutesAggregations
			results = ttcBusyRoutesAggregations(startTime, endTime, order)
		else:
			print "weird aggType passed in from client side. Error"
			results = "Error"

		self.write(json.dumps(results))


#----------------------------------------------------------------------------------------------------------------------
# Form Handler only showing bixi aggregations
class bixiReportsHandler(tornado.web.RequestHandler):
	def post(self):
		print "Inside BIXI handler."
		aggType = self.get_argument('aggType', True)
		timeInterval = self.get_argument('timeInterval', True)
		locationName = self.get_argument('locationName', True)
		startDateTime = self.get_argument('startDateTime', True)
		endDateTime = self.get_argument('endDateTime', True)

		print "startDateTime is: {}".format(startDateTime)
		print "endDateTime is: {}".format(endDateTime)

		startDateTime = time.mktime(datetime.datetime.strptime(startDateTime, "%Y/%m/%d %I:%M %p").timetuple())
		print "\nConverted start time is: {}".format(startDateTime)
		endDateTime = time.mktime(datetime.datetime.strptime(endDateTime, "%Y/%m/%d %I:%M %p").timetuple())
		print "Converted end time is: {}".format(endDateTime)

		# Round off formating
		startDateTime = int(startDateTime)
		endDateTime = int(endDateTime)

		# earliest timestamp can be 1422266401 (5:01 AM EST), so if startDate is less than that, set it to min
		if startDateTime < 	1422266400:
			startDateTime = 1422266400
			print "startDate is modified to min: {}".format(startDateTime)

		# latest timestamp stored is 1422365401, so if endDate is greater, set it to max
		if endDateTime > 1422429300:
			endDateTime = 1422429300
			print "endDate is modified to max: {}".format(endDateTime)

		#Handlers
		import sys
		sys.path.insert(0, '../elasticDbClient/bixi/projectAggregations/')

		#Availability
		if aggType == "BIXI Availability":
			print "Got BIXI Availability request."
			
			# Retrieve and return results
			from bixiAvailability import bixiAvailability
			results = bixiAvailability(locationName, startDateTime, endDateTime)
			self.write(json.dumps(results))

		#Downtime
		elif aggType == "BIXI Station Downtime":
			# Importing function needed
			# Todo: Put in better place later on as more functions are needed
			print "Got BIXI downtime request."
			
			# Retrieve and return results
			from bixiDownTime import bixiDownTime
			results = bixiDownTime(locationName, startDateTime, endDateTime)
			self.write(json.dumps(results))

		#Usage
		elif aggType == "BIXI Station Usage":
			if timeInterval == "Every 5 Minutes":
				# query 5 minute interval for delta bikes
				print "Got BIXI usage request for 5 mins."
				
				# Retrieve and return results
				from bixiUsageInterval import bixiUsageInterval
				results = bixiUsageInterval(locationName, startDateTime, endDateTime)
				self.write(json.dumps(results))

			elif timeInterval == "Hourly":
				#query hourly interval for delta bikes
				print "Got BIXI usage request for 1 hourz."
				
				# Retrieve and return results
				from bixiUsageHourly import bixiUsageHourly
				results = bixiUsageHourly(locationName, startDateTime, endDateTime)
				self.write(json.dumps(results))

		else:
			print "Should not come here!"

#----------------------------------------------------------------------------------------------------------------------

#Form Handler only showing weather aggregations
class weatherReportsHandler(tornado.web.RequestHandler):
	def post(self):
		print "\nInside Weather reports handler.\n"
		
		# Extracting inputs from client
		timeInterval = self.get_argument('timeInterval', True)
		chosenLocations = self.request.arguments["locationName"][0]
		startDateTime = self.get_argument('startDateTime', True)
		endDateTime = self.get_argument('endDateTime', True)

		# Formatting the chosenLocations
		print "raw locations is: {}".format(chosenLocations)
		chosenLocations = json.loads(chosenLocations)
		locations = chosenLocations["locations"]
		locations = [str(x) for x in locations]
		locations = [x.lower() for x in locations]
		locations = [x.replace(" ", "") for x in locations]		
		print "formatted locations is: {}".format(locations)

		# Formatting start and end times
		startDateTime = time.mktime(datetime.datetime.strptime(startDateTime, "%Y/%m/%d %I:%M %p").timetuple())
		print "\nConverted start time is: {}".format(startDateTime)
		endDateTime = time.mktime(datetime.datetime.strptime(endDateTime, "%Y/%m/%d %I:%M %p").timetuple())
		print "Converted end time is: {}".format(endDateTime)

		# Round off formating
		startTimeStamp = int(startDateTime)
		endTimeStamp = int(endDateTime)

		# TO DO: modify earliest timestamp available for weather
		if startTimeStamp < 	1467165600:
			startTimeStamp = 1467165600
			print "startTimeStamp is modified to: {}".format(startTimeStamp)

		# Print Final list of formatted args
		print "\nFinal list of formatted args:"
		print "timeInterval is: {}".format(timeInterval)
		print "locations is: {}".format(locations)
		print "startTimeStamp is: {}".format(startTimeStamp)
		print "endTimeStamp is: {}".format(endTimeStamp)

		# Handler for Weather Report Generator
		import sys
		sys.path.insert(0, '../elasticDbClient/weather/reportGenerator/')
		from weatherOverInterval import weatherOverInterval
		# def weatherOverInterval (locations, interval, startTimeStamp, endTimeStamp):	
		results = weatherOverInterval(locations, timeInterval, startDateTime, endDateTime)		
		self.write(json.dumps(results))

#-------------------------------------Main-------------------------------------------------------------------

def main():
	#setup the tornado server
	tornado.options.parse_command_line()
	http_server = tornado.httpserver.HTTPServer(Application())
	http_server.listen(options.port)
	tornado.ioloop.IOLoop.current().start()

	#elasticsearch connection
	host = 'localhost'
	port = 9200

if __name__ == "__main__":
  	main()

#----------------------------------------------------------------------------------------------------------------------
