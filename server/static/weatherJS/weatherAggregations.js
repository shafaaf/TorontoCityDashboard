/* 
*** Draw initial weather data on map to do aggregations on
*** Takes care of weather aggreagtion submission
*/


console.log("weatherScripts loaded.");

//Flag to keep track of whether rectangle has been made on screen or not
var rectangleOnScreen = 0;

var map;
var rectangle;
var infoWindow;

//Markers for all the raw weather locations
var weatherMarkers = {};

/* List of locations selected by user.*/
var chosenRectangleLocations = {};  // Selected from rectangle
var chosenClickedLocations = {};  // Selected from clicks
var allChosenLocations = []  // Both combined together

//For marker colors when selected
var selectedPinColor;
var selectedPinImage;

//For marker colors when not selected
var unselectedPinColor;
var unselectedPinImage;

//Marker colors when doing percentiles from low, medium to high
var lowPinColor;
var lowPinImage;

var mediumPinColor;
var mediumPinImage;

var highPinColor;
var highPinImage;

// -----------------------------------------------------------------------------------------------------------------------------

// Called when submitting aggregation with click
function submitAggregation()
{
  console.log("Submitted aggregation...");

  // Show the modal as will make an aggregation
  $('#myPleaseWait').modal('show');

  //Hiding old results
  $('#chartResult').hide(); //chart which shows min, max, avg
  $('#overallStats').hide();  // overall stats of avg, min, max
  $('#top10Results').hide();  // top 10 results of snapshots or avg locations for field
  $('#resultMapContainer').hide();  // resultant heat map of results

  //Get all locations from rectangle and indivitual clicked locations
  var chosenRectangleLocationsLen = chosenRectangleLocations.length;
  var i;
  for (var key in chosenRectangleLocations) // Adding unique ones from rectangle to allChosenLocations array
  {
    if(key in chosenClickedLocations)
    {
      //console.log("Already present in chosenClickedLocations: ", chosenRectangleLocations[key]);
    }
    else  //rectangle location not present as clicked location so add in
    {
      allChosenLocations.push(chosenRectangleLocations[key]["location"]);
    }
  }

  //Add ALL ones from chosenClickedLocations dict
  for(var key in chosenClickedLocations) 
  {
    allChosenLocations.push(key);
  }

  //console.log("allChosenLocations is: ", allChosenLocations);

  //Converting chosen locations into json string
  var formattedChosenLocations = {};
  formattedChosenLocations["locations"] = allChosenLocations;
  var jsonLocations = JSON.stringify(formattedChosenLocations);
  console.log("jsonLocations is: ", jsonLocations);
  
// --------------------------------------------------------
  
  // Formatting start and end times

  // Start time conversion to string
  var startHour = $('#startTime').attr("data-timepicki-tim");
  var startMinute = $('#startTime').attr("data-timepicki-mini");
  var startType = $('#startTime').attr("data-timepicki-meri");

  var dateSliderStartDate = $("#dateSlider").dateRangeSlider("min");
  var startDate = dateSliderStartDate.toString();
  var res = startDate.split(" ");

  var month;
  if(res[1] == "Jan")
    month = 01;
  else if(res[1] == "Feb")
    month = 02;
  else if(res[1] == "Mar")
    month = 03;
  else if(res[1] == "Apr")
    month = 04;
  else if(res[1] == "May")
    month = 05;
  else if(res[1] == "Jun")
    month = 06;
  else if(res[1] == "Jul")
    month = 07;
  else if(res[1] == "Aug")
    month = 08;
  else if(res[1] == "Sep")
    month = 09;
  else if(res[1] == "Oct")
    month = 10;
  else if(res[1] == "Nov")
    month = 11;
  else if(res[1] == "Dec")
    month = 12;
  else
    console.log("ERROR in extracting months!!!!!");

  //Format: 2015/01/26 05:00 PM
  var stringStartDateTime = res[3] + "/" + month + "/" + res[2] + " " + startHour + ":" + startMinute + " " + startType;

  
  //End time conversion to string
  var endHour = $('#endTime').attr("data-timepicki-tim");
  var endMinute = $('#endTime').attr("data-timepicki-mini");
  var endType = $('#endTime').attr("data-timepicki-meri");    

  var dateSliderEndDate = $("#dateSlider").dateRangeSlider("max");
  var endDate = dateSliderEndDate.toString();
  res = endDate.split(" ");

  var month;
  if(res[1] == "Jan")
    month = 01;
  else if(res[1] == "Feb")
    month = 02;
  else if(res[1] == "Mar")
    month = 03;
  else if(res[1] == "Apr")
    month = 04;
  else if(res[1] == "May")
    month = 05;
  else if(res[1] == "Jun")
    month = 06;
  else if(res[1] == "Jul")
    month = 07;
  else if(res[1] == "Aug")
    month = 08;
  else if(res[1] == "Sep")
    month = 09;
  else if(res[1] == "Oct")
    month = 10;
  else if(res[1] == "Nov")
    month = 11;
  else if(res[1] == "Dec")
    month = 12;
  else
    console.log("ERROR in extracting months!!!!!");

  var stringDateEndTime = res[3] + "/" + month + "/" + res[2] + " " + endHour + ":" + endMinute + " " + endType;

// --------------------------------------------------------

  //Get field (temp, windmph or humidity)
  var e = document.getElementById("fieldSelect");
  var field = e.options[e.selectedIndex].value;
  console.log("field is: ", field);

// --------------------------------------------------------

  /*  Get aggregation type 
        from avg, max, min (for graphs), or 
        top10HighestSnapshots, top10LowestSnapshots, 
        top10HighestAvgLocations, top10LowestAvgLocations(for top10) 
  */
  var e = document.getElementById("ddlViewBy");
  var aggType = e.options[e.selectedIndex].value;
  console.log("aggType is: ", aggType);
  
  //Category decides on whether graph, (avg, max, min) or top 10 (highest, lowest)
  var category;
  if((aggType == "avg") || (aggType == "min") || (aggType == "max"))  //graph category
  {
    category = "graph";
    console.log("category is: ", category);
  }
  else if((aggType == "top10HighestSnapshots") || (aggType == "top10LowestSnapshots"))
  {
    category = "top10";
    console.log("category is: ", category);
  }
  else if((aggType == "top10HighestAvgLocations") || (aggType == "top10LowestAvgLocations"))
  {
    category = "top10";
    console.log("category is: ", category);
  }

  else if(aggType == "overalls")
  {
    category = "overalls";
    console.log("category is: ", category);
  }
  else
  {
    console.log("ERROR! category is weird!");
  }

// --------------------------------------------------------

  //Setting up category format i.e graph, top10, overalls
  var categoryFinal = {};
  categoryFinal["category"] = category;
  categoryFinal = JSON.stringify(categoryFinal);


// ------------------------------- Ajax calls (still under submitAggregation())

// Called when graph category ajax call is done
// -------------------------------
  function myDrawChart()  //in drawResults.js
  {
    drawChart(jsonLocations, aggType, field, stringStartDateTime, stringDateEndTime, categoryFinal);
  }

  function myDrawTop10Table()
  {
    drawTop10Table(jsonLocations, aggType, field, stringStartDateTime, stringDateEndTime, categoryFinal)
  }
  
// -------------------------------

  //Draw chart and send draw ajax request if graph category
  if(category == "graph")
  {
    console.log("graph category request!");
    //Will draw the graph for max, min, avg
    google.charts.load('current', {'packages':['corechart']});
    google.charts.setOnLoadCallback(myDrawChart);
  }
  else if (category == "top10")
  {
    console.log("category request for: ", category);
    console.log("aggType is: ", aggType);

    google.charts.load('current', {'packages':['table']});
    google.charts.setOnLoadCallback(myDrawTop10Table);
  }
  else if(category == "overalls")
  {
    console.log("category request for: ", category);
      $.ajax({
        url: '/weatherAggregation',
        type: 'post',
        dataType: 'json',
        data: 
        {
          // aggType is overalls for category overalls (not used in this case)
          chosenLocations: jsonLocations, aggType: aggType, field: field, stringStartDateTime: stringStartDateTime, 
          stringDateEndTime: stringDateEndTime, category: categoryFinal
        },
        success: function(data)
        {
          console.log("Ajax for overalls: Success! Data received is: ", data);
          
          //Empty the allChosenLocations array IMP
          allChosenLocations.splice(0,allChosenLocations.length);

          //Update divs to show stats
          $('#overallStats').show();
          var avg = data["avg"];
          var max = data["max"];
          var min = data["min"];

          $('#overallAveragePara').text(avg);
          $('#overallMaximumPara').text(max);
          $('#overallMinimumPara').text(min);

          // Hide the modal since got data
          $('#myPleaseWait').modal('hide');
          
        },
        error: function(error)
        {
          console.log("Ajax for overalls: Error! Error received is: ", data);
          //Empty the allChosenLocations array IMP
          allChosenLocations.splice(0,allChosenLocations.length);
        }
      });
  }

  else
  {
    console.log("Errorzzz in category selection.");
  }


} // End of submit aggregation

// ------------------------------------------------------------------

// Display weather data on startup. 
// Called after gettting latest data from AJAX call
function drawWeatherDataonMap(data)
{
  //console.log("drawWeatherDataonMap: data is ", data);

  //Adding in markers
  for(i=0;i<data.length;i++)
  {
    //Setting marker properties
    var latitude = Number(data[i]["display_location"]["latitude"]);
    var longitude = Number(data[i]["display_location"]["longitude"]);
    var myLatlng = new google.maps.LatLng(latitude,longitude);
    
    //Making the marker
    var marker = new google.maps.Marker({
      position: myLatlng,
      title:"This is a marker",
      icon: unselectedPinImage
    });
    
    // To add the marker to the map
    marker.setMap(map);

    //Add to my marker dict
    var myEntry = {};
    myEntry["location"] = data[i]["location"];
    myEntry["latitude"] = data[i]["display_location"]["latitude"];
    myEntry["longitude"] = data[i]["display_location"]["longitude"];

    myEntry["temp_c"] = data[i]["current_observation"]["temp_c"];
    myEntry["wind_mph"] = data[i]["current_observation"]["wind_mph"];
    myEntry["relative_humidity"] = data[i]["current_observation"]["relative_humidity"];
    
    myEntry["marker"] = marker;

    
    var location = data[i]["location"];
    weatherMarkers[location] = myEntry;

    //Add in popup boxes
    //console.log("Location is: ", data[i]["location"]);
    var contentString = '<div id= "content">'+
          '<div id="siteNotice">'+
          '</div>'+

          '<h1 id="firstHeading" class="firstHeading">' + data[i]["location"] + '</h1>'+
          '<button type="button" onclick="addClickLocation(\'' + data[i]["location"] + '\')">Select/Unselect Location!</button>' + 
          
          '<div id="bodyContent">'+
            '<h4>' + 'Current Observation' + '</h4>' +
              '<p>' + 'Observation Time: ' + data[i]["current_observation"]["observation_time"] + '</p>' +
              '<p>' + 'relative_humidity: ' + data[i]["current_observation"]["relative_humidity"] + '</p>' +
              '<p>' + 'temp_c: ' + data[i]["current_observation"]["temp_c"] + '</p>' +
              '<p>' + 'temperature_string: ' + data[i]["current_observation"]["temperature_string"] + '</p>' +
              '<p>' + 'timestamp: ' + data[i]["current_observation"]["timestamp"] + '</p>' +
              '<p>' + 'visibility_mi: ' + data[i]["current_observation"]["visibility_mi"] + '</p>' +
              '<p>' + 'weather: ' + data[i]["current_observation"]["weather"] + '</p>' +
              '<p>' + 'wind_dir: ' + data[i]["current_observation"]["wind_dir"] + '</p>' +
              '<p>' + 'wind_mph: ' + data[i]["current_observation"]["wind_mph"] + '</p>' +
              '<p>' + 'wind_string: ' + data[i]["current_observation"]["wind_string"] + '</p>' +

            '<h4>' + 'Display Location' + '</h4>' +
              '<p>' + 'full: ' + data[i]["display_location"]["full"] + '</p>' +
              '<p>' + 'latitude: ' + data[i]["display_location"]["latitude"] + '</p>' +
              '<p>' + 'longitude: ' + data[i]["display_location"]["longitude"] + '</p>' +

            '<h4>' + 'observation_location' + '</h4>' +
              '<p>' + 'full: ' + data[i]["observation_location"]["full"] + '</p>' +
              '<p>' + 'latitude: ' + data[i]["observation_location"]["latitude"] + '</p>' +
              '<p>' + 'longitude: ' + data[i]["observation_location"]["longitude"] + '</p>' +

            '<h4>' + 'location: ' + data[i]["location"] + '</h4>' +
            '<h4>' + 'temp_c: ' + data[i]["temp_c"] + '</h4>' +
            '<h4>' + 'timestamp: ' + data[i]["timestamp"] + '</h4>' +  

          '</div>'+
          '</div>';

    //Make info window
    var infowindow = new google.maps.InfoWindow();
    bindInfoWindow(marker, map, infowindow, contentString); 
  }
}

// ---------------------------------------------------------------------------------------------------------------------

$(document).ready(function()
{
  console.log("weatherScripts document ready");

// ---------------------------------------------

  //Hide the key stats below map
  $('#keyStats').hide();

  // Hide resultant stuff
  $('#chartResult').hide();
  $('#overallStats').hide();
  $('#top10Results').hide();
  $('#resultMapContainer').hide();
  
  //Initialize time picker
  $(".time_element").timepicki();

  // Build range slider
  $("#dateSlider").dateRangeSlider({
    defaultValues:{
      min: new Date(2016, 05, 29),
      max: new Date(2016, 08, 21)
    }});


  //Get current date time to set max
  var today = new Date();
  var dd = today.getDate();
  var mm = today.getMonth()+1; //January is 0!
  var yyyy = today.getFullYear();

  console.log("today is: ", today);
  console.log("dd is: ", dd);
  console.log("mm is: ", mm);
  console.log("yyyy is: ", yyyy);

  //Setting min and max values for slider
  var maxYear = yyyy;
  var maxMonth = mm - 1;
  var maxDate = dd;
   $('#dateSlider').dateRangeSlider(
      "option",
      "bounds",
      {
        min: new Date(2016, 05, 29),
        max: new Date(maxYear, maxMonth, maxDate)  
      }
    );

// ---------------------------------------------

  // Get current weather data to display on map
  $.ajax({
    url: "/latestWeather",
    type: "post",
    dataType: "json",
    success: function (data) 
    {
      //console.log("Data received back is: ", data);
      drawWeatherDataonMap(data);
    },
    error: function(error){
      console.log("Error received back is: ", error);
    }
  });

// ---------------------------------------------

});

// -----------------------------------------------------------------------------------------------------------------
