console.log("weatherColorScripts loaded.");
console.log("weatherMarkers is: ", weatherMarkers);

//------------------------------------------------------------------

//Helper functions	
function sortNumber(a,b) 
{
	return a-b;
}

//fuction to get the percentile
function get_percentile(percentile, array) 
{
  //array.sort();
  var index = (percentile/100) * array.length;
  var result;
  if (Math.floor(index) == index) 
  {
    result = (array[index-1] + array[index])/2;
  }
  else
  {
      result = array[Math.floor(index)];
  }
  return result;
}

//------------------------------------------------------------------

//Button handler to color based on temperature
function colorPercentile(id)
{
  console.log("id is: ",id);
  
  //Remove rectangle
  rectangle.setMap(null);
  rectangleOnScreen = 0;

  //Finding out what to color by and also compute avg,max, min
  var colorBy;
  if(id == "colorTemp")
  {
  	colorBy = "temp_c";
    //Get avg, max, min and update DOM
    getAvgMaxMin(colorBy);
  }

  else if(id == "colorWind")
  {
  	colorBy = "wind_mph";
    //Get avg, max, min and update DOM
    getAvgMaxMin(colorBy);
  }
  else
  {
    colorBy = "relative_humidity";
    //Get avg, max, min and update DOM
    getAvgMaxMin(colorBy);
  }
  
  console.log("colorBy is: ", colorBy);

  
  var locationValues = [];
  //Get locations values into array
  for (var key in weatherMarkers)
  { 
    var value = weatherMarkers[key][colorBy];
    //Strip of percentage sign if humidity
    if(colorBy == "relative_humidity")
    {
    	value = value.slice(0, -1);
    }
    value = parseFloat(value);
    locationValues.push(value);
  }

  locationValues.sort(sortNumber);

  //Making percentile ranges. Value returned is starting range for percentile
  var low = get_percentile(33, locationValues);

  var medium = get_percentile(67, locationValues);

  //Color markers based on percentiles
  for (var key in weatherMarkers)
  {
    var marker = weatherMarkers[key]["marker"];
    var newValue = weatherMarkers[key][colorBy];
    if(colorBy == "relative_humidity")
    {
      newValue = newValue.slice(0, -1);
    }
    newValue = parseFloat(newValue);
    
    //Change color of this marker to show low, medium, high values
    if(newValue<=low)
    {
      marker.setIcon(lowPinImage);
    }
    else if(newValue<=medium)
    {
      marker.setIcon(mediumPinImage);
    }
    else
    {
      marker.setIcon(highPinImage);
    }
  }
}

//------------------------------------------------------------------

