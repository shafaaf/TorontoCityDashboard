/* 
*** Make ttc heatmap, 
*** Submit past datetimes to get ttc heatmap data
*** Update ttc to real time
*/

// To hold ttc data of current snapshot
var ttcData = []; //raw data of snapshot looking at right now. Maybe past or current data
var numberOfRoutes;

// Display ttc data on heatmap on startup. 
console.log("ttc scripts loaded!");
var ttcMap, ttcHeatmap;

// Vehicle locations for heatmap
var ttcVehicleLocations = [];

// -----------------------------------------------------------------------------------------------------------------

// Make initial TTC heatmap on startup
function initTTCHeatMap() 
{
  ttcMap = new google.maps.Map(document.getElementById('ttcMap'), {
    zoom: 11,
    center: {lat: 43.744385, lng: -79.406937},// center: {lat: 37.775, lng: -122.434},
    mapTypeId: 'satellite'
  });

  //Setup ttc heatmap. Shows ttc vehicles as each indivitual point
  ttcHeatmap = new google.maps.visualization.HeatmapLayer({
    data: ttcVehicleLocations,
    map: ttcMap
  });


  // Settings for each zoom level
  ttcMap.addListener('zoom_changed', function() 
  {
    var zoomLevel = ttcMap.getZoom();
    console.log("ttc radius is: ", ttcHeatmap.get('radius'));
    if(zoomLevel == 10)
    {
      console.log("Change concentration settings. Zoom level is: ", ttcMap.getZoom());
      ttcHeatmap.setOptions({
        dissipating: true,
        maxIntensity: 7,
        radius: 6,
        opacity: 0.7
        //dissipating: false
      });
    }

    else if(zoomLevel == 9)
    {
      console.log("Change concentration settings. Zoom level is: ", ttcMap.getZoom());
      ttcHeatmap.setOptions({
        dissipating: true,
        maxIntensity: 7,
        radius: 4,
        opacity: 0.7
        //dissipating: false
      });
    }
    else if(zoomLevel == 8)
    {
      console.log("Change concentration settings. Zoom level is: ", ttcMap.getZoom());
      ttcHeatmap.setOptions({
        dissipating: true,
        maxIntensity: 8,
        radius: 2,
        opacity: 0.9
        //dissipating: false
      });
    }

    else if(zoomLevel == 7)
    {
      console.log("Change settings. Zoom level is: ", ttcMap.getZoom());
      ttcHeatmap.setOptions({
        dissipating: true,
        maxIntensity: 10,
        radius: 1,
        opacity: 0.9
        //dissipating: false
      });
    }
    else if(zoomLevel < 7)
    {
      console.log("Change concentration settings. Zoom level is: ", ttcMap.getZoom());
      ttcHeatmap.setOptions({
        dissipating: true,
        maxIntensity: 10,
        radius: 0.5
        //dissipating: false
      });
    }
    else//This is default view. Todo: Find the best one here
    {
      console.log("Change settings. Zoom level is: ", ttcMap.getZoom());
      ttcHeatmap.setOptions({
        dissipating: true,
        maxIntensity: 4,
        radius: null,
        opacity: null
        //dissipating: false
      });
    }
  });
}

//-----------------------------------------------------------------------------------------------------------------

// Turns ttcHeatmap on/off 
function toggleHeatmap() 
{
  ttcHeatmap.setMap(ttcHeatmap.getMap() ? null : ttcMap);
}


// Changes color of ttcHeatmap
function changeGradient() 
{
  var gradient = 
  [
      'rgba(0, 255, 255, 0)',
      'rgba(0, 255, 255, 1)',
      'rgba(0, 191, 255, 1)',
      'rgba(0, 127, 255, 1)',
      'rgba(0, 63, 255, 1)',
      'rgba(0, 0, 255, 1)',
      'rgba(0, 0, 223, 1)',
      'rgba(0, 0, 191, 1)',
      'rgba(0, 0, 159, 1)',
      'rgba(0, 0, 127, 1)',
      'rgba(63, 0, 91, 1)',
      'rgba(127, 0, 63, 1)',
      'rgba(191, 0, 31, 1)',
      'rgba(255, 0, 0, 1)'
  ]
  ttcHeatmap.set('gradient', ttcHeatmap.get('gradient') ? null : gradient);
}

// Changes radius of ttcHeatmap
function changeRadius() 
{
  ttcHeatmap.set('radius', ttcHeatmap.get('radius') ? null : 20);
}

// Get updated TTC data
function ttcUpdateData()
{
  console.log("In ttcUpdateData");

  //Show the modal as will load the ttcHeatmap
  $('#myPleaseWait').modal('show');

  //Remove old stats
  $("#ttcSnapshotStatsView").empty();

  //Get current ttc data to display on map
  $.ajax({
    url: "/latestTTC",
    type: "post",
    dataType: "json",
    success: function (data)
    {
      ttcData = data;
      drawUserSelectedTimeTTCDataOnMap(data);
    },
    error: function(error)
    {
      console.log("Error received back is: ", error);
    }
  }); 
}

// -----------------------------------------------------------------------------------------------------------------

// Draws latest TTC data on ttcHeatmap on startup
function drawTTCDataonMap(data)
{
  //console.log("drawTTCDataonMap recived data as: ", data);
  var numberOfVehicles = data.length;
  console.log("numberOfVehicles is: ", numberOfVehicles);

  // Formatting the data to send to ttcHeatmap
  var i;
  for(i = 0; i < numberOfVehicles; i++)
  {
    var latitude = data[i]["coordinates"][1];
    var longitude = data[i]["coordinates"][0];
    var entry = new google.maps.LatLng(latitude, longitude);
    ttcVehicleLocations.push(entry);
  }
  //console.log("ttcVehicleLocations is: ", ttcVehicleLocations);
  initTTCHeatMap();
}

// -----------------------------------------------------------------------------------------------------------------

// Draw heatmap of ttc at user specified TIME and Date
// Also called when want to update TTC data on heatmap after first viewing
function drawUserSelectedTimeTTCDataOnMap(data)
{
  //console.log("drawUserSelectedTimeTTCDataOnMap: data received is: ", data);
  var numberOfVehicles = data.length;
  //console.log("numberOfVehicles is: ", numberOfVehicles);

  // Remove old vehicles from ttcVehicleLocations
  ttcVehicleLocations.splice(0,ttcVehicleLocations.length);

  // Formatting the data to send to ttcHeatmap
  var i;
  for(i = 0; i < numberOfVehicles; i++)
  {
    var latitude = data[i]["coordinates"][1];
    var longitude = data[i]["coordinates"][0];
    var entry = new google.maps.LatLng(latitude, longitude);
    ttcVehicleLocations.push(entry);
  }

  console.log("new ttcVehicleLocations.length after push is: ", ttcVehicleLocations.length);

  //Remove old ttcHeatmap data
  ttcHeatmap.setMap(null);

  //Add in new one
  //heatmap.setdata(ttcVehicleLocations)
  //heatmap.setMap(ttcMap)

  ttcHeatmap = new google.maps.visualization.HeatmapLayer({
    data: ttcVehicleLocations,
    map: ttcMap
  });

  //Dont show the please wait modal as new ttcHeatmap generated
  $('#myPleaseWait').modal('hide');
  return;
}

// -----------------------------------------------------------------------------------------------------------------

// Submit snapshot values at user specified time, then call drawUserSelectedTimeTTCDataOnMap
function ttcSnapShotSubmit()
{
  // Remove old contents
  // ttcData.splice(0,ttcData.length);

  console.log("ttcSnapShotSubmit called.");
  ttcSnapshotDateTime = $('#ttcSnapshotDateTimeValue').val();
  console.log("ttcSnapshotDateTime is: ", ttcSnapshotDateTime);

  // Make sure user enters in a date
  if(ttcSnapshotDateTime == "")
  {
    console.log("Nothing entered in");
    alert("Need to enter in a past date in the TTC form!");
    return;
  }

  //Show the modal as will load the ttcHeatmap
  $('#myPleaseWait').modal('show');

  //Remove old TTC stats
  $("#ttcSnapshotStatsView").empty();

  //Get current ttc data to display on map
  $.ajax({
    url: "/userSelectedTimeTTCData",
    type: "post",
    dataType: "json",
    data: 
    {
      startDateTime: ttcSnapshotDateTime
    },
    success: function (data) 
    {
      //console.log("Data received back is: ", data);
      ttcData = data;
      drawUserSelectedTimeTTCDataOnMap(data);
    },
    error: function(error)
    {
      console.log("Error received back is: ", error);
    }
  });
}

// -----------------------------------------------------------------------------------------------------------------

// Initialize what needed
// Get current snapshot of ttc data
$(document).ready(function()
{
  console.log("ttcScripts document ready");

  // TTC snapshpt DateTimePickers initializer
  $('#ttcSnapshotDateTime').datetimepicker(
  {
    locale: 'en',
    stepping: 5,
    sideBySide: true,
    format: 'YYYY/MM/DD hh:mm A',
    useCurrent: false,
    minDate: '2015/01/26 10:00 AM'
  });

  //Get current ttc data to display on map
  $.ajax({
    url: "/latestTTC",
    type: "post",
    dataType: "json",
    success: function (data) 
    {
      ttcData = data;
      drawTTCDataonMap(data);
    },
    error: function(error)
    {
      console.log("Error received back is: ", error);
    }
  });
});

// -----------------------------------------------------------------------------------------------------------------

