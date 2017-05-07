import collections
import json
import math
import tornado.web
import logging
import time
import datetime
import requests

from tornado import gen
from tornado.options import options

from elasticsearch import Elasticsearch
from elasticsearch_dsl import query, Q, A, Search

#	@Coordinates for the district polygons
#
from backend.Polygons.District_poly import district_wards

#------------------------------------Handlers for MTO Traffic--------------------------------------

#Handler for the HeatMap for MTO traffic
class MTOTrafficHeatMapHandler(tornado.web.RequestHandler):

	@gen.coroutine
	def get(self):
		
		#Logger Setup
		logger = logging.getLogger('server')
		logger.info("RoadTraffic HeatMap Get: " + self.request.remote_ip)

		#Check url paramaters
		try:
			isDistricts = self.get_argument('district', False)
			isPoint = self.get_argument('point', True)
			stringStartDate = self.get_argument('startDate', None)
			stringEndDate = self.get_argument('endDate', None)
		except Exception as e:
			self.set_status(400)
			self.finish("400:Missing URL arguments")
			return

		#Check if startDate and EndDate are valid and format
		try:
			if(stringStartDate != None):
				startTime = int(time.mktime(datetime.datetime.strptime(stringStartDate, "%Y/%m/%d %I:%M %p").timetuple()))
			else:
				startTime = None
				#Change to last day
			if(stringEndDate != None):
				endTime = int(time.mktime(datetime.datetime.strptime(stringEndDate, "%Y/%m/%d %I:%M %p").timetuple()))
			else:
				endTime = None
				#change to last day
		except Exception as e:
			self.set_status(400)
			self.finish("Invalid start/end time arguments")
			return

		#Query the elastic search data base and return results
		response = yield self.queryHeatMap(startTime, endTime, isDistricts, isPoint)

		self.write(json.dumps(response))
		self.set_status(200)
		self.finish()

	#Func to handle the Querys
	@gen.coroutine
	def queryHeatMap(self, startTime, endTime, isDistricts, isPoint):
		client = Elasticsearch()

		#Filter for start and end time for the heatmap
		date_range = Q({"range" : {"timestamp" : {"gte": startTime, "lte" : endTime, "format" : "epoch_second"}}})

		#Initial settings for the search query
		s = Search(using=client, index="mto_traffic").query(date_range)

		reponse_dict = {}

		#Different buckets are required if heatmap is point or region based
		if(isDistricts == 'True'):
			for i in range(0, len(district_wards)):
				#Loop through all the districts and create a bucket for each
				s.aggs.bucket(i, 'filter', filter=Q({"geo_polygon" : {"co-ordinates": {"points" : district_wards[i]}}}))\
				.metric('avg_curr_speed', 'avg', field='current_speed')\
				.metric('max_curr_speed', 'max', field='current_speed')\
				.metric('min_curr_speed', 'min', field='current_speed')\
				.metric('avg_delta', 'avg', field='delta')\
				.metric('max_delta', 'max', field='delta')\
				.metric('min_delta', 'min', field='delta')
				
			#Execute the query
			response = s.execute()
			response_dict = response.aggregations.to_dict()

			#Format the response from elasticsearch
			output_dict = {}
			for key in response_dict:
				temp = {}
				temp['avg_curr_speed'] = response_dict[key]['avg_curr_speed']['value']
				temp['max_curr_speed'] = response_dict[key]['max_curr_speed']['value']
				temp['min_curr_speed'] = response_dict[key]['min_curr_speed']['value']
				temp['avg_delta'] = response_dict[key]['avg_delta']['value']
				temp['max_delta'] = response_dict[key]['max_delta']['value']
				temp['min_delta'] = response_dict[key]['min_delta']['value']
				output_dict[key] = temp

			return output_dict
		
		elif(isPoint == 'True'):
			#Group by each sensor
			s.aggs.bucket('sensor_locations', A('terms', field='location_geo_string', size=1000000))\
			.metric('avg_curr_speed', 'avg', field='current_speed')\
			.metric('max_curr_speed', 'max', field='current_speed')\
			.metric('min_curr_speed', 'min', field='current_speed')\
			.metric('avg_delta', 'avg', field='delta')\
			.metric('max_delta', 'max', field='delta')\
			.metric('min_delta', 'min', field='delta')

			#Execute the query
			response = s.execute()
			response_dict = response.aggregations['sensor_locations']['buckets']

			#Format the output of the query
			output_dict = {}
			for sensor in response_dict:
				temp = {}
				temp['avg_curr_speed'] = sensor['avg_curr_speed']['value']
				temp['max_curr_speed'] = sensor['max_curr_speed']['value']
				temp['min_curr_speed'] = sensor['min_curr_speed']['value']
				temp['avg_delta'] = sensor['avg_delta']['value']
				temp['max_delta'] = sensor['max_delta']['value']
				temp['min_delta'] = sensor['min_delta']['value']
				
				#Grab the coordinates for point drawing 
				sub_strings = str(sensor['key']).split('#')
				co_ordinates = sub_strings[1].split(',')
				temp['co-ordinates'] = str(co_ordinates[0]) + "," + str(co_ordinates[1])
				output_dict[str(sub_strings[0])] = temp

			return output_dict

		return None
		

#Handler for general MTO Traffic Query Handlers
class MTOTrafficQueryHandler(tornado.web.RequestHandler):

	@gen.coroutine
	def post(self):

		#Logger setups
		logger = logging.getLogger('server')
		logger.info("RoadTraffic POST: " + self.request.remote_ip)

		#try catch for start and end time
		try:
			stringStartDate = self.get_argument('startDate', None)
			stringEndDate = self.get_argument('endDate', None)
			timeInterval = self.get_argument('period', None)
		except Exception as e:
			self.set_status(400)
			self.finish("<html><title>400: Missing URL Arguments</title</html>")
			return	

		#try catch for checking if start and end times are valid
		try:
			if(stringStartDate != None):
				startTime = int(time.mktime(datetime.datetime.strptime(stringStartDate, "%Y/%m/%d %I:%M %p").timetuple()))
			else:
				startTime = None
			if(stringEndDate != None):
				endTime = int(time.mktime(datetime.datetime.strptime(stringEndDate, "%Y/%m/%d %I:%M %p").timetuple()))
			else:
				endTime = None

			if startTime > endTime:
				raise ValueError('End time less than start time')
		except Exception as e:
			self.set_status(400)
			self.finish("<html><title>400: Invalid start/end time arguments</title</html>")
			return

		
		#Grab the body arguments inside post requests
		body_args = tornado.escape.json_decode(self.request.body)
		
		sensorIncludes = None
		sensorExcludes = None
		geoPoints = None

		#Try catch for the individual body arguments
		try:
			sensorIncludes = body_args['station_includes']
		except KeyError as e:
			pass

		try:
			sensorExcludes = body_args['station_excludes']
		except KeyError as e:
			pass

		try:
			geoPoints = body_args['geo_points']
		except KeyError as e:
			pass

		formatted_geo_point = []	
		#Formatting for geo_point objects into the proper format
		for co_ord in geoPoints:
			temp = {}
			temp['lat'] = co_ord['lat']
			temp['lon'] = co_ord['lng']
			formatted_geo_point.append(temp)


		#Query the elasticsearch based on the inputs
		queryResults = yield self.queryES(startTime, endTime, sensorIncludes, sensorExcludes, formatted_geo_point, timeInterval)

		self.write(json.dumps(queryResults))
		self.finish()

	@gen.coroutine
	def queryES(self, startTime, endTime, includes, excludes, geoLocations, interval):
		
		client = Elasticsearch()
		#query_string for the query

		#Individual aggregation/filter fields
		date_range = Q({"range" : {"timestamp" : {"gte": startTime, "lte" : endTime, "format" : "epoch_second"}}})

		geo_point_query = Q({"geo_polygon" : {"co-ordinates" : {"points" : geoLocations}}})

		#filter based on geo location if parameters are provided

		if(geoLocations != None):
			combined_query = Q('bool', must=[date_range, geo_point_query])
		else:
			combined_query = Q('bool', must=[date_range])

		s = Search(using=client, index="mto_traffic").query(combined_query)

		#Histogram aggs if interval is provided
		if(interval != None):
			interval_aggs = A({"date_histogram": {"field": "timestamp", "interval" : interval, "format" : "epoch_second"}})\
			.metric('max_curr_speed', 'max', field='current_speed')\
			.metric('avg_curr_speed', 'avg', field='current_speed')\
			.metric('min_curr_speed', 'min', field='current_speed')\
			.metric('max_delta_speed', 'max', field='delta')\
			.metric('avg_delta_speed', 'avg', field='delta')\
			.metric('min_delta_speed', 'min', field='delta')
			s.aggs.bucket("road_traffic", interval_aggs)

			#Execute the query
			response = s.execute()
			response_dict = response.aggregations['road_traffic']['buckets']

			output_dict = []

			#Format the query outputs
			for sensor in response_dict:
				temp = {}
				temp['avg_curr_speed'] = sensor['avg_curr_speed']['value']
				temp['max_curr_speed'] = sensor['max_curr_speed']['value']
				temp['min_curr_speed'] = sensor['min_curr_speed']['value']
				temp['avg_delta_speed'] = sensor['avg_delta_speed']['value']
				temp['max_delta_speed'] = sensor['max_delta_speed']['value']
				temp['min_delta_speed'] = sensor['min_delta_speed']['value']
				sub_strings = str(sensor['key_as_string'])
				temp['date'] = sub_strings
				#check if any field is null
				if(sensor['doc_count'] > 0):
					output_dict.append(temp)
				else:
					pass

			return output_dict

		else:
			#Normal aggregation into a single data point
			s.aggs.metric('max_curr_speed', 'max', field='current_speed')
			s.aggs.metric('avg_curr_speed', 'avg', field='current_speed')
			s.aggs.metric('min_curr_speed', 'min', field='current_speed')

			s.aggs.metric('max_delta_speed', 'max', field='delta')
			s.aggs.metric('avg_delta_speed', 'avg', field='delta')
			s.aggs.metric('min_delta_speed', 'min', field='delta')

			response = s.execute()

			#Response formatting
			return_aggs={}
			return_aggs['max_curr_speed'] = response.aggs['max_curr_speed']['value']
			return_aggs['avg_curr_speed'] = response.aggs['avg_curr_speed']['value']
			return_aggs['min_curr_speed'] = response.aggs['min_curr_speed']['value']
			return_aggs['max_delta_speed'] = response.aggs['max_delta_speed']['value']
			return_aggs['avg_delta_speed'] = response.aggs['avg_delta_speed']['value']
			return_aggs['min_delta_speed'] = response.aggs['min_delta_speed']['value']

			return return_aggs