console.log("avgMaxMinAggregations.js loaded");


//Gets average of array passed in
function averageFunc(myArray)
{
	console.log("average: myArray is: ", myArray);
	var sum = 0;
	var i;
	for(i = 0;i<myArray.length; i++)
	{
		sum = sum + myArray[i]["value"];
	}
	console.log("sum is: ", sum);
	var average = sum/(myArray.length);
	console.log("average is: ", average);
	return average;
}	

//Gets max of array passed in
function maxFunc(myArray)
{
	console.log("max: myArray is: ", myArray);
  var max = myArray[0]["value"];
  var result = {};
  result["key"] =  myArray[0]["key"];
  result["value"] = max;

	var i;
	for(i=0;i<myArray.length; i++)
	{
		if(myArray[i]["value"] > max)
		{
			max = myArray[i]["value"];
      result["key"] = myArray[i]["key"];
      result["value"] = max;
		}
	}
	console.log("result is: ", result);
	return result;
}

//Gets min of array passed in
function minFunc(myArray)
{
	console.log("min: myArray is: ", myArray);
	var min = myArray[0]["value"];
  var result = {};
  result["key"] =  myArray[0]["key"];
  result["value"] = min;
	
  var i;
	for(i=0;i<myArray.length; i++)
	{
		if(myArray[i]["value"] < min)
		{
      console.log("min is: ", min);
			min = myArray[i]["value"];
      result["key"] = myArray[i]["key"];
      result["value"] = min;
		}
	}
  //console.log("min is finally: ", result);
	console.log("result is: ", result);
	return result;
}

//------------------------------------------------------------------
//Compute and update avg, max, min for temp, windmph, humidiity
function getAvgMaxMin(computeBy)
{
  //Show the key stats div, and remove old values
  $('#keyStats').show();
  $('#totalAverageValue').empty();
  $('#totalMaxValue').empty();
  $('#totalMinValue').empty();
  console.log("weatherMarkers is: ", weatherMarkers);
  console.log("computeBy is: ", computeBy);
  
  var values = [];
  
  for(var key in weatherMarkers)
  {
    var value = weatherMarkers[key][computeBy];
    if(computeBy == "relative_humidity")
    {
      value = value.slice(0, -1);
    }
    value = parseFloat(value);
    var myEntry = {};
    myEntry["key"] = key;
    myEntry["value"] = value;
    values.push(myEntry);
  }
  
  var avg = averageFunc(values);
  var max = maxFunc(values);
  var min = minFunc(values);
  
  //Update DOM
  if(computeBy == "temp_c")
  {
  	avg = avg.toString() + " C";
  	max = max["value"].toString() + " C at " + max["key"];
  	min = min["value"].toString() + " C at " + min["key"];
  }
  else if(computeBy ==  "wind_mph")
  {
  	avg = avg.toString() + " mph";
  	max = max["value"].toString() + " mph at " + max["key"];
  	min = min["value"].toString() + " mph at " + min["key"];
  }
  else
  {
  	avg = avg.toString() + "%";
  	max = max["value"].toString() + "% at " + max["key"];
  	min = min["value"].toString() + "% at " + min["key"];
  }

  $('#totalAverageValue').text(avg);
  $('#totalMaxValue').text(max);
  $('#totalMinValue').text(min); 

}
//------------------------------------------------------------------

