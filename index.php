<html>
<document>
<header>
<title>Data is Beautiful</title>
  <link href='http://fonts.googleapis.com/css?family=Open+Sans:300,400,600,700' rel='stylesheet' type='text/css'>
  <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js"></script>
  <script type="text/javascript" src="https://maps.googleapis.com/maps/api/js?sensor=false"></script>
  <script type="text/javascript" src="https://www.google.com/jsapi"> </script>
  <script type="text/javascript" src="hackPrinceton-heatmap.js"></script>
  <script type="text/javascript" src="hackPrinceton-gmaps-heatmap.js"></script>
  <script type="text/javascript" src="script.js"></script>  
  <link rel="stylesheet" type="text/css" href="stylesheet.css">
</header>
<body style=background-color:#F9F9F9;>
<div class = "header">
	<div class = "header_content">
	<a href = "index.php"><img src="heat_tweet_logo.svg" style ="width:203px;height:46px;position:relative;top:15px"></a>
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
	<div class="divtitle"> Tweets around the World </div>
		<div id="map" style="height: 540px; width: 790px;float:left;clear:both;"></div>
		<div id="tweets">
			<ul id="results">
			<li>@creeswei</li>
			<li><hr></li>
			<li>@basedgod</li>
			<li><hr></li>
			<li>@yungmoney</li>
			<li><hr></li>
			<li>@elonmusk</li>
			<li><hr></li>
			<li>@dj_lean</li>
			<li><hr></li>
			<li>@barney</li>
			<li><hr></li>
			<li>@not_ur_mom</li>
			<li><hr></li>
			<li>@ZZZZZZZZZZZZZZZ</li>
			<li><hr></li>
			<li>@john</li>
			<li><hr></li>
			<li>@gunther</li>
			<li><hr></li>
			<li>@davinci</li>
			<li><hr></li>
			<li>@paul</li>
			<li><hr></li>
			<li>@farnsworth</li>
			</ul>
		</div>
	</div>
	</div>
	<div id = "footer"></div>	

</body>
</document>
</html>