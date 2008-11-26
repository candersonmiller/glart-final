#!/usr/bin/python

import MySQLdb
import sys
import os
import urllib2
import re
from BeautifulSoup import BeautifulSoup
from BeautifulSoup import SoupStrainer


def getImageUrls(url):
	request = urllib2.Request(url)
	request.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5; en-US; rv:1.9.0.4) Gecko/2008102920 Firefox/3.0.4')
	opener = urllib2.build_opener()
	feeddata = opener.open(request).read()
	soup = BeautifulSoup(''.join(feeddata))
	soup.prettify()
	images = soup.findAll('img')
	imageurls = list()
	for image in images:
		imageurl = image['src']
		if( not (imageurl.count('magnify-clip') or imageurl.count('wikimedia-button') or imageurl.count('Commons-logo') or imageurl.count('Status_iucn') or imageurl.count('red_question_mark') or imageurl.count('Wikispecies') or imageurl.count('poweredby_mediawiki'))):
			imageurls.append(imageurl)
	return imageurls

def main():
	conn = MySQLdb.connect( host = "ec2-75-101-245-127.compute-1.amazonaws.com",
							user = "wikihole",
							passwd = "ohhai",
							db = "wikihole")
	cursor = conn.cursor()
	cursor.execute( "SELECT * FROM history")
	while (1):
		row = cursor.fetchone()
		if row == None:
			break
		print "%s\t%s\t%s" % (row[0], row[2], row[1])	
		
		url = row[1]
		imageurls = getImageUrls(url)
		for imageurl in imageurls:
			print imageurl
		
	
if __name__ == '__main__':
	main()
