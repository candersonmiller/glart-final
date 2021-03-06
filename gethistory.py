#!/usr/bin/python

import MySQLdb
import time
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
	opener.close()
	request.close()
	soup = BeautifulSoup(''.join(feeddata))  #make it into beautifulsoup
	soup.prettify() #correct errors
	images = soup.findAll('img') #search for images
	imageurls = list()  #keep list of image urls
	for image in images:
		imageurl = image['src']  #search for image sources
		if( not (imageurl.count('magnify-clip') or imageurl.count('Wikinews-logo') or imageurl.count('wikimedia-button') or imageurl.count('Wiktionary') or imageurl.count('Padlock-olive') or imageurl.count('Question_book') or imageurl.count('Commons-logo') or imageurl.count('Status_iucn') or imageurl.count('red_question_mark') or imageurl.count('Wikispecies') or imageurl.count('poweredby_mediawiki'))):
			#filter out wikimedia images
			imageurls.append(imageurl)
	return imageurls


def getDescription(url):
	sizeToReturn = 200
	
	request = urllib2.Request(url) #create a request
	request.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5; en-US; rv:1.9.0.4) Gecko/2008102920 Firefox/3.0.4')  #http://whatsmyuseragent.com/
	opener = urllib2.build_opener()
	feeddata = opener.open(request).read() #feeddata is the html data received
	opener.close()
	request.close()
	soup = BeautifulSoup(''.join(feeddata))  #make it into beautifulsoup
	soup.prettify() #correct errors
	paras = soup.findAll('p')
	
	
	
	i = 0
	text = ''
	for pa in paras:
		for res in pa.findAll(text=True):
			if(i > 2):
				text = text + res
		i = i + 1
	
	
	textToReturn = text.replace('\n','  ')
	
	if(len(textToReturn) < sizeToReturn):
		while(len(textToReturn) < sizeToReturn):
			textToReturn = textToReturn + "    "
		return textToReturn[0:sizeToReturn]
	else:
		return textToReturn[0:sizeToReturn]


	

## send SQL formatted time 1, SQL formatted time 2, and if they are greater than N seconds apart, it will return false, else it will return false
def timeDiff(time1, time2, secondsApart):

	dateAndTime = time1.split(' ')
	date1 = dateAndTime[0]
	yearMonDay = date1.split('-')
	time1 = dateAndTime[1]
	hourMinSec = time1.split(':')

	year = int(yearMonDay[0])
	month = int(yearMonDay[1])
	day = int(yearMonDay[2])
	hour = int(hourMinSec[0])
	minute = int(hourMinSec[1])
	second = int(hourMinSec[2])
	
	first = datetime.datetime(year,month,day,hour,minute,second)
	
	dateAndTime2 = time2.split(' ')
	date2 = dateAndTime2[0]
	yearMonDay2 = date2.split('-')
	time2 = dateAndTime2[1]
	hourMinSec2 = time2.split(':')

	year2 = int(yearMonDay2[0])
	month2 = int(yearMonDay2[1])
	day2 = int(yearMonDay2[2])
	hour2 = int(hourMinSec2[0])
	minute2 = int(hourMinSec2[1])
	second2 = int(hourMinSec2[2])
	
	second = datetime.datetime(year2,month2,day2,hour2,minute2,second2)
	#(  	[days[, seconds[, microseconds[, milliseconds[, minutes[, hours[, weeks]]]]]]])
	
	#print (second - first)
	correctDiff = datetime.timedelta(0, secondsApart, 0, 0 , 0 , 0, 0)
	#print correctDiff
 	if ( (second - first) > correctDiff ):
		return 0
	else:
		return 1
	

def main():
	conn = MySQLdb.connect( host = "ec2-75-101-245-127.compute-1.amazonaws.com",
							user = "wikihole",
							passwd = "ohhai",
							db = "wikihole")
	cursor = conn.cursor()
	cursor.execute( "SELECT * FROM history")
	prevTime = "1984-04-16 02:01:02"
	currTime = "1984-04-16 02:01:02"
	first = 1
	while (1):
		row = cursor.fetchone()
		if row == None:
			break
		print "%s\t%s\t%s" % (row[0], row[2], row[1])	
		if(first):
			currTime = "%s" % row[2]
			prevTime = "%s" % row[2]
			first = 0
		
		prevTime = currTime
		currTime = "%s" % row[2]
		if( timeDiff(prevTime, currTime, 45) ):
			print 'Consecutive'
		else:
			print "NONCONSECUTIVE"
		url = row[1]
		imageurls = getImageUrls(url)
		#for imageurl in imageurls:
		#	print imageurl
		
	
if __name__ == '__main__':
	main()
