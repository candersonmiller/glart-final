<HTML>
<H1>Feed This To WikiHole</H1>
<?php
	function wikipediaParser($url){
		$website = file_get_contents($url);
		$siteParts = split('This page was last modified on',$website);
		$lastMod = split('</li>',$siteParts[1]);
		#<li id="lastmod"> This page was last modified on 19 June 2008, at 10:45.</li>
		$lastDate = split(', ',$lastMod[0]);
		return $lastDate[0];
	}

	$url = $_GET["url"];
	$title = $_GET["title"];
	print "<b>Page URL:</b> $url\n";
	print "<br><br>\n";
	print "<b>Page Title: </b>$title\n";
	print "<br><br>";
	$today = date('l F jS  Y \a\t h:i:s A');
	print "<b>Date Accessed: </b> $today";
	print "<BR><BR>\n";
	print "<b>Your Username: </b> input when you generate the bookmarklet (need to be logged in to do so)";
	print "<BR><BR>\n";
	
	if(strpos($url,'amazon.com') !== false and (strpos($url,'dp') !== false or strpos($url,'product') !== false)){
		$pageData = amazonParser($url);
		$isbn10 = $pageData[0];
		$isbn13 = $pageData[1];
		$publisher = $pageData[2];
		$author = $pageData[3];
		$title = $pageData[4];
		print "<b>ISBN 10: </b> $isbn10<br><br>\n";
		print "<b>ISBN 13: </b> $isbn13<br><br>\n";				
		print "<b>Publisher: </b> $publisher<br><br>\n";
		print "<b>Author: </b> $author<br><br>\n";
		print "<b>Title: </b> $title<br><br>\n";
	}
	
	if(strpos($url,'.wikipedia.org') !== false){
		$lastMod = wikipediaParser($url);
		$titleParts = split(' - ',$title);
		print "<b>Site Title: </b>$titleParts[1]<br><br>\n";
		print "<b>Page Title: </b>$titleParts[0]<br><br>\n";
		print "<b>Site last updated on:</b> $lastMod<br><br>\n";
	}
	
	#$website = file_get_contents("http://www.robotchef.tv/cgi-bin/test.pl");
	
	
?>
	<form action="javascript: self.close ()">
	<INPUT type="submit" name="mysubmit" value="Close!">
	</form>
</HTML>