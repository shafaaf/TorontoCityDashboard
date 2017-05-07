// Output data from report generator
var jsonOutput;

function outputJsonLink()
{
    console.log("Making jsonLink");
    console.log("jsonOutput is: ", jsonOutput);

    var jswin = window.open("", "jswin", "width=350,height=150");
    var displayFormat = JSON.stringify(jsonOutput, null, '\t');
    //jswin.document.write(displayFormat);

    jswin.document.write('<html><body><pre>' + displayFormat + '</pre></body></html>');
}

// For Report Generator
$(document).ready(function(){

    // Hide the output json button
    $("#outputJson").hide();

    var dataType, aggType, timeInterval, locationName, startDate, startTime, endDate, endTime, startDateTime, endDateTime;

    $('#dataTypeBIXI, #dataTypeTTC, #dataTypeRC, #dataTypeRI, #dataTypeRT, #dataTypeWeather, #dataTypeAir, #selectTimeInterval, #bixiStation, #ttcStation, #weatherLocation, #roadTrafficDistricts, #roadTrafficDataSource').hide();

    // Toggle aggregation type selection tool according to dataType selected
    $('#dataType').change(function(){
        var selected = $('#dataType option:selected').text();

        if(selected == "Weather")
        {
            $('#selectTimeInterval').show();
            $('#weatherLocation').show();
            $('#bixiStation').hide();
            $('#ttcStation').hide();
            $('#roadTrafficDataSource').hide();
            $('#roadTrafficDistricts').hide();

            $('#startDateTime').datetimepicker({
                minDate: '2016/06/28 10:00 PM'
            });

            $('#endDateTime').datetimepicker({
                minDate: '2016/06/28 10:00 PM'
            });
        }
        else if(selected == "BIXI")
        {
            $('#selectTimeInterval').hide();
            $('#weatherLocation').hide();
            $('#bixiStation').hide();
            $('#ttcStation').hide();
            $('#roadTrafficDataSource').hide();
            $('#roadTrafficDistricts').hide();

            $('#startDateTime').datetimepicker({
                minDate: '2015/01/26 10:00 AM'
            });

            $('#endDateTime').datetimepicker({
                minDate: '2015/01/26 10:00 AM'
            });
        }
        else if(selected == "TTC")
        {
            $('#selectTimeInterval').hide();
            $('#weatherLocation').hide();
            $('#bixiStation').hide();
            $('#ttcStation').hide();
            $('#roadTrafficDataSource').hide();
            $('#roadTrafficDistricts').hide();

            $('#startDateTime').datetimepicker({
                minDate: '2015/01/26 10:00 AM'
            });

            $('#endDateTime').datetimepicker({
                minDate: '2015/01/26 10:00 AM'
            });
        }
        else if(selected == "Road Traffic")
        {
            $('#selectTimeInterval').show();
            $('#roadTrafficDataSource').show();
            $('#roadTrafficDistricts').show();
            $('#weatherLocation').hide();
            $('#bixiStation').hide();
            $('#ttcStation').hide();

            $('#startDateTime').datetimepicker({
                minDate: '2017/01/01 12:00 AM'
            });

            $('#endDateTime').datetimepicker({
                minDate: '2017/01/01 12:00 AM'
            });
        }
        else
        {
            $('#selectTimeInterval').hide();
            $('#weatherLocation').hide();
            $('#bixiStation').hide();
            $('#ttcStation').hide();
            $('#roadTrafficDataSource').hide();
            $('#roadTrafficDistricts').hide();
        }

        $('#dataTypeBIXI').toggle(selected == "BIXI");
        $('#dataTypeTTC').toggle(selected == "TTC");
        $('#dataTypeRC').toggle(selected == "Road Closures");
        $('#dataTypeRI').toggle(selected == "Road Incidents");
        $('#dataTypeRT').toggle(selected == "Road Traffic");
        $('#dataTypeAir').toggle(selected == "Air Sensor");
    });

    // Toggle time interval selection tool according to aggType selected
    /*$('#aggTypeBIXI').change(function(){
        var selected = $('#aggTypeBIXI option:selected').text();
        
        $('#selectTimeInterval').show();
    });*/

//---------------------------------------------------------------------

    $('#startDateTime').datetimepicker({
        locale: 'en',
        stepping: 5,
        sideBySide: true,
        format: 'YYYY/MM/DD hh:mm A',
        useCurrent: false
    });

//---------------------------------------------------------------------

    $('#endDateTime').datetimepicker({
        locale: 'en',
        stepping: 5,
        sideBySide: true,
        format: 'YYYY/MM/DD hh:mm A',
        useCurrent: false
    });

//---------------------------------------------------------------------

    $('#formInput').on('submit', function(e) {
        e.preventDefault();

        // Show Please Wait Modal
        $('#myPleaseWait').modal('show');

        // Hide json button link
        $("#outputJson").hide();

        // Hide chart div
        $("#chart_div").hide();        

        dataType = $('#dataType').val();
        timeInterval = $('#timeInterval').val();
        startDateTime = $('#startDateTimeValue').val();
        endDateTime = $('#endDateTimeValue').val();

        if(dataType == "BIXI")
        {
            locationName = $('#bixiLocationName').val();
            aggType = $('#aggTypeBIXI').val();

            function drawBIXIChart(){
                $.ajax({
                    url: '/bixiReportsHandler',
                    type: 'post',
                    dataType: 'json',
                    data: {dataType: dataType, aggType: aggType, timeInterval: timeInterval, locationName: locationName, startDateTime: startDateTime, endDateTime: endDateTime},
                    success: function(data){
                        console.log("Data returned from server is:\n ", data);
                        //$('#outputEcho .dataResult').empty();
                        //$('#outputEcho .dataResult').html(JSON.stringify(data, null, 2));

                        //Formatting results into a form to make graph
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

                        //$('#outputEcho2 .modResult').empty();
                        //$('#outputEcho2 .modResult').html(JSON.stringify(formattedValues, null, 2));

                        var chartData = new google.visualization.DataTable();
                        var chart_div = document.getElementById('chart_div');

                        if(aggType == "BIXI Availability")
                        {
                            chartData.addColumn('datetime', 'Timestamp');
                            chartData.addColumn('number', 'Average Number of Bikes');
                            
                            formattedValues["packets"].forEach(function(packet){
                                
                                chartData.addRow([
                                    (new Date(packet.time_stamp * 1000)),
                                    parseFloat(packet.avg_bikes),
                                ]);
                            });

                            var options = {
                                title: aggType,
                                hAxis: {
                                    title: 'Date & Time'
                                },
                                vAxis: {
                                    title: 'Bike Average'
                                },
                                legend: { position: 'bottom' }, 
                                height : 400,
                                bar: {groupWidth: "95%"}
                            };

                            var chart = new google.visualization.ColumnChart(chart_div);
                            
                            google.visualization.events.addListener(chart, 'ready', function(){
                                chart_div.innerHTML = '<img src="' + chart.getImageURI() + '">';
                            });

                            chart.draw(chartData, options);
                        }
                        else if(aggType == "BIXI Station Downtime")
                        {
                            chartData.addColumn('datetime', 'Timestamp');
                            chartData.addColumn('number', 'Bike Status');
                            
                            formattedValues["packets"].forEach(function(packet){
                                
                                chartData.addRow([
                                    (new Date(packet.time_stamp * 1000)),
                                    parseFloat(packet.bixi_status),
                                ]);
                            });

                            var options = {
                                title: aggType,
                                hAxis: {
                                    title: 'Date & Time'
                                },
                                vAxis: {
                                    title: 'Bike Status'
                                },
                                legend: { position: 'bottom' }, 
                                height : 400
                            };

                            var chart = new google.visualization.LineChart(chart_div);
                            
                            google.visualization.events.addListener(chart, 'ready', function(){
                                chart_div.innerHTML = '<img src="' + chart.getImageURI() + '">';
                            });

                            chart.draw(chartData, options);
                        }
                        else if(aggType == "BIXI Station Usage")
                        {
                            chartData.addColumn('datetime', 'Timestamp');
                            chartData.addColumn('number', 'Delta Number of Bikes');
                            
                            formattedValues["packets"].forEach(function(packet){
                                
                                chartData.addRow([
                                    (new Date(packet.time_stamp * 1000)),
                                    parseFloat(packet.delta),
                                ]);
                            });

                            var options = {
                                title: aggType,
                                hAxis: {
                                    title: 'Date & Time'
                                },
                                vAxis: {
                                    title: 'Bike Delta'
                                },
                                legend: { position: 'bottom' }, 
                                height : 400,
                                bar: {groupWidth: "95%"}
                            };

                            var chart = new google.visualization.ColumnChart(chart_div);
                            
                            google.visualization.events.addListener(chart, 'ready', function(){
                                chart_div.innerHTML = '<img src="' + chart.getImageURI() + '">';
                            });

                            chart.draw(chartData, options);
                        }
                        else
                        {
                            chartData.addColumn('datetime', 'Timestamp');
                            chartData.addColumn('number', 'Number of Bikes');
                            
                            formattedValues["packets"].forEach(function(packet){
                                console.log("packet.time_stamp is: ", packet.time_stamp);
                                console.log("packet.bixi_status is: ", packet.bixi_status);
                                console.log("\n");
                                
                                chartData.addRow([
                                    (new Date(packet.time_stamp * 1000)),
                                    parseFloat(packet.bixi_status),
                                ]);
                            });

                            var options = {
                                title: aggType,
                                hAxis: {
                                    title: 'Date & Time'
                                },
                                vAxis: {
                                    title: 'Bike Status'
                                },
                                legend: { position: 'bottom' }, 
                                height : 400
                            };

                            var chart = new google.visualization.LineChart(chart_div);
                            
                            google.visualization.events.addListener(chart, 'ready', function(){
                                chart_div.innerHTML = '<img src="' + chart.getImageURI() + '">';
                            });

                            chart.draw(chartData, options);

                            // Hide the modal since chart is done
                            $('#myPleaseWait').modal('hide');
                        }                
                    }
                });
            }
            
            google.charts.load('current', {'packages':['corechart']});
            google.charts.setOnLoadCallback(drawBIXIChart);

            
        }
//---------------------------------------------------------------------
        else if(dataType == "TTC")
        {
            /*
            locationName = $('#ttcLocationName').val();

            function drawBIXIChart(){
                $.ajax({
                    url: '/bixiReportsHandler',
                    type: 'post',
                    dataType: 'json',
                    data: {dataType: dataType, timeInterval: timeInterval, locationName: locationName, startDateTime: startDateTime, endDateTime: endDateTime},
                    success: function(data){
                        console.log("Data returned from server is:\n ", data);
                        $('#outputEcho .dataResult').empty();
                        $('#outputEcho .dataResult').html(JSON.stringify(data, null, 2));

                        //Formatting results into a form to make graph
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

                        $('#outputEcho2 .modResult').empty();
                        $('#outputEcho2 .modResult').html(JSON.stringify(formattedValues, null, 2));

                        var chartData = new google.visualization.DataTable();
                        var chart_div = document.getElementById('chart_div');
                        
                        chartData.addColumn('datetime', 'Timestamp');
                        chartData.addColumn('number', 'Number of Bikes');
                        
                        formattedValues["packets"].forEach(function(packet){
                            console.log("packet.time_stamp is: ", packet.time_stamp);
                            console.log("packet.bixi_status is: ", packet.bixi_status);
                            console.log("\n");
                            
                            chartData.addRow([
                                (new Date(packet.time_stamp * 1000)),
                                parseFloat(packet.bixi_status),
                            ]);
                        });

                        var options = {
                            title: aggType,
                            hAxis: {
                                title: 'Date & Time'
                            },
                            vAxis: {
                                title: 'Bike Status'
                            },
                            legend: { position: 'bottom' }, 
                            height : 400
                        };

                        var chart = new google.visualization.LineChart(chart_div);
                        
                        google.visualization.events.addListener(chart, 'ready', function(){
                            chart_div.innerHTML = '<img src="' + chart_div.getImageURI() + '">';
                        });

                        chart.draw(chartData, options);

                        // Hide the modal since chart is done
                        $('#myPleaseWait').modal('hide');
                    }
                });
            }
            
            google.charts.load('current', {'packages':['corechart']});
            google.charts.setOnLoadCallback(drawBIXIChart);

            
            */
        }
//---------------------------------------------------------------------
        else if(dataType == "Weather")
        {   
            console.log("dataType is: ", dataType);            

            // Formatting timeInterval
            console.log("raw timeInterval is: ", timeInterval);
            if(timeInterval == "Every 5 Minutes")
            {
                timeInterval = "5m";
            }
            else if(timeInterval == "Hourly")
            {
                timeInterval = "hour";
            }
            else if(timeInterval == "Daily")
            {
                timeInterval = "day";
            }
            else if(timeInterval == "Weekly")
            {
                timeInterval = "week";
            }
            else if(timeInterval == "Monthly")
            {
                timeInterval = "month";
            }
            else
            {
                console.log("Error here in weather report submit.");
                return;
            }
            console.log("formatted timeInterval is: ", timeInterval);
            
            //Formatting locationName into json string
            locationName = $('#weatherLocationName').val();
            console.log("raw locationName is: ", locationName);
            var formattedChosenLocations = {};
            formattedChosenLocations["locations"] = locationName;
            var jsonLocations = JSON.stringify(formattedChosenLocations);
            console.log("jsonLocations is: ", jsonLocations);

            //start and end date times formatted on server side
            console.log("startDateTime is: ", startDateTime);
            console.log("endDateTime is: ", endDateTime);
            
            function drawWeatherChart(){
                $.ajax({
                    url: '/weatherReportsHandler',
                    type: 'post',
                    dataType: 'json',
                    data: {dataType: dataType, timeInterval: timeInterval, locationName: jsonLocations, startDateTime: startDateTime, endDateTime: endDateTime},
                    success: function(data){
                        console.log("Data returned from server is:\n ", data);
                        jsonOutput = data;
                        
                        // Show json button link
                        $("#outputJson").show();

                        // $('#outputEcho .dataResult').empty();
                        // $('#outputEcho .dataResult').html(JSON.stringify(data, null, 2));

                        //Formatting results into a form to make graph
                        var formattedValues = {};
                        formattedValues["packets"] = [];
                        lengthOfArray = data.length;
                        //console.log("length of array returned is: ", lengthOfArray);
                        var i = 0;
                        for(i=0;i<lengthOfArray;i++)
                        {
                            formattedValues["packets"].push(data[i]);
                        }

                        console.log("New formatted array is: ", formattedValues);

                        // $('#outputEcho2 .modResult').empty();
                        // $('#outputEcho2 .modResult').html(JSON.stringify(formattedValues, null, 2));

                        var chartData = new google.visualization.DataTable();
                        var chart_div = document.getElementById('chart_div');

                        chartData.addColumn('datetime', 'Timestamp');
                        chartData.addColumn('number', 'Temperature');
                        
                        formattedValues["packets"].forEach(function(packet){
                            
                            chartData.addRow([
                                (new Date(packet.date)),
                                parseFloat(packet.temp.avg),
                            ]);
                        });

                        var options = {
                            title: aggType,
                            hAxis: {
                                title: 'Date & Time'
                            },
                            vAxis: {
                                title: 'Average Temperature [C]'
                            },
                            legend: { position: 'bottom' }, 
                            height : 400,
                            bar: {groupWidth: "95%"}
                        };

                        var chart = new google.visualization.LineChart(chart_div);
                        // Show chart div
                        $("#chart_div").show(); 
                        
                        google.visualization.events.addListener(chart, 'ready', function(){
                            chart_div.innerHTML = '<img src="' + chart.getImageURI() + '">';
                        });

                        chart.draw(chartData, options);
                        
                        // Hide the modal since chart is done
                        $('#myPleaseWait').modal('hide');                            
                    }
                });
            }

            google.charts.load('current', {'packages':['corechart']});
            google.charts.setOnLoadCallback(drawWeatherChart);

            
        }
//--------------------------------------------------------------------- end of weather
        else if(dataType="Road Traffic")
        {
            console.log("Data type is Road Traffic");

            // Formatting timeInterval
            console.log("raw timeInterval is: ", timeInterval);
            if(timeInterval == "Every 5 Minutes")
            {
                timeInterval = "5m";
            }
            else if(timeInterval == "Hourly")
            {
                timeInterval = "hour";
            }
            else if(timeInterval == "Daily")
            {
                timeInterval = "day";
            }
            else if(timeInterval == "Weekly")
            {
                timeInterval = "week";
            }
            else if(timeInterval == "Monthly")
            {
                timeInterval = "month";
            }
            else
            {
                console.log("Error here in traffic report submit.");
                return;
            }

            //Gran the start and end times from the datetime pickers
            
            var trafficDataObj = document.getElementById('roadTrafficDataSourceNames');
            var trafficDataType = trafficDataObj.options[trafficDataObj.selectedIndex].value;

            var baseTrafficURL = "";
            if(trafficDataType == "MTO")
            {
                baseTrafficURL = "/MTOTraffic";
            }else if (trafficDataType == "TomTom")
            {
                baseTrafficURL = "/TomTomTraffic";
            }

            var districtIndexObj = document.getElementById('roadTrafficDistrictNames');
            var districtIndex = districtIndexObj.options[districtIndexObj.selectedIndex].value;
            var selectedTrafficDistrict = (getPolyCoords(districtIndex));

            baseTrafficURL = baseTrafficURL + "?startDate=" + startDateTime + "&endDate=" + endDateTime + "&period=" + timeInterval;

            console.log("base url:" + baseTrafficURL);

            var data= {geo_points:selectedTrafficDistrict};
            var dataToSend = JSON.stringify(data);

            var trafficAggType = $('#aggTypeRT').val();

            function drawTrafficInfoChart() {
                $.ajax({
                    url: baseTrafficURL,
                    type: 'post',
                    dataType: 'json',
                    data: dataToSend,
                    success: function(data){
                        //console.log(data);
                        jsonOutput = data;

                        $("#outputJson").show();

                        var formattedValues = {};
                        formattedValues["packets"] = [];
                        lengthOfArray = data.length;

                        for(var i =0; i < lengthOfArray; i++)
                        {
                            formattedValues["packets"].push(data[i])
                        }

                        console.log(formattedValues);

                        var chartData = new google.visualization.DataTable();
                        var chart_div = document.getElementById('chart_div');

                        chartData.addColumn('datetime', 'Timestamp');
                        chartData.addColumn('number', 'speed(km/h)');

                        if(trafficAggType == "Maximum Speed")
                        {
                            formattedValues["packets"].forEach(function(packet){
                               
                                chartData.addRow([
                                    (new Date(packet.date*1000)),
                                    parseFloat(packet.max_curr_speed),
                                ]);
                            });

                            var options = {
                                title: trafficAggType,
                                hAxis: {
                                    title: 'Date & Time'
                                },
                                vAxis: {
                                    title: "Max Speed [km/h]"
                                },
                                legend: { position: 'bottom'},
                                height: 400,
                                bar: {groupWidth: "95%"}
                            };

                            var chart = new google.visualization.LineChart(chart_div);
                            // Show chart div
                            $("#chart_div").show(); 

                            google.visualization.events.addListener(chart, 'ready', function(){
                                chart_div.innerHTML = '<img src="' + chart.getImageURI() + '">';
                            });

                            chart.draw(chartData, options);

                            console.log("Max Speed");
   
                        }else if(trafficAggType == "Average Speed")
                        {
                            formattedValues["packets"].forEach(function(packet){
                               
                                chartData.addRow([
                                    (new Date(packet.date*1000)),
                                    parseFloat(packet.avg_curr_speed),
                                ]);
                            });

                            var options = {
                                title: trafficAggType,
                                hAxis: {
                                    title: 'Date & Time'
                                },
                                vAxis: {
                                    title: "Avg Speed [km/h]"
                                },
                                legend: { position: 'bottom'},
                                height: 400,
                                bar: {groupWidth: "95%"}
                            };

                            var chart = new google.visualization.LineChart(chart_div);
                            // Show chart div
                            $("#chart_div").show(); 

                            google.visualization.events.addListener(chart, 'ready', function(){
                                chart_div.innerHTML = '<img src="' + chart.getImageURI() + '">';
                            });

                            chart.draw(chartData, options);

                            console.log("Average Speed");

                        }else if (trafficAggType == "Minimum Speed")
                        {
                            formattedValues["packets"].forEach(function(packet){
                               
                                chartData.addRow([
                                    (new Date(packet.date*1000)),
                                    parseFloat(packet.min_curr_speed),
                                ]);
                                console.log(packet.date + ":" + packet.max_curr_speed);
                            });

                            var options = {
                                title: trafficAggType,
                                hAxis: {
                                    title: 'Date & Time'
                                },
                                vAxis: {
                                    title: "Min Speed [km/h]"
                                },
                                legend: { position: 'bottom'},
                                height: 400,
                                bar: {groupWidth: "95%"}
                            };

                            var chart = new google.visualization.LineChart(chart_div);

                            // Show chart div
                            $("#chart_div").show(); 

                            google.visualization.events.addListener(chart, 'ready', function(){
                                chart_div.innerHTML = '<img src="' + chart.getImageURI() + '">';
                            });

                            chart.draw(chartData, options);

                            console.log("Min Speed"); 
                        }else if (trafficAggType == "Maximum Freeflow-Speed Deviation")
                        {
                            formattedValues["packets"].forEach(function(packet){
                               
                                chartData.addRow([
                                    (new Date(packet.date*1000)),
                                    parseFloat(packet.max_delta_speed),
                                ]);
                            });

                            var options = {
                                title: trafficAggType,
                                hAxis: {
                                    title: 'Date & Time'
                                },
                                vAxis: {
                                    title: "Max Deviation [km/h]"
                                },
                                legend: { position: 'bottom'},
                                height: 400,
                                bar: {groupWidth: "95%"}
                            };

                            var chart = new google.visualization.LineChart(chart_div);

                            // Show chart div
                            $("#chart_div").show(); 

                            google.visualization.events.addListener(chart, 'ready', function(){
                                chart_div.innerHTML = '<img src="' + chart.getImageURI() + '">';
                            });

                            chart.draw(chartData, options);

                            console.log("Max Deviation");
                        }else if (trafficAggType == "Average Freeflow-Speed Deviation")
                        {
                            formattedValues["packets"].forEach(function(packet){
                               
                                chartData.addRow([
                                    (new Date(packet.date*1000)),
                                    parseFloat(packet.avg_delta_speed),
                                ]);
                                console.log(packet.date + ":" + packet.avg_delta_speed);
                            });

                            var options = {
                                title: trafficAggType,
                                hAxis: {
                                    title: 'Date & Time'
                                },
                                vAxis: {
                                    title: "Average Deviation [km/h]"
                                },
                                legend: { position: 'bottom'},
                                height: 400,
                                bar: {groupWidth: "95%"}
                            };

                            var chart = new google.visualization.LineChart(chart_div);

                            // Show chart div
                            $("#chart_div").show(); 

                            google.visualization.events.addListener(chart, 'ready', function(){
                                chart_div.innerHTML = '<img src="' + chart.getImageURI() + '">';
                            });

                            chart.draw(chartData, options);

                            console.log("Average Deviation");

                        }else if(trafficAggType == "Minimum Freeflow-Speed Deviation")
                        {
                            formattedValues["packets"].forEach(function(packet){
                               
                                chartData.addRow([
                                    (new Date(packet.date*1000)),
                                    parseFloat(packet.min_delta_speed),
                                ]);
                            });

                            var options = {
                                title: trafficAggType,
                                hAxis: {
                                    title: 'Date & Time'
                                },
                                vAxis: {
                                    title: "Min Deviation [km/h]"
                                },
                                legend: { position: 'bottom'},
                                height: 400,
                                bar: {groupWidth: "95%"}
                            };

                            var chart = new google.visualization.LineChart(chart_div);

                            // Show chart div
                            $("#chart_div").show(); 

                            google.visualization.events.addListener(chart, 'ready', function(){
                                chart_div.innerHTML = '<img src="' + chart.getImageURI() + '">';
                            });

                            chart.draw(chartData, options);

                            console.log("Min Deviation");
                        }else {
                            console.log("Unknown Agg type");
                        }

                        $('#myPleaseWait').modal('hide');
                    },error: function(data){
                        console.log("Error:" + data);
                    }
                });
            }

            google.charts.load('current', {'packages':['corechart']});
            google.charts.setOnLoadCallback(drawTrafficInfoChart);
        }
        else
        {
            locationName = $('#weatherLocationName').val();
            console.log("whats this??")
        }

        //$('#inputEcho .queryLine').empty();
        //$('#inputEcho .queryLine').append("?dataType=" + dataType + "?aggType=" + aggType + "?timeInterval=" + timeInterval + "&locationName=" + locationName + "&startDateTime=" + startDateTime + "&endDateTime=" + endDateTime);  

        //alert("completed!");

    });

//------------------------------------------------------------------------------------------------------------

});
