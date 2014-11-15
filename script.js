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
    console.log(map);
}

$( document ).ready(function() {
  make_map();
});