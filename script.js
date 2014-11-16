var query = '';
var counter = 0;

var map;

var heatmap;

var data;

function update_heatmap(newLatLng){
  data.push(newLatLng);
}

function set_heatmap(data, map){

  var sanFrancisco = new google.maps.LatLng(37.774546, -122.433523);

  heatmap = new google.maps.visualization.HeatmapLayer({
    data: heatmapData,
    gradient: ["#060990", "#4400ff", "#ff0000", "#f2aaaa"],
    radius: 5
  });
  heatmap.setMap(map);

}

function set_map(map){
  var sanFrancisco = new google.maps.LatLng(37.774546, -122.433523);

  map = new google.maps.Map(document.getElementById('map'), {
    center: sanFrancisco,
    zoom: 13,
    mapTypeId: google.maps.MapTypeId.SATELLITE
  });
}

function scroll_to_div()
{
	$('html, body').animate({
    scrollTop: $("#anchor").offset().top
 	});
}

function apply_updates(){
	$.getJSON("twitter_query.php",{"q":query},
		function(data) {
		console.log(data);
		/*for (dp in data)
		{
			console.log(dp);
		}*/
  });
}

function send_query(q)
{
	query = q
	timer_fired();
}

function timer_fired()
{
	if (counter == 5)
		return;
	setTimeout(
		function(){ 
			counter+=1;
			apply_updates();
			timer_fired();
		}
		,1000);
}


$( document ).ready(function() {
  data = [
    new google.maps.LatLng(37.782, -122.447),
    new google.maps.LatLng(37.782, -122.445),
    new google.maps.LatLng(37.782, -122.443),
    new google.maps.LatLng(37.782, -122.441),
    new google.maps.LatLng(37.782, -122.439),
    new google.maps.LatLng(37.782, -122.437),
    new google.maps.LatLng(37.782, -122.435),
    new google.maps.LatLng(37.785, -122.447),
    new google.maps.LatLng(37.785, -122.445),
    new google.maps.LatLng(37.785, -122.443),
    new google.maps.LatLng(37.785, -122.441),
    new google.maps.LatLng(37.785, -122.439),
    new google.maps.LatLng(37.785, -122.437),
    new google.maps.LatLng(37.785, -122.435)
  ];

  var sanFrancisco = new google.maps.LatLng(37.774546, -122.433523);
  map = new google.maps.Map(document.getElementById('map'), {
    center: sanFrancisco,
    zoom: 13
  });

  set_heatmap(data, map);

  $('#submit').click(function(){
  		var val = $('#query_text').val();
  		if (val != '')
  		{
  			send_query();
			scroll_to_div();
  		}
	});
});


