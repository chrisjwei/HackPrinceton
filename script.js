var query = '';
var counter = 0;

var map;

var heatmap;

var data = new google.maps.MVCArray();

function update_heatmap(newLatLng){
  data.push(newLatLng);
  if(data.length > 50){
    data[0]= null;
    data.push(newLatLng);
    data.shift();
  }
  else if(data.length === 1){ //activates when data = []
    set_heatmap(data, map);
  }
}

function set_heatmap(heatdata, map){

  var sanFrancisco = new google.maps.LatLng(37.774546, -122.433523);

  heatmap = new google.maps.visualization.HeatmapLayer({
    data: heatdata,
    //gradient: ["#060990", "#4400ff", "#ff0000", "#f2aaaa"],
    radius: 10,
  });
  heatmap.setMap(map);

}

function set_map(){

  var sanFran = new google.maps.LatLng(50, -70);

  /*map = new google.maps.Map(document.getElementById('map'), {
    center: sanFran,
    zoom: 8,
    mapTypeId: google.maps.MapTypeId.SATELLITE
  });*/
  data.push(new google.maps.LatLng(50, -100));
  //set_heatmap(data, map);
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

  //defaults
  var USA = new google.maps.LatLng(39.5, -98.35);
  map = new google.maps.Map(document.getElementById('map'), {
    center: USA,
    zoom: 4
  });
  data = [new google.maps.LatLng(50, -80)];
  set_heatmap(data, map)

  $('#submit').click(function(){
  		var val = $('#query_text').val();
  		if (val != '')
  		{
  			send_query();
			scroll_to_div();
  		}
	});
});


