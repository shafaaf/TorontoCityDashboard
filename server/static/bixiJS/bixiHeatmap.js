/* 
*** Make bixi heatmap, 
*** Submit past datetimes to get bixi heatmap data
*** Todo: Update bixi to real time
*/

console.log("bixiHeatmap.js loaded");


// To hold bixi data of current snapshot
var bixiData = []; //raw data of snapshot looking at right now. Maybe past or current data

// Bixi heatmap stuff
var bixiMap, bixiHeatmap;

// Bixi Stations of snapshot looking at right now to display bikes on heatmap
var bixiStations = [];

// -----------------------------------------------------------------------------------------------------------------

// Make initial Bixi heatmap on startup
function initBixiHeatMap() 
{
  bixiMap = new google.maps.Map(document.getElementById('bixiMap'), {
    zoom: 13,
    center: {lat: 43.653743, lng: -79.38882},// center: {lat: 37.775, lng: -122.434},
    mapTypeId: 'satellite'
  });

  //Setup bixi heatmap. Points with more bikes are more concentrated
  bixiHeatmap = new google.maps.visualization.HeatmapLayer({
    data: bixiStations,
    map: bixiMap
  });

  // Settings for each zoom level
  bixiMap.addListener('zoom_changed', function() 
  {
    var zoomLevel = bixiMap.getZoom();
    //console.log("bixi radius is: ", bixiHeatmap.get('radius'));
    bixiHeatmap.setOptions({
      dissipating: true,
      maxIntensity: 15
    });

    if(zoomLevel < 9)
    {
      bixiHeatmap.setOptions({
        radius: 0.5,
        opacity: 0.9
        //dissipating: false
      });
      console.log("Zoom level: ", bixiMap.getZoom(), "  Radius: ", bixiHeatmap.get('radius'));
    }
    else if(zoomLevel == 9)
    {
      bixiHeatmap.setOptions({
        radius: 1,
        opacity: 0.7
        //dissipating: false
      });
      console.log("Zoom level: ", bixiMap.getZoom(), "  Radius: ", bixiHeatmap.get('radius'));
    }
    else if(zoomLevel == 10)
    {
      bixiHeatmap.setOptions({
        radius: 1.5,
        opacity: 0.7
        //dissipating: false
      });
      console.log("Zoom level: ", bixiMap.getZoom(), "  Radius: ", bixiHeatmap.get('radius'));
    }
    else if(zoomLevel == 11)
    {
      bixiHeatmap.setOptions({
        radius: 3,
        opacity: 0.9
        //dissipating: false
      });
      console.log("Zoom level: ", bixiMap.getZoom(), "  Radius: ", bixiHeatmap.get('radius'));
    }
    else if(zoomLevel == 12)
    {
      bixiHeatmap.setOptions({
        radius: 4,
        opacity: 0.9
        //dissipating: false
      });
      console.log("Zoom level: ", bixiMap.getZoom(), "  Radius: ", bixiHeatmap.get('radius'));
    }
    else if(zoomLevel == 13)
    {
      bixiHeatmap.setOptions({
        radius: 6,
        opacity: 0.7
        //dissipating: false
      });
      console.log("Zoom level: ", bixiMap.getZoom(), "  Radius: ", bixiHeatmap.get('radius'));
    }
    else if(zoomLevel == 14)
    {
      bixiHeatmap.setOptions({
        radius: 9,
        opacity: 0.7
        //dissipating: false
      });
      console.log("Zoom level: ", bixiMap.getZoom(), "  Radius: ", bixiHeatmap.get('radius'));
    }
    else if(zoomLevel > 14)
    {
      bixiHeatmap.setOptions({
        radius: null,
        opacity: null
        //dissipating: false
      });
      console.log("Zoom level: ", bixiMap.getZoom(), "  Radius: ", bixiHeatmap.get('radius'));
    }
  });  
}

// -----------------------------------------------------------------------------------------------------------------

// Turns bixi heatmap on/off 
function bixiToggleHeatmap() 
{
     bixiHeatmap.setMap(bixiHeatmap.getMap() ? null : bixiMap);
}

// Changes color of bixi heatmap
function bixiChangeGradient() 
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

     bixiHeatmap.set('gradient', bixiHeatmap.get('gradient') ? null : gradient);
}

// Changes radius of bixi heatmap
function bixiChangeRadius() 
{
     bixiHeatmap.set('radius', bixiHeatmap.get('radius') ? null : 20);
}

// Get updated Bixi data
function bixiUpdateData()
{
  console.log("In bixiUpdateData");

  //Show the modal as will load the bixiHeatmap
  $('#myPleaseWait').modal('show');

  //Remove old stats of bixi
  $("#bixiSnapshotStatsView").empty();

  //Get current bixi data to display on map
  $.ajax({
    url: "/latestBixi",
    type: "post",
    dataType: "json",
    success: function (data)
    {
      bixiData = data;
      drawUserSelectedTimeBixiDataonMap(data);
    },
    error: function(error)
    {
      console.log("Error received back is: ", error);
    }
  }); 

}

// -----------------------------------------------------------------------------------------------------------------

// Draws latest Bixi data on heatmap
function drawBixiDataonMap(data)
{
  //console.log("drawBixiDataonMap received data as: ", data);
  var numberOfStations = data.length;
  //console.log("numberOfStations is: ", numberOfStations);

  // Formatting the data to send to heatmap
  var i;
  var j;
  for(i = 0; i < numberOfStations; i++)
  {
    var latitude = data[i]["coordinates"][1];
    var longitude = data[i]["coordinates"][0];
    var bikes = data[i]["bikes"];

    // Shows concentration to show number of bikes
    var entry = {location: new google.maps.LatLng(latitude, longitude), weight: bikes};
    bixiStations.push(entry);
  }

     //console.log("bixiStations is: ", bixiStations);
     initBixiHeatMap();
}
// -----------------------------------------------------------------------------------------------------------------

 // Draw heatmap of bixi at user specified time
 function drawUserSelectedTimeBixiDataonMap(data)
 {
    //console.log("drawUserSelectedTimeBixiDataonMap: data received is: ", data);
    var numberOfStations = data.length;
    console.log("numberOfStations is: ", numberOfStations);

    // Remove old stations from bixiStations
    bixiStations.splice(0,bixiStations.length);
    console.log("bixiStations.length is: ", bixiStations.length);

    // Formatting the data to send to heatmap
    var i;
    for(i = 0; i < numberOfStations; i++)
    {
      var latitude = data[i]["coordinates"][1];
      var longitude = data[i]["coordinates"][0];
      var bikes = data[i]["bikes"];
      if((latitude == 0) && (longitude == 0))
      {
        continue;
      }

      var entry = {location: new google.maps.LatLng(latitude, longitude), weight: bikes};
      bixiStations.push(entry);
    }

    console.log("new bixiStations.length after push is: ", bixiStations.length);

    //Remove old heat map data
    bixiHeatmap.setMap(null)
    
    bixiHeatmap = new google.maps.visualization.HeatmapLayer({
          data:  bixiStations,
          map: bixiMap
        });


    //Dont show the please wait modal as new heatmap generated
    $('#myPleaseWait').modal('hide');
    return;
 }

// -----------------------------------------------------------------------------------------------------------------

// Get snapshot data about bixi at user specified time, then call drawUserSelectedTimeBixiDataonMap
function bixiSnapShotSubmit()
{
  console.log("bixiSnapShotSubmit called.");
  bixiSnapshotDateTime = $('#bixiSnapshotDateTimeValue').val();
  console.log("bixiSnapshotDateTime is: ", bixiSnapshotDateTime);

    // Make sure user enters in a date
  if(bixiSnapshotDateTime == "")
  {
    console.log("Nothing entered in bixi form");
    alert("Need to enter in a past date in the bixi form!");
    return;
  }


  // Show the modal as will load the heatmap
  $('#myPleaseWait').modal('show');

  //Remove old Bixi stats
  $("#bixiSnapshotStatsView").empty();

  // Get specific bixi data to display on map
  $.ajax({
    url: "/userSelectedTimeBixiData",
    type: "post",
    dataType: "json",
    data: 
    {
      startDateTime: bixiSnapshotDateTime
    },
    success: function (data) 
    {
      //console.log("bixiSnapShotSubmit: Data.length received back is: ", data);
      console.log("bixiSnapShotSubmit: Data received back is: ", data.length);
      bixiData = data;
      drawUserSelectedTimeBixiDataonMap(data);
    },
    error: function(error)
    {
      console.log("Error received back is: ", error);
    }
  });
}

// -----------------------------------------------------------------------------------------------------------------

// Load current bixi data on heatmap
$(document).ready(function()
{
    console.log("bixiScripts document ready");

    // Bixi snapshpt DateTimePickers initializer
    $('#bixiSnapshotDateTime').datetimepicker(
    {
      locale: 'en',
      stepping: 5,
      sideBySide: true,
      format: 'YYYY/MM/DD hh:mm A',
      useCurrent: false,
      minDate: '2015/01/26 10:00 AM'
    });


    //Get current bixi data to display on heatmap
     $.ajax(
     {
         url: "/latestBixi",
         type: "post",
         dataType: "json",
         success: function (data) 
         {
           //console.log("Data received back for bixi is: ", data);
           bixiData = data;
           drawBixiDataonMap(data);
         },
         error: function(error)
         {
           console.log("Error received back for bixi is: ", error);
         }
     });
});