var query = '';
var counter = 0;
var users = [];
var map;
var heatmap;
var data = new google.maps.MVCArray();

function update_people(usrArr){
  var results = document.getElementById("results")
  $(results).empty();
  if (usrArr === []) { return; }
  for (var i = usrArr.length-1; i >= 0; i--) {
    $(results).append('<li>@'+usrArr[i]+'</li>');
    $(results).append('<li><hr></li>'); 
  }
}

function update_heatmap(newLatLng){
  data.push(newLatLng);
  if(data.getLength() > 1000){
    data.removeAt(0);
  }
  else if(data.getLength() === 1){ //activates when data = []
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

var ws = new WebSocket('wss://' + location.hostname);
var map, markers = [];
var currentLocation;
var play = true;
var censor = window.location.search.indexOf("censor=false") > -1;
//var infoWindow = new google.maps.InfoWindow();

// Socket open event
ws.onopen = function () {
    console.log('Socket connection established.');
}

// Socket message
ws.onmessage = function (message) {
    handleTweet(message);
}

// Log errors
ws.onerror = function (error) {
    console.log('WebSocket Error ' + error);
};

// Socket close event
ws.onclose = function () {
    console.log('Socket connection interrupted.');
}

// Handle tweet
function handleTweet(message) {
    // pass in query
    if (play) {
        var tweet = JSON.parse(message.data);
        var keyword = query;
        //var keyword = query;
        // pizza, yolo, :), omg, hella, mad
        var text = tweet.text.toLowerCase();
        if (text.toLowerCase().indexOf(keyword) == -1) { return; }
        var geo = tweet.coordinates;
        console.log(text);
        
        // Check if the geo type is a Point (it can also be a Polygon).
        if (geo && geo.type === 'Point') {
            var lat_lon = new google.maps.LatLng(geo.coordinates[1], geo.coordinates[0]);

            users.push(tweet.user.screen_name);
            if (users.length > 13) {
                    users.shift();
            }
        }
        update_heatmap(lat_lon);
	update_people(users);
    }
}


// Callback function when the geolocation is retrieved.
function geolocationSuccess(position) {
    if (currentLocation) {
        return;
    }

    currentLocation = position;
    var longitude = position.coords.longitude;
    var latitude = position.coords.latitude;

    // Position the map.
    var centerPosition = new google.maps.LatLng(latitude, longitude);

    map.setCenter(centerPosition);
}

// Callback function when the geolocation is not supported.
function geolocationError() {
    // Center and show the US
    var centerPosition = new google.maps.LatLng(39.159, -100.518);
    map.setCenter(centerPosition);
    map.setZoom(4);
}

function scroll_to_div()
{
	$('html, body').animate({
    scrollTop: $("#anchor").offset().top
 	});
}

$( document ).ready(function() {
  //defaults
  var USA = new google.maps.LatLng(39.5, -98.35);
  map = new google.maps.Map(document.getElementById('map'), {
    center: USA,
    zoom: 4
  });
  
  set_heatmap(data, map);

  $('#submit').click(function(){
    var val = $('#query_text').val();
    if (val != '')
    {
      query = val;
      map = new google.maps.Map(document.getElementById('map'), {
                                center: USA,
                                zoom: 4
                                });
      data = new google.maps.MVCArray();
      set_heatmap(data, map);
      document.getElementById("search_term").innerHTML = query
      scroll_to_div();
    }
  });
});

