  /* 
  *** Show snapshot stats, and draw ttcHeatmap of median and busiest routes
  */

  var idToRoutename = {}; // Keep track of ids to routenames to draw ttcHeatmap of only the route clicked on
  
// -----------------------------------------------------------------------------------------------------------------

  // Draw heatmap of ttc ROUTE selected (median or busiest)
  function drawUserSelectedRouteTTCDataOnMap(data)
  {
    console.log("At drawUserSelectedRouteTTCDataOnMap, route is: ", data);
    var routeClickedOn = idToRoutename[data]; //actal name of route to draw ttcHeatmap of
    console.log("routeClickedOn: ", routeClickedOn);

    //Get vehicles on this route
    var ttcDataLength = ttcData.length;
    var ttcRouteVehicleLocations = [];  //keep track of vehicles on this route thats clicked on
    for(i=0;i<ttcDataLength;i++)
    {
      if(ttcData[i]["route_name"] == routeClickedOn)
      {
        var latitude = ttcData[i]["coordinates"][1];
        var longitude = ttcData[i]["coordinates"][0];
        var entry = new google.maps.LatLng(latitude, longitude);
        ttcRouteVehicleLocations.push(entry);
      }
    }
    console.log("ttcRouteVehicleLocations is: ", ttcRouteVehicleLocations);
    console.log("ttcRouteVehicleLocations.length is: ", ttcRouteVehicleLocations.length);

    //Remove old heat map data and add in new data for only this route
    ttcHeatmap.setMap(null)
    ttcHeatmap = new google.maps.visualization.HeatmapLayer({
      data: ttcRouteVehicleLocations,
      map: ttcMap
    });
  }

// -----------------------------------------------------------------------------------------------------------------

// To calculate ttc Snapshot Statistics on browser side.
// Called when clicked on TTC heatmap statistics button
function ttcSnapshotStats()
{
  console.log("ttcSnapshotStats: ttcData is: ", ttcData);
  
  var routeToVehicles = {}; // Keep track of vehicles at every route
  var i;
  var ttcDataLength = ttcData.length;
  console.log("ttcDataLength OR number of vehicles: ", ttcDataLength);

  // Keeping track how many vehicles in each route
  var routeName;
  for (i = 0; i < ttcDataLength; i++)
  { 
    routeName = ttcData[i]["route_name"];
    
    //If routeName already seen before
    if(routeName in routeToVehicles)
    {
      if(routeToVehicles.hasOwnProperty(routeName))
      {
        routeToVehicles[routeName] = routeToVehicles[routeName] + 1;
      }
    }
    else
    {
      routeToVehicles[routeName] = 1;
    }
  }
  //console.log("routeToVehicles is: ", routeToVehicles);

  // Get number of different routes tht are tracked
  numberOfRoutes = Object.keys(routeToVehicles).length;
  console.log("numberOfRoutes is: ", numberOfRoutes);

  // Get average TTC vehicles per route
  var averageTTCVehicles = ttcDataLength/numberOfRoutes;
  console.log("averageTTCVehicles is: ", averageTTCVehicles);

  // Sort the routes by number of vehicles
  var vehicleRouteEntries = new Array();
  for(var key in routeToVehicles) 
  {
    var entry = {};
    entry["routeName"] = key;
    entry["numberOfVehicles"] = routeToVehicles[key];
    vehicleRouteEntries.push(entry);
  }
  //console.log("vehicleRouteEntries is: ", vehicleRouteEntries);
  var sortedTTCData = vehicleRouteEntries.sort(function(a,b) {
    return a.numberOfVehicles - b.numberOfVehicles;
  });
  console.log("sortedTTCData is: ", sortedTTCData);


  //Update the DOM to show all stats till now
  $( "#ttcSnapshotStatsView" ).empty();
  $( "#ttcSnapshotStatsView" ).append( "<h3>TTC statistics</h3>");
  $( "#ttcSnapshotStatsView" ).append( "<p>Total number of vehicles: " + ttcDataLength + "</p>" );
  $( "#ttcSnapshotStatsView" ).append( "<p>Total number of routes tracked: " + numberOfRoutes + "</p>" );
  $( "#ttcSnapshotStatsView" ).append( "<p>Average vehicles per route: " + averageTTCVehicles + "</p>");

  // Median calculation
  var medianIndex = sortedTTCData.length/2;
  console.log("medianIndex is: ",medianIndex);
  medianIndex = Math.floor( medianIndex );
  console.log("medianIndex is now: ",medianIndex);

  var medianRouteName = sortedTTCData[medianIndex]["routeName"];
  var medianVehicles = sortedTTCData[medianIndex]["numberOfVehicles"];

  // Keep track of this route p element using an id, but use idToRoutename to track routename
  // Done because class and ids cant have spaces and route names have spaces, so use free number 
  // to route name mapping
  var freeId = 0;
  var routeId = "busyroute" + freeId;
  idToRoutename[routeId] = medianRouteName;
  freeId = freeId + 1;
  $( "#ttcSnapshotStatsView" ).append( '<p id  = ' + routeId + '>Median route: ' + medianRouteName + " with vehicles: " + medianVehicles + "</p>");
  
  //Add in style and click event for median route
  var chosenRoute = "#" + routeId;
  $(chosenRoute).click(function() {
    drawUserSelectedRouteTTCDataOnMap(this.id);
  });
  $(chosenRoute).css("cursor", "pointer");
  $(chosenRoute).css("cursor", "hand");


  //Busy route stats
  var busiestRouteVehicles = sortedTTCData[numberOfRoutes-1]["numberOfVehicles"]; //Number of vehicles at busiest route
  var busiestRouteNames = []; //Track the most busiest route name. Can have multiple due to them sharing same number of vehicles
  busiestRouteNames.push(sortedTTCData[numberOfRoutes-1]["routeName"]);
  //test - remove this later
  //sortedTTCData[numberOfRoutes-2]["numberOfVehicles"] = busiestRouteVehicles;

  // Get route names with same number of vehicles as the max
  var i;
  for (i = numberOfRoutes-2; i>=0;i--)
  {
    if(sortedTTCData[i]["numberOfVehicles"] == busiestRouteVehicles)
    {
       busiestRouteNames.push(sortedTTCData[i]["routeName"]);
    }
    else
    {
      console.log("Break! Encountered at sorted index: ", i);
      break;
    }
  }
  console.log("busiestRouteVehicles: ", busiestRouteVehicles);
  console.log("busiestRouteNames: ", busiestRouteNames);
  
  var stringRouteNames = ""; //used to display route names on screen
  var busiestRouteNamesLength = busiestRouteNames.length;
  for (i=0; i<busiestRouteNamesLength; i++)
  {
    if(i!=0)  //Taking care of comma case
    {
      stringRouteNames = stringRouteNames + ", " + busiestRouteNames[i];
    }
    else
    {
      stringRouteNames = stringRouteNames + busiestRouteNames[i];
    }

  }
  console.log("stringRouteNames is: ", stringRouteNames);
  $("#ttcSnapshotStatsView").append( "<p>Busiest route: " + stringRouteNames + " with " + busiestRouteVehicles + " vehicles</p>");
  

  // Draw ttcHeatmap of busiest chosen route
  $("#ttcSnapshotStatsView").append( "<h4>Click below to see heatmaps of busiest route</h4>");
  for(i = 0;i<busiestRouteNamesLength; i++)
  { 
    // Keep track of this route p element using an id, but use idToRoutename to track routename
    // Done because class and ids cant have spaces and route names have spaces, so use free number 
    //to route name mapping
    routeId = "busyroute" + freeId;
    idToRoutename[routeId] = busiestRouteNames[i];
    freeId = freeId + 1;

    $("#ttcSnapshotStatsView").append( '<p id = ' + routeId + '>' + busiestRouteNames[i] +'</p>');

    //Add in style and click event for chosen route
    chosenRoute = "#" + routeId;
    $(chosenRoute).click(function() {
      drawUserSelectedRouteTTCDataOnMap(this.id);
    });

    $(chosenRoute).css("cursor", "pointer");
    $(chosenRoute).css("cursor", "hand");
  }
  console.log("idToRoutename is: ", idToRoutename);

  // Go back to "Overall ttcHeatmap" button
  var  myId = "overallTTCHeatmap";
  $("#ttcSnapshotStatsView").append( '<button id =' + myId + '>Click below to go back to overall heatmap</button>');
  //Add in style and click event for chosen route
  $("#overallTTCHeatmap").click(function() {
    //console.log("ttcData is: ", ttcData);
    drawUserSelectedTimeTTCDataOnMap(ttcData); 
  });

}

// -----------------------------------------------------------------------------------------------------------------

