console.log("ttcAggregations.js loaded in");

// -------------------------------------------------------------------
function hideTTCTable()
{
  console.log("need to hide table");
  // Hide the ttc aggregation table
  $("#ttcAggregationsResult").hide();

}
// -------------------------------------------------------------------

function ttcAggregationsSubmit()
{
  console.log("ttcAggregationsSubmit button pressed");

  var ttcAggregationsStartTime = $('#ttcAggregationsDateTimeStartValue').val();
  var ttcAggregationsEndTime = $('#ttcAggregationsDateTimeEndValue').val();

    // Make sure user enters in dates
  if((ttcAggregationsStartTime == "") || (ttcAggregationsEndTime == ""))
  {
    console.log("Nothing entered in ttc form");
    alert("Need to enter in both dates in the TTC aggregations form!");
    return;
  }

  // Show the modal as will make an aggregation
  $('#myPleaseWait').modal('show');

  console.log("ttcAggregationsStartTime is: ", ttcAggregationsStartTime);
  console.log("ttcAggregationsEndTime is: ", ttcAggregationsEndTime);

  var e = document.getElementById("ttcAggregationSelection");
  var aggType = e.options[e.selectedIndex].value;
  console.log("ttc aggType is: ", aggType);

  // Ajax call
  $.ajax({
    url: '/ttcAggregation',
    type: 'post',
    dataType: 'json',
    data: 
    {
      aggType: aggType, stringStartDateTime: ttcAggregationsStartTime, 
      stringDateEndTime: ttcAggregationsEndTime
    },
    success: function(data)
    {
      console.log("data from server is: ", data);
        // Hide the modal
        $('#myPleaseWait').modal('hide');
        
        // Make table
        $("#ttcAggregationsResult").show();

        var ttcTableResults = [];

        function drawTable() 
        {
          var data = new google.visualization.DataTable();
          data.addColumn('string', 'Route Name');
          data.addColumn('number', 'Number of vehicles instances');
          // data.addRows([
          //   ['Mike',  1200],
          //   ['Jim',   8000],
          //   ['Alice', 1100],
          //   ['Bob',   09]
          // ]);
          data.addRows(ttcTableResults);
          var table = new google.visualization.Table(document.getElementById('ttcTable'));

          table.draw(data, {showRowNumber: true, width: '100%', height: '100%', page:'enable', pageSize:20});
        }

      //Format output
      ttcTableResults = [];
      var dataLength = data.length;
      var i;
      for(i = 0;i<dataLength;i++)
      {
        //Make each row
        var myEntry = [];
        myEntry.push(data[i]["routeName"]);
        myEntry.push(data[i]["value"]);
        ttcTableResults.push(myEntry); 
      }
      console.log("ttcTableResults is: ", ttcTableResults);
      



      // Draw chart
      google.charts.load('current', {'packages':['table']});
      google.charts.setOnLoadCallback(drawTable);

        
    },
    error: function(error)
    {
      console.log("error from server is: ", error);
    }
  }); 

}

// -------------------------------------------------------------------

// Initialize start, end date time pickers
$(document).ready(function()
{

  // Hide the ttc aggregation table
  $("#ttcAggregationsResult").hide();

  // TTC aggregations date time start initializer
  $('#ttcAggregationsDateTimeStart').datetimepicker(
  {
    locale: 'en',
    stepping: 5,
    sideBySide: true,
    format: 'YYYY/MM/DD hh:mm A',
    useCurrent: false,
    minDate: '2015/01/26 5:00 AM'
  });

  // TTC aggregations date time end initializer
  $('#ttcAggregationsDateTimeEnd').datetimepicker(
  {
    locale: 'en',
    stepping: 5,
    sideBySide: true,
    format: 'YYYY/MM/DD hh:mm A',
    useCurrent: false,
    minDate: '2015/01/26 5:00 AM'
  });
});