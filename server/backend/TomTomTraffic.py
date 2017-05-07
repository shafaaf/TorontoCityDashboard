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


#------------------------------------Handlers for TomTom Traffic--------------------------------------


class TomTomTrafficQueryHandler(tornado.web.RequestHandler):

	@gen.coroutine
	def post(self):
		logger = logging.getLogger('server')

		logger.info("TomTom Query: " + self.request.remote_ip)

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

		#check body arguments
		body_args = tornado.escape.json_decode(self.request.body)
		
		sensorIncludes = None
		sensorExcludes = None
		geoPoints = None

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
		#Formatting for geo_point objects
		for co_ord in geoPoints:
			temp = {}
			temp['lat'] = co_ord['lat']
			temp['lon'] = co_ord['lng']
			formatted_geo_point.append(temp)

		print json.dumps(formatted_geo_point)	

		queryResults = yield self.queryES(startTime, endTime, sensorIncludes, sensorExcludes, formatted_geo_point, timeInterval)

		self.write(json.dumps(queryResults))
		self.finish()
	
	@gen.coroutine
	def queryES(self, startTime, endTime, includes, excludes, geoLocation, interval):

		client = Elasticsearch()

		#Individual aggregation/filter fields
		date_range = Q({"range" : {"timestamp" : {"gte": startTime, "lte" : endTime, "format" : "epoch_second"}}})

		start_point_query = Q({"geo_polygon" : {"start_location" : {"points" : geoLocation}}})
		end_point_query = Q({"geo_polygon" : {"end_location" : {"points" : geoLocation}}})

		#filter based on geo location if parameters are provided

		if(geoLocation != None):
			combined_query = Q('bool', must=[date_range], should=[start_point_query, end_point_query])
		else:
			combined_query = Q('bool', must=[date_range])

		s = Search(using=client, index="tomtom_traffic").query(combined_query)

		#Histogram aggs if interval is provided
		if(interval != None):
			interval_aggs = A({"date_histogram": {"field": "timestamp", "interval" : interval, "format" : "dd-MM-YYYY HH-mm-ss"}})\
			.metric('max_curr_speed', 'max', field='average_speed')\
			.metric('avg_curr_speed', 'avg', field='average_speed')\
			.metric('min_curr_speed', 'min', field='average_speed')\
			.metric('max_delta_speed', 'max', field='delta')\
			.metric('avg_delta_speed', 'avg', field='delta')\
			.metric('min_delta_speed', 'min', field='delta')
			s.aggs.bucket("road_traffic", interval_aggs)

			response = s.execute()

			response_dict = response.aggregations['road_traffic']['buckets']

			output_dict = []

			for sensor in response_dict:
				temp = {}
				temp['avg_curr_speed'] = sensor['avg_curr_speed']['value']
				temp['max_curr_speed'] = sensor['max_curr_speed']['value']
				temp['min_curr_speed'] = sensor['min_curr_speed']['value']
				temp['avg_delta'] = sensor['avg_delta_speed']['value']
				temp['max_delta'] = sensor['max_delta_speed']['value']
				temp['min_delta'] = sensor['min_delta_speed']['value']
				sub_strings = str(sensor['key_as_string'])
				temp['date'] = sub_strings

				if(sensor['doc_count'] > 0):
					output_dict.append(temp)
				else:
					pass
			return output_dict

		#aggregations for max/min/avg
		else:
			s.aggs.metric('max_curr_speed', 'max', field='average_speed')
			s.aggs.metric('avg_curr_speed', 'avg', field='average_speed')
			s.aggs.metric('min_curr_speed', 'min', field='average_speed')

			s.aggs.metric('max_delta_speed', 'max', field='delta')
			s.aggs.metric('avg_delta_speed', 'avg', field='delta')
			s.aggs.metric('min_delta_speed', 'min', field='delta')

			print s.to_dict()

			response = s.execute()

			return_aggs = {}
			return_aggs['max_curr_speed'] = response.aggs['max_curr_speed']['value']
			return_aggs['avg_curr_speed'] = response.aggs['avg_curr_speed']['value']
			return_aggs['min_curr_speed'] = response.aggs['min_curr_speed']['value']
			return_aggs['max_delta_speed'] = response.aggs['max_delta_speed']['value']
			return_aggs['avg_delta_speed'] = response.aggs['avg_delta_speed']['value']
			return_aggs['min_delta_speed'] = response.aggs['min_delta_speed']['value']

			return return_aggs

class TomTomTrafficHeatMapHandler(tornado.web.RequestHandler):

	@gen.coroutine
	def get(self):
		#Logger Setup
		logger = logging.getLogger('server')
		logger.info("RoadTraffic HeatMap Get: " + self.request.remote_ip)

		#Check url paramaters
		try:
			isDistricts = self.get_argument('district', None)
			isPoint = self.get_argument('point', None)
			stringStartDate = self.get_argument('startDate',None)
			stringEndDate = self.get_argument('endDate',None)
		except Exception as e:
			self.set_status(400)
			self.finish("400:Missing URL arguments")
			return

		#Check time parameters for validity
		try:
			if(stringStartDate != None):
				startTime = int(time.mktime(datetime.datetime.strptime(stringStartDate, "%Y/%m/%d %I:%M %p").timetuple()))
			else:
				startTime = None
			if(stringEndDate != None):
				endTime = int(time.mktime(datetime.datetime.strptime(stringEndDate, "%Y/%m/%d %I:%M %p").timetuple()))
			else:
				endTime = None
		except Exception as e:
			self.set_status(400)
			self.finish("Invalid start/end time arguments")
			return

		response = yield self.queryHeatMap(startTime, endTime, isDistricts, isPoint)

		self.write(json.dumps(response))
		self.finish()

	@gen.coroutine
	def queryHeatMap(self, startTime, endTime, isDistricts, isPoints):
		client = Elasticsearch()

		#Filter for start and end time for the heatmap
		date_range = Q({"range" : {"timestamp" : {"gte": startTime, "lte" : endTime, "format" : "epoch_second"}}})

		#Initial settings for the search query
		s = Search(using=client, index="tomtom_traffic").query(date_range)

		#Different buckets are required to group. Either group by the districts or as single points
		if(isDistricts):
			for i in range(0, len(district_wards)):
				#Loop through all the districts and create a bucket for each
				start_locationFilter = Q({"geo_polygon" : {"start_location": {"points" : district_wards[i]}}})
				end_locationFilter = Q({"geo_polygon" : {"end_location": {"points" : district_wards[i]}}})

				s.aggs.bucket(i, 'filter', filter=Q('bool', should=[start_locationFilter, end_locationFilter]))\
				.metric('avg_speed', 'avg', field='average_speed')\
				.metric('max_speed', 'max', field='average_speed')\
				.metric('min_speed', 'min', field='average_speed')\
				.metric('avg_delta', 'avg', field='delta')\
				.metric('max_delta', 'max', field='delta')\
				.metric('min_delta', 'min', field='delta')

			response = s.execute()

			response_dict = response.aggregations.to_dict()


			output_dict = {}

			for key in response_dict:
				temp = {}
				temp['avg_speed'] = response_dict[key]['avg_speed']['value']
				temp['max_speed'] = response_dict[key]['max_speed']['value']
				temp['min_speed'] = response_dict[key]['min_speed']['value']
				temp['avg_delta'] = response_dict[key]['avg_delta']['value']
				temp['max_delta'] = response_dict[key]['max_delta']['value']
				temp['min_delta'] = response_dict[key]['min_delta']['value']
				output_dict[key] = temp

			return output_dict

		else:
			s.aggs.bucket('eidaggs', A('terms', field='eid_geo_string', size=10000000))\
			.metric('avg_speed', 'avg', field='average_speed')\
			.metric('max_speed', 'max', field='average_speed')\
			.metric('min_speed', 'min', field='average_speed')\
			.metric('avg_delta', 'avg', field='delta')\
			.metric('max_delta', 'max', field='delta')\
			.metric('min_delta', 'min', field='delta')
			
			response = s.execute()

			response_dict = response.aggregations['eidaggs']
		
		output_dict = {}

		#Formatting the response for the heatmap
		for key in response_dict:
		 	temp = {}
		 	temp['avg_speed'] = key['avg_speed']['value']
		 	temp['max_speed'] = key['max_speed']['value']
		 	temp['min_speed'] = key['min_speed']['value']
		 	temp['avg_delta'] = key['avg_delta']['value']
		 	temp['max_delta'] = key['max_delta']['value']
		 	temp['min_delta'] = key['min_delta']['value']

		 	#Formatting for the geo coordinates
		 	sub_strings = str(key['key']).split('#')
			start_co_ordinates = sub_strings[1].split(',')
			temp['start_location'] = str(start_co_ordinates[1]) + "," + str(start_co_ordinates[0])
			end_co_ordinates=sub_strings[2].split(',')
			temp['end_location'] = str(end_co_ordinates[1]) + "," + str(end_co_ordinates[0])
			output_dict[sub_strings[0]] = temp

		return output_dict
