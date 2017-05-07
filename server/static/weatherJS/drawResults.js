
  // Ajax call for generating weather graphs
  function drawChart(jsonLocations, aggType, field, stringStartDateTime, stringDateEndTime, categoryFinal)
  {
    //Todo: Pass in field name here i.e temp, wind, humidity
    $.ajax({
      url: '/weatherAggregation',
      type: 'post',
      dataType: 'json',
      data: 
      {
        chosenLocations: jsonLocations, aggType: aggType, field: field, stringStartDateTime: stringStartDateTime, 
        stringDateEndTime: stringDateEndTime, category:categoryFinal
      },
      success: function(data)
      {
        console.log("Ajax for graph: Success! Data received from server is: ",  data);

        //Empty the allChosenLocations array
        allChosenLocations.splice(0,allChosenLocations.length);

        //Formatting results into a form to make graph
        $('#chartResult').show();
        console.log("Formatting data...");
        console.log("field for graph is: ", field);
        var formattedValues = {};
        formattedValues["packets"] = [];
        lengthOfArray = data.length;
        console.log("length of array returned is: ", lengthOfArray);
        var i = 0;
        for(i=0;i<lengthOfArray;i++)
        {
            formattedValues["packets"].push(data[i]);
        }
        console.log("New formatted array is: ", formattedValues);

        var chartData = new google.visualization.DataTable();

        var vAxisName;
        if(field == "windMph")
        {
          chartData.addColumn('datetime', 'Timestamp');
          chartData.addColumn('number', 'Windspeed');

          formattedValues["packets"].forEach(function(packet)
          {
            console.log("packet.timestamp is: ", packet.timestamp);
            console.log("packet.windMph is: ", packet.windMph);
            console.log("\n");
            chartData.addRow([
                (new Date(packet.timestamp * 1000)),
                parseFloat(packet.windMph),
            ]);
          });

          vAxisName = "Wind Speed [mph]";
        }

        else if(field == "temp_c")
        {
          chartData.addColumn('datetime', 'Timestamp');
          chartData.addColumn('number', 'Temperature');

          formattedValues["packets"].forEach(function(packet)
          {
            console.log("packet.timestamp is: ", packet.timestamp);
            console.log("packet.temp_c is: ", packet.temp_c);
            console.log("\n");
            chartData.addRow([
                (new Date(packet.timestamp * 1000)),
                parseFloat(packet.temp_c),
            ]);
          });

          vAxisName = "Temperature [C]"; 
        }

        else if(field == "relativeHumidity")
        {
          chartData.addColumn('datetime', 'Timestamp');
          chartData.addColumn('number', 'Humidity');

          formattedValues["packets"].forEach(function(packet)
          {
            console.log("packet.timestamp is: ", packet.timestamp);
            console.log("packet.relativeHumidity is: ", packet.relativeHumidity);
            console.log("\n");
            chartData.addRow([
                (new Date(packet.timestamp * 1000)),
                parseFloat(packet.relativeHumidity),
            ]);
          });

          vAxisName = "Relative Humidity [%]";
        }

        else
        {
          console.log("Wrong field!");
        }

        var options = {
            title: aggType,
            hAxis: {
                title: 'Date & Time'
            },
            vAxis: {
                title: vAxisName
            },
            legend: { position: 'bottom' }, 
            height : 400
        };

        var chart = new google.visualization.LineChart(document.getElementById('chart'));

        // Hide the modal since got data
        $('#myPleaseWait').modal('hide');

        chart.draw(chartData, options);          
      },

      error: function(error)
      {
        console.log("Ajax for graph: Error received back is: ", error);

        //Empty the allChosenLocations array
        allChosenLocations.splice(0,allChosenLocations.length);
      }
    });
  }

// ------------------------------------------------------------------

// Display Top 10 Data Table
// 
function drawTop10Table(jsonLocations, aggType, field, stringStartDateTime, stringDateEndTime, categoryFinal)
{
  $.ajax({
    url: '/weatherAggregation',
    type: 'post',
    dataType: 'json',
    data: 
    {
      //Note: aggType is either top10Highest, top10Lowest for the category top10
      chosenLocations: jsonLocations, aggType: aggType, field: field, stringStartDateTime: stringStartDateTime, 
      stringDateEndTime: stringDateEndTime, category: categoryFinal
    },
    success: function(data)
    {
      console.log("Ajax for top10: Success! Data received is: ", data);

      //Empty the allChosenLocations array IMP
      allChosenLocations.splice(0,allChosenLocations.length);
      
      //Update DOM to show results
      $('#top10Results').show();
      $('#top10Table').empty();

      //Set headers and sentences for results
      if(aggType == "top10HighestSnapshots")
      {
        $('#top10ResultsHeader').html("Top 10 highest snapshots for " + field);     
      }
      else if(aggType == "top10LowestSnapshots") 
      {
        $('#top10ResultsHeader').html("Top 10 lowest snapshots for " + field);     
      }
      else if(aggType == "top10HighestAvgLocations") 
      {
        $('#top10ResultsHeader').html("Top 10 highest ranked locations for " + field);     
      }
      else if(aggType == "top10LowestAvgLocations") 
      {
        $('#top10ResultsHeader').html("Top 10 lowest ranked locations for " + field);     
      }
      else
      {
        console.log("Weird case! Shouldnt come here in dom update for top10!");
      }

      var chartData = new google.visualization.DataTable();
      var dataLength = data.length;
      var i;

      if((aggType == "top10HighestSnapshots") || (aggType == "top10LowestSnapshots"))
      {
        chartData.addColumn('number', 'Rank');
        chartData.addColumn('number', field);
        chartData.addColumn('string', 'Location');
        chartData.addColumn('datetime', 'Time');        

        for(i = 0; i < dataLength; i++)
        {
          chartData.addRow([
            parseInt(i + 1),
            parseFloat(data[i][field]),
            (data[i]["location"]),
            (new Date(data[i]["timestamp"] * 1000)),
          ]);
        }

      }
      //Sentence for top 10 avg ranked locations
      else if((aggType == "top10HighestAvgLocations") || (aggType == "top10LowestAvgLocations"))
      {
        chartData.addColumn('number', 'Rank');
        chartData.addColumn('number', field);
        chartData.addColumn('string', 'Location');
        
        for(i = 0; i < dataLength; i++)
        {
          chartData.addRow([
            parseInt(i + 1),
            parseFloat(data[i][field]),
            (data[i]["location"]),
          ]);
        }

      }

      var options = {
        showRowNumber: false,
        width: '100%',
        height: '100%'
      };

      var table = new google.visualization.Table(document.getElementById('top10Table'));

      // Hide the modal since got data
      $('#myPleaseWait').modal('hide');
      
      table.draw(chartData, options);
    },
    error: function(error)
    {
      console.log("Ajax for top10: Error! Error received is: ", data);
      //Empty the allChosenLocations array IMP
      allChosenLocations.splice(0,allChosenLocations.length);
    }
  });
}




