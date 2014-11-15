function scroll_to_div()
{
	$('html, body').animate({
    scrollTop: $("#anchor").offset().top
 	});
}