// SOURCE : http://collaboradev.com/2011/04/01/twitter-oauth-php-tutorial/


// Storing OAuth header in an array
$nonce = time();
$timestamp = time();
$oauth = array('oauth_callback' => 'http://facebook.com/rao.ariel',
              'oauth_consumer_key' => 'owKiK84O9Ui3q7KYAJzTrRETx',
              'oauth_nonce' => $nonce,
              'oauth_signature_method' => 'HMAC-SHA1',
              'oauth_timestamp' => $timestamp,
              'oauth_version' => '1.0');


/**
 * Method for creating a base string from an array and base URI.
 * @param string $baseURI the URI of the request to twitter
 * @param array $params the OAuth associative array
 * @return string the encoded base string
**/
function buildBaseString($baseURI, $params){
 
$r = array(); //temporary array
    ksort($params); //sort params alphabetically by keys
    foreach($params as $key=>$value){
        $r[] = "$key=" . rawurlencode($value); //create key=value strings
    }//end foreach                
 
    return 'POST&' . rawurlencode($baseURI) . '&' . rawurlencode(implode('&', $r)); //return complete base string
}//end buildBaseString()

$baseString = buildBaseString($baseURI, $oauth);