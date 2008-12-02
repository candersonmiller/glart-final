#!/usr/bin/python

import MySQLdb
import datetime
import sys
import os
import urllib2
import re
from BeautifulSoup import BeautifulSoup
from BeautifulSoup import SoupStrainer


def getImageUrls(url):
	request = urllib2.Request(url) #create a request
	request.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5; en-US; rv:1.9.0.4) Gecko/2008102920 Firefox/3.0.4')  #http://whatsmyuseragent.com/
	opener = urllib2.build_opener()
	feeddata = opener.open(request).read() #feeddata is the html data received
	soup = BeautifulSoup(''.join(feeddata))  #make it into beautifulsoup
	soup.prettify() #correct errors
	images = soup.findAll('img') #search for images
	imageurls = list()  #keep list of image urls
	for image in images:
		imageurl = image['src']  #search for image sources
		if( not (imageurl.count('magnify-clip') or imageurl.count('wikimedia-button') or imageurl.count('Commons-logo') or imageurl.count('Status_iucn') or imageurl.count('red_question_mark') or imageurl.count('Wikispecies') or imageurl.count('poweredby_mediawiki'))):
			#filter out wikimedia images
			imageurls.append(imageurl)
	return imageurls


def timeDiff(time1, time2):
	print fromtimestamp(time1)
	print time2
	

def main():
	conn = MySQLdb.connect( host = "ec2-75-101-245-127.compute-1.amazonaws.com",
							user = "wikihole",
							passwd = "ohhai",
							db = "wikihole")
	cursor = conn.cursor()
	cursor.execute( "SELECT * FROM history")
	prevTime = "1984-04-16 02:01:02"
	currTime = "1984-04-16 02:01:02"
	while (1):
		row = cursor.fetchone()
		if row == None:
			break
		print "%s\t%s\t%s" % (row[0], row[2], row[1])	
		prevTime = currTime
		currTime = "%s" % row[2]
		timeDiff(prevTime, currTime)
		url = row[1]
		imageurls = getImageUrls(url)
		for imageurl in imageurls:
			print imageurl
		
	
if __name__ == '__main__':
	main()
