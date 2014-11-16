<!--DOCTYPE html-->
<html>
<document>
<header>
<title>Data is Beautiful</title>
  <link href='http://fonts.googleapis.com/css?family=Open+Sans:300,400,600,700' rel='stylesheet' type='text/css'>
  <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js"></script>
  <script type="text/javascript" src="https://www.google.com/jsapi"> </script>
  <script type="text/javascript"
  src="https://maps.googleapis.com/maps/api/js?libraries=visualization&sensor=true_or_false">
	</script>
  <script type="text/javascript">
	</script>
  <script type="text/javascript" src="min.js"></script> 
  <link rel="stylesheet" type="text/css" href="stylesheet.css">
  <link rel="icon" type="image/ico" href="favicon.ico">
</header>
<body style=background-color:#F9F9F9;>
<div class = "header">
	<div class = "header_content">
	<a href = "index.php"><img src="heat_tweet_logo.svg" style ="width:203px;height:30px;position:relative;top:25px"></a>
	</div>
</div>
	<div class="hline"></div>
	<div class = "main">
		<div class = "jumbo">
			<div class = "jumbo_inner">
			View tweets<br>
			From around the world <br>
			In real time <br>
			<input id = "query_text" type="text" name="SearchQuery" placeholder="ex. #twerking">
			<input id = "submit" type="submit" value="Search">
			</div>
		</div>
	<div class="buffer"></div>
	<div id="anchor"></div> <!--Jump here after submit -->
	</div>
	<div class="hline" style="background-color:#eaeaea"></div>
	<div class = "drop_shadow">
	<div class = "main">
	<div style = "height:30px;margin-top:20px">
		<div style="position:inline-block; float:left;">Twitter feed across the world, filtering by &nbsp;</div>
		<div id="search_term" style="position:inline-block; float:left;">NONE</div>
	</div>
		<div id="map" style="height: 540px; width: 790px;float:left;clear:both;"></div>
		<div id="tweets">
			<ul id="results">
			</ul>
		</div>
	</div>
	</div>
	<div id = "footer">
	<div class = "main">
		<br>
		<div style="color:white;font-size:12px;font-weight:800;padding-top:15px;padding-bottom:5px">
		Created by...
		</div>
		<div id="credits">
		<ul style="font-weight:200">
			<li>Christopher Wei</li>
			<li>Shreya Gupta</li>
			<li>Richard Chiang</li>
			<li>Ariel Rao</li>
			<li>Anatol Liu</li>
		</ul>
		<ul style="color:#91e8fb">
			<li><a href="https://twitter.com/creeswei">@creeswei</a></li>
			<li><a href="https://twitter.com/omgitsshreya">@omgitsshreya</a></li>
			<li><a href="https://twitter.com/richardchiang2">@richardchiang2</a></li>
			<li><a href="https://twitter.com/raoariel">@raoariel</a></li>
			<li><a href="https://twitter.com/liuanatol">@liuanatol</a></li>
		</ul>
		</div>
	</div>
	</div>	

</body>
</document>
</html>
