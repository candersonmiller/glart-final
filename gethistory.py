#!/usr/bin/python

import MySQLdb
import sys
import os
import urllib2
import re
from BeautifulSoup import BeautifulSoup
from BeautifulSoup import SoupStrainer


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
		
		#url = row[1]
		#page = urllib2.urlopen(url)
		#pageString = page.read()
		#soup = BeautifulSoup(''.join(pageString))
		#soup.renderContents()
		#soup.prettify()
	
if __name__ == '__main__':
	main()
