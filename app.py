#! /usr/bin/env python
'''SelectRenderMode demonstration code with background thread

Demonstrates use of "named transforms", objects which
use push/pop of the name-stack to report selection during
the rendermode.SelectRenderMode pass.

Background thread perturbs the object positions.
'''
from OpenGLContext import testingcontext
BaseContext, MainFunction = testingcontext.getInteractive(("glut",))
from OpenGLContext import drawcube, context, interactivecontext
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGLContext.arrays import *
import string, time, random, threading, random
from OpenGLContext.scenegraph import basenodes
from OpenGLContext import glutinteractivecontext
from OpenGLContext import trackball
from OpenGLContext.events.timer import Timer
from OpenGLContext.scenegraph.text import toolsfont, fontprovider, fontstyle3d
from OpenGLContext import displaylist

### Stuff For Wikipedia Image Import
import urllib2
import re
from BeautifulSoup import BeautifulSoup
from BeautifulSoup import SoupStrainer
import sys
import os

#for mysql
import MySQLdb
import gethistory

import math
import universe

## For speed optimization
import psyco
psyco.full()


#from OpenGLContext import trackball, quaternion

class TestContext( BaseContext ):
	def OnInit( self ):
		
		self.bigString = "A cactus (plural: cacti or cactuses) is any member of the spine plant family Cactaceae, native to the Americas. They are often used as ornamental plants, but some are also crop plants. Cacti are distinctive and unusual plants, which are adapted to extremely arid and hot environments, showing a wide range of anatomical and physiological features which conserve water. Their stems have expanded into green succulent structures containing the chlorophyll necessary for life and growth, while the leaves have become the spines for which cacti are so well known. Cacti come in a wide range of shapes and sizes. The tallest is Pachycereus pringlei, with a maximum recorded height of 19.2 m,[1] and the smallest is Blossfeldia liliputiana, only about 1 cm diameter at maturity.[2] Cactus flowers are large, and like the spines and branches arise from areoles. Many cactus species are night blooming, as they are pollinated by nocturnal insects or small animals, principally moths and bats. Cacti range in size from small and globular to tall and columnar."
		
		
		self.iter = 0
		self.strPos = 0
		self.newSystemTime = 300
		self.systemIterator = 0
		self.uniqueIDs = []
		
		glutReshapeWindow( 800, 600)
		glutPositionWindow( 0, 0 )
		
		self.time = Timer( duration = 60.0, repeating = 1 )
		self.time.addEventHandler( "fraction", self.OnTimerFraction )
		self.time.register (self)
		self.time.start ()
		
		#self.updater = Timer(duration = 61, repeating = 1)
		#self.updater.addEventHandler("cycle", self.updateFromSQL )
		#self.updater.register(self)
		#self.updater.start ()
		
		
		self.rot = 0
		
		self.offset = 3
		
		#dragging flag
		self.startDrag = 0
		
		#holder for last detail rendered planet
		self.lastDetail = ()
		
		
		#make some random planets and systems
		#self.universe = universe.Universe()
		
		#numSys = 10#random.random()*100
		#for s in range( int(numSys) ):
		#	self.universe.addSys( s )
		#	numPlan = 8#random.random()*100+1
		#	for p in range( int(numPlan) ):
		#		numMoons = random.random()*4+1
		#		self.universe.addPlanet( p,int(numMoons) )
				
				
		####	Starting SQL Integration Here
		self.universe = universe.Universe()
		numSys = 1
		self.universe.addSys(self.systemIterator)
		
		conn = MySQLdb.connect( host = "ec2-75-101-245-127.compute-1.amazonaws.com",
								user = "wikihole",
								passwd = "ohhai",
								db = "wikihole")
		self.stringArray = []
		cursor = conn.cursor()
		cursor.execute( "SELECT * FROM history")
		self.planetMoons = list();
		offsetset = 0
		while (1):
			row = cursor.fetchone()
			if row == None:
				break
			print "%s\t%s\t%s" % (row[0], row[2], row[1])	
			if(not offsetset):
				self.offset = row[0]
				offsetset = 1
				lastTime = "%s" % row[2]
				thisTime = "%s" % row[2]
			else:
				lastTime = thisTime
				thisTime = "%s" % row[2]
			
			if( not gethistory.timeDiff(lastTime, thisTime, self.newSystemTime) ):
				self.systemIterator = self.systemIterator + 1
				self.universe.addSys(self.systemIterator)
				print "MADE NEW SYSTEM"
				#print lastTime
				#print thisTime
			
			url = row[1]
			
			self.uniqueIDs.append(row[0])
			
			imageurls = gethistory.getImageUrls(url)
			self.universe.addPlanet(row[0], len(imageurls))
			names = url.split('/')
			wikititle = names[len(names) - 1]
			wikititle = wikititle.replace('_', ' ')
			self.stringArray.append(wikititle)
			
			
			fileList = list()
			for image in imageurls:
				linetoExec = "wget " + image
				
				fullpath = image.split('/')
				existsOrNot =  os.path.exists( fullpath[len(fullpath) - 1] )
				if(existsOrNot):
					fileList.append( fullpath[len(fullpath) - 1] )
				else:
					fileList.append( fullpath[len(fullpath) - 1] )
					os.system(linetoExec)  #uncomment this before real runs
				
			self.planetMoons.append(fileList)
			
			# send file list to moons
				

						
		"""Setup callbacks and build geometry for rendering"""
		#on mouse down
		self.addEventHandler( "mousebutton", button = 0, state=1, function = self.mouseDown )
		#on mouse up
		self.addEventHandler( "mousebutton", button = 0, state = 0, function = self.mouseUp )
				
		glutinteractivecontext.GLUTInteractiveContext.setupDefaultEventCallbacks(self)
		
		self.initialPosition = ( 0,0,20 )
		self.STEPDISTANCE = 5.0
		self.newPos = self.initialPosition
		self.goTo = 0
		
		#get fonts
		providers = fontprovider.getProviders( 'solid' )
		if not providers:
			raise ImportError( """NONONO solid font providers registered! Demo won't function properly!""" )
		registry = self.getTTFFiles()
		styles = []
		for font in registry.familyMembers( 'SANS' ):
			names = registry.fontMembers( font, 400, 0)
			for name in names:
				styles.append( fontstyle3d.FontStyle3D(
					family = [name],
					size = .06,
					justify = "LEFT",
					thickness = .02,
					quality = 3,
					renderSides = 1,
					renderFront = 1,
					renderBack = 1,
				))
		self.styles = styles
				
		#r = threading.Thread( target = self.randomiser )
		#r.setDaemon(1)
		#r.start()
		

	def OnIdle( self, ):
		if self.goTo:
			self.tweenCam()
		self.triggerRedraw(1)
		return 1
		
	def getSceneGraph( self ):
		return self.universe.uni
		
	def glutOnMouseMove(self, x, y):
		if self.startDrag == 1:
			trackP,trackQ = self.track.update( x,y )
			print "p: ",trackP
			print "q: ",trackQ
			self.platform.setPosition( trackP )
			self.platform.setOrientation( trackQ )
			
	def mouseDown( self, event ):
		#make trackball
		x,y  = event.getPickPoint()
		print "track centerY: ", self.newPos[1]
		self.track = trackball.Trackball( position=self.platform.position, quaternion=self.platform.quaternion, center=(self.newPos[0],self.newPos[1],self.newPos[2]-2), originalX=x, originalY=y, width=800, height=600 )
		self.startDrag = 1
		
	def mouseUp( self, event ):
		"""Handle a mouse-click in our window.
		Retrieves the "pick point", and the unprojected (world-space) coordinates
		of the clicked geometry (if a named object was clicked).
		"""
		
		self.startDrag = 0
		self.track.cancel()
		
		x,y  = event.getPickPoint()
		print 'Click', (x,y)
		
		
		print '  %s objects:'%( len(event.getObjectPaths()))
		for path in event.getObjectPaths():
			#find planet
			foundPlanet = self.universe.findPlanet( path )
			#find solarsys
			foundSys = self.universe.findSys( path )
			
			
			if foundPlanet and foundSys:
				print "found planet:",foundPlanet.name, "in sys:", foundSys.name
				#if there is one rendered detailed... put the simple back in
				if self.lastDetail:
					self.universe.unRenderDetail( self.lastDetail )
				#print self.planetMoons
				#render font geom
				geom = []
				gNum = 0
				while gNum<240:
					tmpGeom = basenodes.Text( fontStyle=self.styles[0], string=self.bigString[ gNum ] )
					geom.append( tmpGeom )
					gNum += 1
					print "rendred a: ", self.bigString[ gNum ]
				
				#self.geometry = basenodes.Text( fontStyle=self.styles[0], string=self.stringArray[ foundPlanet.name - self.offset] )
				#self.strPos += 1
					
				#render the new one detailed
				
				self.lastDetail = foundPlanet
				self.universe.renderDetail( foundPlanet, geom , self.planetMoons[foundPlanet.name - self.offset] )
				
				#calc the new point in global space
				summedTrans =  foundPlanet.translation + foundSys.translation
				self.newPos = ( summedTrans[0], summedTrans[1], summedTrans[2]+2 )
				self.goTo = 1
								
								
	def OnClick2( self, event ):
		"""Handle mouse click for a given name/id"""
		print "You clicked on the magic sphere!"
		self.OnClick1( event )


	def setupFontProviders( self ):
		"""Load font providers for the context

		See the OpenGLContext.scenegraph.text package for the
		available font providers.
		"""
		fontprovider.setTTFRegistry(
			self.getTTFFiles(),
		)
	
	def randomiser( self ):
		while self:
			self.lockScenegraph()
			try:
				#rotate all the planets
				#self.universe.rotatePlanets( self.rot )
				self.rot += 0.05
			finally:
				self.unlockScenegraph()
			if self:
				self.triggerRedraw(1)
			time.sleep( .05 )	
			
	def OnTimerFraction( self, event ):
		self.universe.rotatePlanets( -60*event.fraction() )
		self.iter = self.iter + 1
		#print "awesome! %d" % self.iter
		if(self.iter > 200):  
			self.updateFromSQL()
			self.iter = 0
		
	def tweenCam( self ):
		speed = 0.1
		#move to newPos
		deltaVector = ( self.newPos[0]-self.platform.position[0] , self.newPos[1]-self.platform.position[1], self.newPos[2]-self.platform.position[2] )
		deltaInc = ( deltaVector[0]*speed,deltaVector[1]*speed,deltaVector[2]*speed )
		self.platform.moveRelative( x=deltaInc[0],y=deltaInc[1],z=deltaInc[2] )
	
		#look at newPos
		#set orientation back to initial default 
		self.platform.setOrientation( (0,1,0,0) )
		#calc dela ang about y axis
		dx = self.platform.position[0] - self.newPos[0]
		dy = self.platform.position[1] - self.newPos[1]
		dz = self.platform.position[2] - self.newPos[2]
		#compute axis rotation angles
		yAng = math.atan( dx/dz )
		xAng = math.atan( dy/dz )
		#apply turn on y axis
		self.platform.turn( (0,1,0,yAng*speed) )
		#apply turn to x axis
		self.platform.turn( (1,0,0,-xAng*speed) )
		
		avgDist = math.fabs(deltaInc[0]+deltaInc[1]+deltaInc[2])/3
		if( avgDist < 0.001 ):
			self.goTo = 0
			
	def updateFromSQL(self):
		print "ACTUALLY CALLED updateFromSQL!!! wohoo!!!\n"
		largestRecord = -12
		for ident in self.uniqueIDs:
			if(ident > largestRecord):
				largestRecord = ident
		
		
		conn = MySQLdb.connect( host = "ec2-75-101-245-127.compute-1.amazonaws.com",
								user = "wikihole",
								passwd = "ohhai",
								db = "wikihole")
								
		cursor = conn.cursor()
		cursor.execute("SELECT * FROM history WHERE id = %d" % largestRecord)
		row = cursor.fetchone()
		lastHighest = "%s" % row[2]
		
		
		cursor = conn.cursor()
		cursor.execute( "SELECT * FROM history WHERE id > %d" % largestRecord)
		
		print "checking for records larger than %d" % largestRecord
		first = 1
		while (1):
			row = cursor.fetchone()
			if row == None:
				break
			print "%s\t%s\t%s" % (row[0], row[2], row[1])	
			if(first):
				lastTime = lastHighest
				thisTime = "%s" % row[2]
				first = 0
			else:
				lastTime = thisTime
				thisTime = "%s" % row[2]

			if( not gethistory.timeDiff(lastTime, thisTime, self.newSystemTime) ):
				self.systemIterator = self.systemIterator + 1
				self.universe.addSys(self.systemIterator)
				print "MADE NEW SYSTEM"
				#print lastTime
				#print thisTime
			url = row[1]
			self.uniqueIDs.append(row[0])
			imageurls = gethistory.getImageUrls(url)
			self.universe.addPlanet(row[0], len(imageurls))
			names = url.split('/')
			wikititle = names[len(names) - 1]
			wikititle = wikititle.replace('_', ' ')
			self.stringArray.append(wikititle)
			
			
			fileList = list()
			#do this stuff in a thread
			for image in imageurls:
				linetoExec = "wget " + image
				fullpath = image.split('/')
				fileList.append( fullpath[len(fullpath) - 1] )
				os.system(linetoExec)  #uncomment this before real runs
				
			self.planetMoons.append(fileList)

if __name__ == "__main__":
	MainFunction ( TestContext)
