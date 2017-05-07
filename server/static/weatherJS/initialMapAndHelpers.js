
// Initilize rectangle to be able to select points
function initRectangle()
{
  if(rectangleOnScreen == 1)
  {
    //console.log("Rectangle on screen already so dont make");
    return;
  }
  //console.log("Rectangle NOT on screen so make");
  rectangleOnScreen = 1;

  //Hide the avg, max, min stats
  $('#keyStats').hide();
  
  //Making rectangular box to select nodes
  var bounds = 
  {
    north: 44.08632793039645,
    south: 43.97637149262356,
    east: -79.65149609374998,
    west: -79.85749609375
  };

  // Define the rectangle and set its editable property to true.
  rectangle = new google.maps.Rectangle(
  {
    bounds: bounds,
    editable: true,
    draggable: true
  });

  rectangle.setMap(map);

  // Add event listeners on the rectangle. Add in if needed
  //rectangle.addListener('bounds_changed', newRectangleCoordinates);
  rectangle.addListener('bounds_changed', displayChosenRectangleLocations);


  // Define an info window on the map
  infoWindow = new google.maps.InfoWindow();

  // When dragging, show the new coordinates for the rectangle in an info window.
  function newRectangleCoordinates(event) 
  {
    //console.log("Dragging");
    var ne = rectangle.getBounds().getNorthEast();
    var sw = rectangle.getBounds().getSouthWest();

    var contentString = '<b>Rectangle moved.</b><br>' +
    'New north-east corner: ' + ne.lat() + ', ' + ne.lng() + '<br>' +
    'New south-west corner: ' + sw.lat() + ', ' + sw.lng();

    // Set the info window's content and position.
    infoWindow.setContent(contentString);
    infoWindow.setPosition(ne);
    infoWindow.open(map);
  }

  // Whenever rectangle moved around
  function displayChosenRectangleLocations(event) 
  {
    var ne = rectangle.getBounds().getNorthEast();
    var sw = rectangle.getBounds().getSouthWest();
    var bounds = new google.maps.LatLngBounds(sw, ne);

    //Empty DOM results
    $("#rectangleResults").empty();

    //Empty the array which has the results
    chosenRectangleLocations = {};

    // Add to chosenRectangleLocations array if marker falls into rectangle
    //for (i=0; i<weatherMarkers.length;i++)
    for (var key in weatherMarkers) 
    {
      var latitude = weatherMarkers[key]["latitude"];
      var longitude = weatherMarkers[key]["longitude"];
      if (bounds.contains(new google.maps.LatLng(latitude, longitude))) //selected
      {

        var location = weatherMarkers[key]["location"];
        //$("#rectangleResults").append("<p>" + location + "</p>");
        chosenRectangleLocations[location] = weatherMarkers[key];


        //Change color of this marker to green to show selected
        var marker = weatherMarkers[key]["marker"];
        marker.setIcon(selectedPinImage);
      }

      else //Not selected in rectangle, but may be clicked separately
      {

        //If not clicked on already, change color of this marker to red to show unselected 
        if(!(key in chosenClickedLocations))
        {
          //console.log("not in chosenClickedLocations");
          var marker = weatherMarkers[key]["marker"];
          marker.setIcon(unselectedPinImage);  
        }
        else
        {
          //console.log("in chosenClickedLocations");
        }

        //console.log("weatherMarkers is: ", weatherMarkers);
      }
    }
  }
} // End of init rectangle

// ------------------------------------------------------------------

// Initialization for weather map. Called from allMapsInit.js
function initWeatherMap()
{
  var center = {lat: 43.739832, lng: -79.65954};  
  map = new google.maps.Map(document.getElementById('map'), 
  {
    //These are google.maps.MapOptions object specification
    zoom: 9,
    center: center
  });

  //Initialize rectangle
  initRectangle();
  rectangleOnScreen = 0;
  rectangle.setMap(null);

  console.log("test is ", map.getDiv());

  // Unselected marker colors initialization 
  unselectedPinColor = "fc5e4f";
  unselectedPinImage = new google.maps.MarkerImage("http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|" + unselectedPinColor,
  new google.maps.Size(21, 34),
  new google.maps.Point(0,0),
  new google.maps.Point(10, 34));

  // Selected marker colors initialization 
  selectedPinColor = "52B552";
  selectedPinImage = new google.maps.MarkerImage("http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|" + selectedPinColor,
  new google.maps.Size(21, 34),
  new google.maps.Point(0,0),
  new google.maps.Point(10, 34));


  // Markers for low, medium, high
  lowPinColor = "ffff00";
  lowPinImage = new google.maps.MarkerImage("http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|" + lowPinColor,
  new google.maps.Size(21, 34),
  new google.maps.Point(0,0),
  new google.maps.Point(10, 34));

  mediumPinColor = "ff9933";
  mediumPinImage = new google.maps.MarkerImage("http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|" + mediumPinColor,
  new google.maps.Size(21, 34),
  new google.maps.Point(0,0),
  new google.maps.Point(10, 34));

  highPinColor = "ff3333";
  highPinImage = new google.maps.MarkerImage("http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|" + highPinColor,
  new google.maps.Size(21, 34),
  new google.maps.Point(0,0),
  new google.maps.Point(10, 34)); 
}

// ------------------------------------------------------------------

//Attach popup window to marker
function bindInfoWindow(marker, map, infowindow, html) 
{
    marker.addListener('click', function() {
        infowindow.setContent(html);
        infowindow.open(map, this);
    });
}

//Called when a location is clicked and selected/unselected
function addClickLocation(locationName)
{
  //if location is already in rectangle, unselect and unhighlight
  if(locationName in chosenRectangleLocations)
  {
    console.log("This location already in rectangle");
    var marker = chosenRectangleLocations[locationName]["marker"];
    marker.setIcon(unselectedPinImage);
    delete chosenRectangleLocations[locationName];

    //Also remove from chosenClickedLocations if there
    if(locationName in chosenClickedLocations)
    {
      var marker = chosenClickedLocations[locationName]["marker"];
      marker.setIcon(unselectedPinImage);
      delete chosenClickedLocations[locationName];
    }
  }

  else//location not already in rectangle
  {
    //if location is already clicked before unselect and unhighlight to red
    if (locationName in chosenClickedLocations)
    {
      var marker = chosenClickedLocations[locationName]["marker"];
      marker.setIcon(unselectedPinImage);
      delete chosenClickedLocations[locationName];
    }

    else //Selected for first time, so add to dict and highlight to green
    {
      var marker = weatherMarkers[locationName]["marker"];
      marker.setIcon(selectedPinImage);
      chosenClickedLocations[locationName] = weatherMarkers[locationName];
    }
  } 
  return;
}

// ------------------------------------------------------------------

