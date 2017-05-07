/* 
*** Maps to initialize on start. 
*** Called from google maps as callback
*/

function initMap() 
{
	console.log("In allMapsInit");
	//Initialize ttc heatmap. Called later after getting current TTC data first
	//initTTCHeatMap();

	//Initialize weather aggregation map
	initWeatherMap();	

	//Initialize ttc polygon map
	initTTCPolygonMap();

	//drawRoadsDataonMap();
	//initTrafficMap();
}
