  /* 
  *** Show bixi snapshot stats, and draw bixiHeatmap of todo: update this
  */

var stationToBikes = {}; //Mapping of stationName to number of bikes
var idToStationName = {}; // Keep track of ids to stationName to draw bixiHeatmap of only the station clicked on

// -----------------------------------------------------------------------------------------------------------------

// Draw heatmap of bixi station selected (median or with most bikes)
function drawUserSelectedStationBixiDataOnMap(data)
{
	console.log("At drawUserSelectedStationBixiDataOnMap, data is: ", data);
	var stationClickedOn = idToStationName[data];
	console.log("stationClickedOn is: ", stationClickedOn);

	//Get number of vehicles at this station
    var vehiclesAtStation = stationToBikes[stationClickedOn];
    console.log("vehiclesAtStation is: ", vehiclesAtStation);

    // Get latitude, longitude of this station clicked on
    // Also make station entry to display on map
    var stationBikesWeightToDraw = [];
    var bixiDataLength = bixiData.length;
    for(i=0;i<bixiDataLength;i++)
    {
      if(bixiData[i]["station_name"] == stationClickedOn)
      {
        var latitude = bixiData[i]["coordinates"][1];
        var longitude = bixiData[i]["coordinates"][0];
        var bikes = bixiData[i]["bikes"];

        // Shows concentration to show number of bikes
        var entry = {location: new google.maps.LatLng(latitude, longitude), weight: bikes};
        stationBikesWeightToDraw.push(entry);
        break;
      }
    }

    console.log("stationBikesWeightToDraw is: ", stationBikesWeightToDraw);

    //Remove old heat map data and add in new data for only this station clicked on
    bixiHeatmap.setMap(null)
    bixiHeatmap = new google.maps.visualization.HeatmapLayer({
      data: stationBikesWeightToDraw,
      map: bixiMap
    });


}

// -----------------------------------------------------------------------------------------------------------------

// To calculate bixi Snapshot Statistics on browser side.
// Called when clicked on Bixi heatmap statistics button
function bixiSnapshotStats()
{
	console.log("bixiSnapshotStatistics.js: In bixiSnapshotStats");
	console.log("bixiData is: ", bixiData);

	stationToBikes = {}; // Empty it
	var totalBikes = 0;	//Keeps track of total number of bikes
	var numberOfStations = bixiData.length;	//number of stations
	console.log("numberOfStations OR bixiData.length is: ", numberOfStations);

	//Get number of bikes on each station, and total number of bikes
	var i;
	for(i=0;i<numberOfStations;i++)
	{
		var station_name = bixiData[i]["station_name"];
		var numberOfBikes = bixiData[i]["bikes"];
		stationToBikes[station_name] = numberOfBikes;

		totalBikes = totalBikes + bixiData[i]["bikes"];
	}
	console.log("stationToBikes is: ", stationToBikes);
	console.log("totalBikes is: ", totalBikes);

	// Get average bikes per station
	var averageBikes = totalBikes/numberOfStations;

	//Sort the stations by number of bikes
	var bikeStationEntries = new Array();
	for (var key in stationToBikes)
	{
		var entry = {};
		entry["stationName"] = key;
		entry["numberOfBikes"] = stationToBikes[key];
		bikeStationEntries.push(entry);
	}
	console.log("bikeStationEntries is: ", bikeStationEntries);
	var sortedBixiData = bikeStationEntries.sort(function(a,b) {
    	return a.numberOfBikes - b.numberOfBikes;
 	 });
	console.log("sortedBixiData is: ", sortedBixiData);

	//Update the DOM to show all stats till now
	$( "#bixiSnapshotStatsView" ).empty();
	$( "#bixiSnapshotStatsView" ).append( "<h3>Bixi statistics</h3>");
	$( "#bixiSnapshotStatsView" ).append( "<p>Total number of bikes: " + totalBikes + "</p>" );
	$( "#bixiSnapshotStatsView" ).append( "<p>Total number of stations tracked: " + numberOfStations + "</p>" );
	$( "#bixiSnapshotStatsView" ).append( "<p>Average bikes per station: " + averageBikes + "</p>");

	// Median calculcation
	var medianIndex = sortedBixiData.length/2;
	console.log("medianIndex is: ", medianIndex);
	medianIndex = Math.floor(medianIndex);
	console.log("medianIndex is now: ", medianIndex);

	var medianStationName = sortedBixiData[medianIndex]["stationName"];
	var medianNumberOfBikes = sortedBixiData[medianIndex]["numberOfBikes"];

 	// Keep track of this station to show on heatmap when clicked on
 	var freeId = 0;
 	var stationId = "stationId" + freeId;
 	idToStationName[stationId] = medianStationName;
 	freeId = freeId + 1;
 	$("#bixiSnapshotStatsView" ).append( '<p id = ' + stationId + '>Median station: ' + medianStationName + " with bikes: " + medianNumberOfBikes + "</p>");

	//Add in style and click event for median station
	var chosenStation = "#" + stationId;
	$(chosenStation).click(function() {
		drawUserSelectedStationBixiDataOnMap(this.id);
	});
	$(chosenStation).css("cursor", "pointer");
	$(chosenStation).css("cursor", "hand");


	//Most bikes stats
	var mostBikes = sortedBixiData[numberOfStations-1]["numberOfBikes"]; // Max number of bikes at a station
	var mostBikesStations = []; //Track the station with most bikes. Can have multiple due to them sharing same number of bikes
	mostBikesStations.push(sortedBixiData[numberOfStations-1]["stationName"]);
	console.log("mostBikesStations is: ", mostBikesStations);
	//test - remove this later
	//sortedBixiData[numberOfStations-2]["numberOfBikes"] = mostBikes;


	// Get station names with same number of bikes as the max
	var i;
	for(i = numberOfStations-2; i>=0; i--)
	{
		if(sortedBixiData[i]["numberOfBikes"] == mostBikes)
	    {
	       mostBikesStations.push(sortedBixiData[i]["stationName"]);
	    }
	    else
	    {
	      console.log("Break! Encountered at sorted index: ", i);
	      break;
	    }
	}

	console.log("mostBikes is: ", mostBikes);
  	console.log("mostBikesStations is: ", mostBikesStations);

  	var stringStationNames = ""; //used to display station names on screen
  	var mostBikesStationsLength = mostBikesStations.length;
  	for (i=0; i<mostBikesStationsLength; i++)
  	{
	    if(i!=0)  //Taking care of comma case
	    {
	      stringStationNames = stringStationNames + ", " + mostBikesStations[i];
	    }
	    else
	    {
	      stringStationNames = stringStationNames + mostBikesStations[i];
	    }
	}
	console.log("stringStationNames is: ", stringStationNames);
  	$("#bixiSnapshotStatsView").append( "<p>Most bikes at station: " + stringStationNames + " with " + mostBikes + " bikes</p>");

	// Draw bixiHeatmap of stations with most bikes
	$("#bixiSnapshotStatsView").append( "<h4>Click below to see heatmaps of stations with most bikes</h4>");
	
	// Keep track of these stations to show on heatmap when clicked on
	for(i = 0;i<mostBikesStationsLength; i++)
  	{ 
	    stationId = "stationId" + freeId;
	    idToStationName[stationId] = mostBikesStations[i];
	    freeId = freeId + 1;
	    $("#bixiSnapshotStatsView").append( '<p id = ' + stationId + '>' + mostBikesStations[i] +'</p>');

	    //Add in style and click event for chosen route
	    chosenRoute = "#" + stationId;
	    $(chosenRoute).click(function() {
			drawUserSelectedStationBixiDataOnMap(this.id);
	    });

	    $(chosenRoute).css("cursor", "pointer");
	    $(chosenRoute).css("cursor", "hand");
	}

	console.log("idToStationName is: ", idToStationName);
	
	// Go back to "Overall bixiHeatmap" button
	var myId = "overallbixiHeatmap";
	$("#bixiSnapshotStatsView").append( '<button id =' + myId + '>Click below to go back to overall heatmap</button>');
	//Add in style and click event for chosen route
	$("#overallbixiHeatmap").click(function() {
		//console.log("bixiData is: ", bixiData);
		drawUserSelectedTimeBixiDataonMap(bixiData); //in bixiHeatmap.js
	});
}
