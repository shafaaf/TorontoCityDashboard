/**
*
*
*
*/

console.log("load traffic.js");

var trafficMap;

var trafficType;

var trafficInfoPolygonTrackers;
var trafficPointHeatMapLocations;
var trafficPointHeatMap;

var heatMapDataType = 'MTO';

var trafficInfoMarker;

//Initialize the maps and all the polygons. The polygons are hidden for now
function initTrafficMap()
{
	trafficMap = new google.maps.Map(document.getElementById('trafficMap'), {
		zoom: 11,
		center: {lat: 43.653908, lng: -79.384293}
	});
	console.log("Drawn Google Map for Road Traffic")

	//Initialize a hidden marker for popups
	trafficInfoMarker = new MarkerWithLabel({
		position: new google.maps.LatLng(0,0),
		draggable: false,
		raiseOnDrag: false,
		map: trafficMap,
		labelContent: "Hello World",
		labelAnchor: new google.maps.Point(30,20),
		labelClass: "labels",
		labelStyle: {opacity: 1.0},
		icon: "http://placehold.it/1x1",
		visible: false
	});

	//Draw the polygons but hide them
	trafficInfoPolygonTrackers = constructPolygons(trafficMap);

	//addTrafficInfoEventListener(trafficInfoPolygonTrackers, trafficMap, trafficInfoMarker);

	hidePolygons();


	//Initialize the point heat map array
	var emptyData = [
		new google.maps.LatLng(0,0),
		new google.maps.LatLng(0,0)
		];

	trafficPointHeatMap = new google.maps.visualization.HeatmapLayer(
	{
		data: emptyData,
		map: trafficMap
	});

	/*-----------------------------------------Zoom Level Settings---------------------------------------*/

	// Settings for each zoom level
	trafficMap.addListener('zoom_changed', function() 
	{
		var zoomLevel = trafficMap.getZoom();
		//console.log("traffic radius is: ", trafficPointHeatMap.get('radius'));
		trafficPointHeatMap.setOptions({
		  dissipating: true
		  //maxIntensity: 15
		});

		if(zoomLevel < 9)
		{
		  trafficPointHeatMap.setOptions({
		    radius: 3,
		    opacity: 0.9
		    //dissipating: false
		  });
		  console.log("Zoom level: ", trafficMap.getZoom(), "  Radius: ", trafficPointHeatMap.get('radius'));
		}
		else if(zoomLevel == 9)
		{
		  trafficPointHeatMap.setOptions({
		    radius: 5,
		    opacity: 0.7
		    //dissipating: false
		  });
		  console.log("Zoom level: ", trafficMap.getZoom(), "  Radius: ", trafficPointHeatMap.get('radius'));
		}
		else if(zoomLevel == 10)
		{
		  trafficPointHeatMap.setOptions({
		    radius: 9,
		    opacity: 0.7
		    //dissipating: false
		  });
		  console.log("Zoom level: ", trafficMap.getZoom(), "  Radius: ", trafficPointHeatMap.get('radius'));
		}
		else if(zoomLevel == 11)
		{
		  trafficPointHeatMap.setOptions({
		    radius: 13,
		    opacity: 0.9
		    //dissipating: false
		  });
		  console.log("Zoom level: ", trafficMap.getZoom(), "  Radius: ", trafficPointHeatMap.get('radius'));
		}
		else if(zoomLevel == 12)
		{
		  trafficPointHeatMap.setOptions({
		    radius: 18,
		    opacity: 0.9
		    //dissipating: false
		  });
		  console.log("Zoom level: ", trafficMap.getZoom(), "  Radius: ", trafficPointHeatMap.get('radius'));
		}
		else if(zoomLevel == 13)
		{
		  trafficPointHeatMap.setOptions({
		    radius: 22,
		    opacity: 0.7
		    //dissipating: false
		  });
		  console.log("Zoom level: ", trafficMap.getZoom(), "  Radius: ", trafficPointHeatMap.get('radius'));
		}
		else if(zoomLevel == 14)
		{
		  trafficPointHeatMap.setOptions({
		    radius: 25,
		    opacity: 0.7
		    //dissipating: false
		  });
		  console.log("Zoom level: ", trafficMap.getZoom(), "  Radius: ", trafficPointHeatMap.get('radius'));
		}
		else if(zoomLevel > 14)
		{
		  trafficPointHeatMap.setOptions({
		    radius: null,
		    opacity: null
		    //dissipating: false
		  });
		  console.log("Zoom level: ", trafficMap.getZoom(), "  Radius: ", trafficPointHeatMap.get('radius'));
		}
	});

	hidePointHeatMap();
}

//Display the data ontop of polygons. Add hover over to display the values
function getTomTomData(startTime, endTime)
{
	var pointRequestURL = "/TomTomTraffic/HeatMap?point=True";
	var districtRequestURL = "/TomTomTraffic/HeatMap?district=True";

	if(startTime != null && endTime != null){
		console.log("Valid Traffic Info Times");
		pointRequestURL = pointRequestURL + "&startDate=" + startTime + "&endDate=" + endTime;
		districtRequestURL = districtRequestURL + "&startDate=" + startTime + "&endDate=" + endTime;
	}
	//Grab the data for both the points as well as the polygons through ajax calls
	$.ajax({
			url: districtRequestURL,
			type: "get",
			dataType: "json",
			success: function (data)
			{
				console.log("TomTom Point HeatMap request successful");

				//Store the tomtom data into the trafficInfo Polygons
				for(i=0; i < trafficInfoPolygonTrackers.length; i++)
				{
					//Check if empty region
					if(data[i].avg_delta != null)
					{
						var avg_delta_value = data[i].avg_delta * -1;

						//Calculate a hexcolor based on the delta value scale from 0 to 30
						var hue = Math.floor((30 - avg_delta_value) * 120 / 30);
						var saturation = Math.abs(avg_delta_value - 15)/15;
						
						//Use a function to grab an hex code color
						//var color_hex_code = 	
						trafficInfoPolygonTrackers[i].setOptions({fillOpacity: 0.3, strokOpacity: 0.5, fillColor: hsvToHex(hue,saturation,1), strokeColor: hsvToHex(hue,saturation,1)});
					} else {
						trafficInfoPolygonTrackers[i].setOptions({fillOpacity: 0, strokOpacity:0});
						trafficInfoPolygonTrackers[i].setMap(null);
					}
				}
				
			},
			error: function(error)
			{
				console.log("Error recieve back is: ", error);
			}

		});

	$.ajax({
			url: pointRequestURL,
			type: "get",
			dataType: "json",
			success: function (data)
			{
				console.log("TomTom District HeatMap Request Successful");
				trafficPointHeatMapLocations = [];

				//Loop through all keys in data
				for (var KV in data)
				{
					if (data.hasOwnProperty(KV))
					{
						//Grab the delta value and calculate the weight
						var avg_delta_value = data[KV].avg_delta;

						var delta_weight = ((avg_delta_value*-1)/40)*5;

						//Grab the start location and push the data onto the array
						var start_lat_lng = (data[KV]['start_location']).split(",");
						var tempLocation = new google.maps.LatLng(start_lat_lng[0], start_lat_lng[1]);
						trafficPointHeatMapLocations.push(tempLocation);

						var end_lat_lng = data[KV]['end_location'].split(",");
						tempLocation = new google.maps.LatLng(end_lat_lng[0], end_lat_lng[1]);
						trafficPointHeatMapLocations.push(tempLocation);
					}
				}
				//console.log("points are: " + trafficPointHeatMapLocations);
				trafficPointHeatMap.setData(trafficPointHeatMapLocations);
			},
			error: function(error)
			{
				console.log("Error recieve back is: ", error);
			}

		});
}

function getMTOData(startTime, endTime)
{
	var pointRequestURL = "/MTOTraffic/HeatMap?point=True";
	var districtRequestURL = "/MTOTraffic/HeatMap?district=True";

	if(startTime != null && endTime != null) {
		console.log("Valid Traffic Info Times");
		pointRequestURL = pointRequestURL + "&startDate=" + startTime + "&endDate=" + endTime;
		districtRequestURL = districtRequestURL + "&startDate=" + startTime + "&endDate=" + endTime;
	}
	//Grab the data for both the points as well as the polygons through ajax calls
	$.ajax({
			url: districtRequestURL,
			type: "get",
			dataType: "json",
			success: function (data)
			{
				console.log("MTO Point HeatMap request successful");

				//Store the tomtom data into the trafficInfo Polygons
				for(i=0; i < trafficInfoPolygonTrackers.length; i++)
				{
					//Check if empty region
					if(data[i].avg_delta != null)
					{
						var avg_delta_value = data[i].avg_delta * -1;

						//Calculate a hexcolor based on the delta value scale from 0 to 30
						var hue = Math.floor((30 - avg_delta_value) * 120 / 30);
						var saturation = Math.abs(avg_delta_value - 15)/15;

						//Use a function to grab an hex code color
						//var color_hex_code = 	
						trafficInfoPolygonTrackers[i].setOptions({fillOpacity: 0.3, strokOpacity: 0.5, fillColor: hsvToHex(hue,saturation,1), strokeColor: hsvToHex(hue,saturation,1)});
					} else {
						trafficInfoPolygonTrackers[i].setOptions({fillOpacity: 0, strokOpacity:0});
						trafficInfoPolygonTrackers[i].setMap(null);
					}
				}
				
			},
			error: function(error)
			{
				console.log("Error recieve back is: ", error);
			}

		});

	$.ajax({
			url: pointRequestURL,
			type: "get",
			dataType: "json",
			success: function (data)
			{
				console.log("MTO District HeatMap request successful")
				trafficPointHeatMapLocations = [];

				//Loop through all keys in data
				for (var KV in data)
				{
					if (data.hasOwnProperty(KV))
					{
						//Grab the start location and push the data onto the array
						var point_lat_lng = data[KV]['co-ordinates'].split(",");
						//Grab the delta value and calculate a weight

						//console.log("point lat lng" + point_lat_lng[0] + ";" + point_lat_lng[1]);

						var tempLocation = new google.maps.LatLng(point_lat_lng[0], point_lat_lng[1]);
						//console.log("points: " + tempLocation);
						trafficPointHeatMapLocations.push(tempLocation);
					}
				}
				//console.log("points are:" + trafficPointHeatMapLocations);
				trafficPointHeatMap.setData(trafficPointHeatMapLocations);
			},
			error: function(error)
			{
				console.log("Error recieve back is: ", error);
			}

		});
}

//Functions to toggle data shown based on user inputs
function trafficToggleDistrict()
{
	hidePointHeatMap();
	showPolygons();
}

function trafficTogglePoints()
{
	hidePolygons();
	showPointHeatMap();
}

function hidePolygons()
{
	for (i=0; i < trafficInfoPolygonTrackers.length; i++)
	{
		trafficInfoPolygonTrackers[i].setMap(null);
	}
}

function showPolygons()
{
	for (i=0; i < trafficInfoPolygonTrackers.length; i++)
	{
		if(trafficInfoPolygonTrackers[i].fillOpacity > 0){
			trafficInfoPolygonTrackers[i].setMap(trafficMap);
		}
	}
}

function hidePointHeatMap()
{
	trafficPointHeatMap.setMap(null);
}

function showPointHeatMap()
{
	trafficPointHeatMap.setMap(trafficMap);
}

function trafficToggleMTO()
{
	heatMapDataType = "MTO";

	//Grab the start and end times
	var startTime = getStartDate();
	var endTime = getEndDate();

	getMTOData(startTime, endTime);

	trafficTogglePoints();
}

function trafficToggleTomTom()
{
	heatMapDataType = "TomTom";

	//Grab the start and end times
	var startTime = getStartDate();
	var endTime = getEndDate();

	getTomTomData(startTime, endTime);

	trafficTogglePoints();
}

//Function to update the data
function trafficUpdateData()
{

	//Grab the MTO Data
	if (heatMapDataType == "MTO")
	{
		trafficToggleMTO();

	} else if (heatMapDataType == "TomTom")
	{
		trafficToggleTomTom();
	}

	trafficTogglePoints;
}

function getStartDate()
{
	if($('#trafficInfoStartTimeValue').val() == ''){
		return null;
	}
	else{
		return $('#trafficInfoStartTimeValue').val()
	}
}

function getEndDate()
{
	if($('#trafficInfoEndTimeValue').val() == ''){
		return null;
	}
	else{
		return $('#trafficInfoEndTimeValue').val()
	}
}

//Coloring scheme for the polygons
function hsvToHex(h,s,v)
{
	var r, g, b, i, f, p, q, t;

	//First convert hsv to RGB
	i = Math.floor(h * 6);
	f = h * 6 - i;
	p = v * (1- s);
	q = v * (1- f * s);
	t = v * (1 - (1 - f) * s);

	switch(i % 6) {
		case 0: r = v, g = t, b = p; break;
        case 1: r = q, g = v, b = p; break;
        case 2: r = p, g = v, b = t; break;
        case 3: r = p, g = q, b = v; break;
        case 4: r = t, g = p, b = v; break;
        case 5: r = v, g = p, b = q; break;
	}

	r = Math.round(r * 255);
	g = Math.round(g * 255);
	b = Math.round(b * 255);

	//Then convert RGB to hex
	hex_string = "#" + ("0" + r.toString(16)).slice(-2) + ("0" + g.toString(16)).slice(-2) + ("0" + b.toString(16)).slice(-2);

	return hex_string;
}

function addTrafficInfoEventListener(polys, gMap, infoMarker)
{
	var polygonsLength = polys.length;

	//add event listener for hover over
	for(i=0; i < polygonsLength; i++)
	{
		google.maps.event.addListener(polys[i], "mousemove", function(event){
			infoMarker.setPosition(event.latLng);
			infoMarker.setVisible(true);
		});

		google.maps.event.addListener(polys[i], "mouseout", function(event) {
			infoMarker.setVisible(false);
		});
	}
}

//Initialie what is needed
//Get a simple default call to the server for traffic data
$(document).ready(function()
	{

		// Traffic DateTimePickers initializer
	    $('#trafficInfoStartTime').datetimepicker(
	    {
	      locale: 'en',
	      stepping: 5,
	      sideBySide: true,
	      format: 'YYYY/MM/DD hh:mm A',
	      useCurrent: false,
	      minDate: '2015/01/26 10:00 AM'
	    });

	    $('#trafficInfoEndTime').datetimepicker(
	    {
	      locale: 'en',
	      stepping: 5,
	      sideBySide: true,
	      format: 'YYYY/MM/DD hh:mm A',
	      useCurrent: false,
	      minDate: '2015/01/26 10:00 AM'
	    });

		console.log("traffic.js loads");

		//Initialize the traffic heat map
		initTrafficMap();

		//Ajax call to the server for the data
		trafficUpdateData();
	}
);

