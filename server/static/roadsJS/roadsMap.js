/* 
*** Make roadsMap (snapshot of road incidents, twitter)
*** Todo: Submit past datetimes to get roads map data
*** Todo: Aggregation
*** Todo: Update road data to real time
*/

console.log("loaded roadsMap.js");

// To know if made initial map or not
var initialRoadsMapMade = 0;

// Map data
var roadsMap;
var roadMarkers = []; // Markers for clustering later on
var markerCluster;

// To hold road data of current snapshot
var roadData = {}; //raw data of snapshot looking at right now. Maybe past or current data

// -----------------------------------------------------------------------------------------------------------------

//Attach popup window to marker
function bindInfoWindow(marker, map, infowindow, html) 
{
    marker.addListener('click', function() {
        infowindow.setContent(html);
        infowindow.open(map, this);
    });
}

// -----------------------------------------------------------------------------------------------------------------

// Get snapshot data about roads at user specified time,
function roadsSnapShotSubmit()
{
	console.log("roadsSnapShotSubmit called");
	roadsSnapshotDateTime = $('#roadsSnapshotDateTimeValue').val();
  	console.log("roadsSnapshotDateTime is: ", roadsSnapshotDateTime);

    // Make sure user enters in a date
	if(roadsSnapshotDateTime == "")
	{
		console.log("Nothing entered in roads form");
		alert("Need to enter in a past date in the roads form!");
		return;
	}

	//Show the modal as will load the heatmap
  	$('#myPleaseWait').modal('show');

  	// Get current road data to display on map
	$.ajax({
		url: "/userSelectedTimeRoadData",
		type: "post",
		dataType: "json",
		data: 
		{
			startDateTime: roadsSnapshotDateTime
		},
		success: function (data) 
		{
			console.log("roadsSnapShotSubmit: Data received back is: ", data);
			roadData = data;
			drawRoadsDataonMap();
		},
		error: function(error)
		{
			console.log("Error received back is: ", error);
			alert("CVST can not provide road data for that date and time. Map not updated!");
			$('#myPleaseWait').modal('hide');
		}
	});
}

// -----------------------------------------------------------------------------------------------------------------

// Draws roads data on map on startup
// Called on startup AND when user submits date, time
function drawRoadsDataonMap()
{
	if(initialRoadsMapMade == 0)
	{
		roadsMap = new google.maps.Map(document.getElementById('roadsMap'), {
		    zoom: 5,
		    center: {lat: 43.653908, lng: -79.384293}
		});
		console.log("roadData is: ", roadData);
		initialRoadsMapMade = 1;
	}
	else	//remove previous markers and marlerCluster
	{
		console.log("initialRoadsMap is already made so just make changes on it.")
		console.log("roadMarkers is: ", roadMarkers);
		console.log("markerCluster is: ", markerCluster);
		
		// Remove all old markers, and cluster
        for (var i = 0; i < roadMarkers.length; i++) 
        {
	        //roadMarkers[i].setMap(null);
	        markerCluster.removeMarker(roadMarkers[i]);
        } 
        roadMarkers = [];
        console.log("new roadMarkers is: ", roadMarkers);
        console.log("new markerCluster is: ", markerCluster);
        //return;
	}

	// Add in markers for Road Incidents
	var roadIncidentsData =  roadData["roadIncidents"]["result"];
	console.log("roadIncidentsData is: ", roadIncidentsData);
	var roadIncidentsDataLength = roadIncidentsData.length;
	var i;
	for(i=0; i<roadIncidentsDataLength;i++)
	{
		// Setting marker properties
	    var latitude = Number(roadIncidentsData[i]["lat"]);
	    var longitude = Number(roadIncidentsData[i]["longit"]);
	    var myLatlng = new google.maps.LatLng(latitude,longitude);

	    // Making the marker
	    var marker = new google.maps.Marker({
	      position: myLatlng,
	      title:"roadsMap marker!"
	    });

	    // To add the marker to the map
    	marker.setMap(roadsMap);

    	// Set content string up on marker click
    	var contentString = "<h3>Road Incident</h3>";
    	contentString = contentString + roadIncidentsData[i]["description"];

    	// Make info window
	    var infowindow = new google.maps.InfoWindow();
	    bindInfoWindow(marker, roadsMap, infowindow, contentString);

	    // Collect markers for clustering
	    roadMarkers.push(marker);
	}

	// Add in markers for Twitter Traffic Reports
	var twitterReportsData =  roadData["twitter"]["result"];
	console.log("twitterReportsData is: ", twitterReportsData);
	var twitterReportsDataLength = twitterReportsData.length;
	for(i=0; i<twitterReportsDataLength;i++)
	{
		// Setting marker properties
	    var latitude = Number(twitterReportsData[i]["lat"]);
	    var longitude = Number(twitterReportsData[i]["longit"]);
	    var myLatlng = new google.maps.LatLng(latitude,longitude);

	    // Making the marker
	    var image = 'static/roadsJS/twitter-icon.png';
	    var marker = new google.maps.Marker({
	      position: myLatlng,
	      title:"twitterReports marker!",
	      icon: image
	    });

	    // To add the marker to the map
    	marker.setMap(roadsMap);

    	// Set content string up on marker click
    	var contentString = '<h3>Report id: ' + twitterReportsData[i]["id"] + '</h3>'
    	contentString = contentString + twitterReportsData[i]["description"];

    	// Make info window
	    var infowindow = new google.maps.InfoWindow();
	    bindInfoWindow(marker, roadsMap, infowindow, contentString);

	    // Collect markers for clustering
	    roadMarkers.push(marker);
	}

	// Clusering all markers
	console.log("roadMarkers is: ", roadMarkers);
	markerCluster = new MarkerClusterer(roadsMap, roadMarkers,
            {
            	imagePath: 'https://developers.google.com/maps/documentation/javascript/examples/markerclusterer/m',
            	maxZoom: 5 // This or less, do not cluster
            });

	// Hide the modal as map has been made/updated
  	$('#myPleaseWait').modal('hide');
}	

// -----------------------------------------------------------------------------------------------------------------

// Initialize what needed
// Get current snapshot of ttc data
$(document).ready(function()
{
	console.log("roadsMap.js document ready");

	// Roads snapshpt DateTimePickers initializer
    $('#roadsSnapshotDateTime').datetimepicker(
    {
      locale: 'en',
      stepping: 5,
      sideBySide: true,
      format: 'YYYY/MM/DD hh:mm A',
      useCurrent: false,
      minDate: '2015/01/26 10:00 AM'
    });

	// Get road data to display on map
	// Get current roads data to display on map
	$.ajax({
		url: "/latestRoads",
		type: "post",
		dataType: "json",
		success: function (data) 
		{
			//console.log("latestRoads: data received back is: ", data);
			roadData = data;
			drawRoadsDataonMap();
		},
		error: function(error)
		{
			console.log("Error received back is: ", error);
		}
	});

});
