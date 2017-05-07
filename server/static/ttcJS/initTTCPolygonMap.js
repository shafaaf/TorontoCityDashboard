/* 
*** Make initial ttc polygon
*/

console.log("initTTCPolygonMap.js loaded");

var ttcPolygonMap;  //polygon for TTC
var ttcPolygonsSelected = {};	//ttc polygon regions selected for aggregation
var freeNumber = 1;

//-----------------------------------------------------------------------------------------------------------------

// Called when a polygon region is clicked on
function showArrays(event) 
{	
	console.log("early this: ", this);
	
	if(this.highlighted == 0) //Not highlighted, so highlight the polygon
	{
		this.setMap(null);

		// Change color to show selected
		this.fillColor = '#FF0000';
		this.setMap(ttcPolygonMap);
		this.highlighted = 1;

		// Iterate to get the polygonCoords and push to ttcPolygonsSelected array
		var polygonCoords = [];	//used as value of key
		var vertices = this.getPath();
	    for (var i =0; i < vertices.getLength(); i++) 
	    {
	      var xy = vertices.getAt(i);
	      polygonCoords.push(xy.lat() + ',' + xy.lng());
	    }
	    console.log("polygonCoords is: ", polygonCoords);
		
		// Add to selected list
		var myId = this.myId;
		ttcPolygonsSelected[myId] = polygonCoords;
		console.log("ttcPolygonsSelected is: ", ttcPolygonsSelected);
	}
	else if (this.highlighted == 1) // Highlighted, so unhighlight the polygon
	{
		this.setMap(null);

		// Change color to show unselected
		this.fillColor = '#FFFFFF';
		this.setMap(ttcPolygonMap);
		this.highlighted = 0;

		//Remove the key from ttcPolygonsSelected
		delete ttcPolygonsSelected[this.myId];
		console.log("ttcPolygonsSelected is: ", ttcPolygonsSelected);
	}
	else
	{
		console.log("weird error in showArrays");
	}

	var vertices = this.getPath();
	console.log("showArrays: Clicked region has coordinates: " + event.latLng.lat() + " && " + event.latLng.lng());

	// Iterate over the vertices.
    for (var i =0; i < vertices.getLength(); i++) 
    {
      var xy = vertices.getAt(i);
      var contentString = 'Coordinate ' + i + ':' + xy.lat() + ',' + xy.lng();
      console.log(contentString);
    }

    console.log("new this: ", this);
		
}

//-----------------------------------------------------------------------------------------------------------------

function initTTCPolygonMap() 
{
	console.log("In initTTCPolygonMap function");
	ttcPolygonMap = new google.maps.Map(document.getElementById('ttcPolygonMap'), {
		zoom: 10,
		center: {lat: 43.6532, lng: -79.3832},
		mapTypeId: 'terrain'
	});

	// Draw polygons regions for ttc
	var ttcPolygonTrackers = constructPolygons(ttcPolygonMap);	//function in polygonRegions.js
	console.log("ttcPolygonTrackers is: ", ttcPolygonTrackers);

	// Add a listener for the click event for each polygon
	ttcPolygonTrackersLength = ttcPolygonTrackers.length;
	for (i = 0; i < ttcPolygonTrackersLength; i++)
	{
		ttcPolygonTrackers[i].addListener('click', showArrays);
	}
}

//-----------------------------------------------------------------------------------------------------------------
