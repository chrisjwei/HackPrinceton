var query = '';
var counter = 0;

function scroll_to_div()
{
	$('html, body').animate({
    scrollTop: $("#anchor").offset().top
 	});
}
function make_map(){
    // copy-paste this tag: <script type="text/javascript" src="https://maps.googleapis.com/maps/api/js?sensor=false"></script>
    // map center

    var myLatlng = new google.maps.LatLng(25.6586, -80.3568);
    // map options,
    var myOptions = {
          zoom: 4,
          center: myLatlng,
          panControl: false,
          zoomControl: false,
          scaleControl: true
    };
        // standard map
    map = new google.maps.Map(document.getElementById("map"), myOptions);
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
  make_map();
  $('#submit').click(function(){
  		var val = $('#query_text').val();
  		if (val != '')
  		{
  			send_query();
			scroll_to_div();
  		}
	});
});