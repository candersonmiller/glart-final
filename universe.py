#! /usr/bin/env python
from OpenGLContext.scenegraph import *
import math, random
from time import time

from OpenGLContext import displaylist
from OpenGLContext.scenegraph.text import toolsfont
from OpenGLContext.scenegraph import imagetexture

import PIL
from PIL import Image


class Universe( object ):
	

	
	def __init__( self ):
		#create scene graph (universe)
		self.uni = basenodes.sceneGraph()
		#create one child for the universe... a galaxy
		tmpGalaxy = []
		t = basenodes.Transform(
			translation = (0,0,0),
			children = [],
			)
		t.name = "galaxy01"			
		tmpGalaxy.append(t)
		self.uni.children = tmpGalaxy #now one galaxy added to the universe... access it via self.uni.children[0]		
				
		
	def addSys( self, name ):
		"""adds solar system (session) to scenegraph"""		
		coords = []
		#transform to hold connect line
		l = basenodes.Transform(
			children = [
				basenodes.Shape(
					geometry = basenodes.IndexedLineSet(	
						coord = basenodes.Coordinate(
							point = coords,
						),
						coordIndex = range( len(coords)),
					),
					appearance = basenodes.Appearance(
						material = basenodes.Material( emissiveColor = (0.5,0.5,0.5) ),
					),
				),
			],
		)
		l.name = "line"
		#transform to hold solar system
		p = random.random()*44-22, random.random()*12-6, random.random()*44-22 #position
		r = random.random()*math.radians(180) #rotation
		t = basenodes.Transform(
			translation = p,
			children = [ l ],
		)
		t.name = name
		t.sensititive = 0
		#add solar system to galaxy
		tmpHolder = self.uni.children[0].children
		tmpHolder.append(t)
		self.uni.children[0].children = tmpHolder
		
		
	def addPlanet( self, name, moonsNum, title, geom, urls ):
		"""adds planet (webpage) to last solar system"""
		#make moon children transform
		moonChildren = []
		for m in range( moonsNum ):
			#make the translation Transform for the moon and add it to the rotation Transform
			orbitD = random.random()*.5+.2
			mTrans = basenodes.Transform(
				translation = ( orbitD,0,0 ),
				rotation = ( 0,0,0,0 ),
				children = [
					basenodes.Shape(
						geometry = basenodes.Box( size = ( 0.01,0.2,0.2) ),
						appearance = basenodes.Appearance(
							material = basenodes.Material( emissiveColor = (.8,.8,.8) ),
						),
					),
				],
			)
			#make the rotation Transforms for the moon
			mRatio = random.random()*0.5
			mRotY = basenodes.Transform(
				translation = (0,0,0 ),
				rotation = (0,1,0,0),
				children = [ mTrans ],
			)
			mr = random.random()*math.radians(360) #rotation
			mRotX = basenodes.Transform(
				translation = (0,0,0 ),
				rotation = (mRatio,0,0,mr),
				children = [ mRotY ],
			)
			speedMultiplyer = random.random()*2.5+0.5
			mRotX.name = speedMultiplyer
			moonChildren.append( mRotX )
			
		#make moons Transform
		moons = basenodes.Transform(
			translation = ( 0,0,0 ),
			rotation = ( 0,0,0,0 ),
			children = moonChildren
		)
			
		#make planet Transform
		rad = random.random()*0.4+0.2 #size
		#c = random.random(), random.random(), random.random() #color
		plan = basenodes.Transform(
			translation = ( 0,0,0 ),
			children = [
				basenodes.TouchSensor(),
				basenodes.Shape(
					geometry = basenodes.Box( size = (rad,rad,rad) ),
					appearance = basenodes.Appearance(
						material = basenodes.Material( emissiveColor = (.8,.8,.8) ),
					),
				),
			]
		)		
		
		#transform to hold new planet and moons
		p = random.random()*16-8, random.random()*16-8, random.random()*16-8 #position
		r = random.random()*math.radians(180) #rotation
		planetAndMoons = basenodes.Transform(
			translation = p,
			rotation = (0,1,0,r),
			children = [
				plan,
				moons
			]
		)
		planetAndMoons.name = name
		planetAndMoons.sensititive = 0
		
		#made detail nodes
		detailPlanet = self.makeSpiral( geom )	
		detailMoons = self.textureMoons( moons,urls )
		xTrans = len(title.string[0])*-0.015
		dTitle = basenodes.Transform(
			translation = (xTrans,0.25,0),
			rotation = (0,0,0,0),
			children = [
				basenodes.Shape(
					geometry = title,
					appearance = basenodes.Appearance(
						material = basenodes.Material( emissiveColor = (.8,.8,.8) ),
					),
				)
			]
		)
		dTitleBB = basenodes.Billboard(
			axisOfRotation = (0,1,0),
			children = [ dTitle ]
		)
		#make the detail leg of the switch
		planetAndMoonsDetail = basenodes.Transform(
			translation = p,
			rotation = (0,1,0,0),
			children = [
				detailPlanet,
				detailMoons,
				dTitleBB
			]
		)
		planetAndMoonsDetail.name = name
		planetAndMoonsDetail.sensititive = 0
		
		#make switch
		detailSwitch = basenodes.Switch(
			whichChoice = 0,
			choice = [
				planetAndMoons,
				planetAndMoonsDetail,
			],
		)
		
		#add (planet) to solar sys
		tmpHolder = self.uni.children[0].children[-1].children
		tmpHolder.append(detailSwitch)
		self.uni.children[0].children[-1].children = tmpHolder
		#calc coors of all planets in solarsys
		coordsHolder = []
		for planet in self.uni.children[0].children[-1].children:
			if len(coordsHolder) == 0:
				coordsHolder.append( planet.translation )
			else:
				coordsHolder.append( planet.choice[0].translation )
		#put those calced points in the line object in the solarsys, and update length of line
		self.uni.children[0].children[-1].children[0].children[0].geometry.coord.point = coordsHolder
		self.uni.children[0].children[-1].children[0].children[0].geometry.coordIndex = range( 1,len(coordsHolder))
		
		
	def findPlanet( self, objPath ):
		"""helper function to find the planet in the scenegraph from a path"""
		"""returns object you are looking for, or null if not found"""
		print objPath
		tmpSys = objPath[2].name
		tmpPlanet = objPath[4].name
		#find the solar system position
		sysPos = -1
		sysNum = 0
		for sys in self.uni.children[0].children:
			if sys.name == tmpSys:
				sysPos = sysNum
			sysNum += 1
		if sysPos >= 0:			
			#find planet in solar system
			planetPos = -1
			planetNum = 0
			for planet in self.uni.children[0].children[sysPos].children:
				if planetNum == 0:
					if planet.name == tmpPlanet:
						planetPos = planetNum
				else:
					if planet.choice[0].name == tmpPlanet:
						planetPos = planetNum
				planetNum += 1
			if planetPos >= 0:
				print "found planet at:", planetPos
				return self.uni.children[0].children[sysPos].children[planetPos]
			else:
				print "didn't find planet in system"
				return () 
		else:
			print "did't find system"
			return ()
			
		
	def findSys( self, objPath ):
		"""helper function to find solarsys in the scenegraph from a path"""
		"""returns object you are looking for, or null if not found"""
		print objPath
		tmpSys = objPath[2].name
		#find the solar system position
		sysPos = -1
		sysNum = 0
		for sys in self.uni.children[0].children:
			if sys.name == tmpSys:
				sysPos = sysNum
			sysNum += 1
		if sysPos >= 0:
			print "Found sys at: ", sysPos
			return self.uni.children[0].children[sysPos]
		else:
			print "did't find system"
			return ()
		
		
	def renderDetail( self, obj ):
		"""takes in an object, switches out its geometry for detailed geometry"""
		#make the detail geometry
		"""
		t = basenodes.Transform(
			translation = ( 0,0,0 ),
			rotation = ( 0,0,0,0 ),
			children = [ 
				basenodes.Shape(
					geometry = geom,
					appearance = basenodes.Appearance(
						material = basenodes.Material( emissiveColor = (.8,.8,.8) ),
						#texture = imagetexture.ImageTexture( url = "200px-Bradypus.jpg"),
					),
				),
			],
		)	
		"""
		obj.whichChoice = 1
		"""
		t = self.makeSpiral( geom )	
		obj.choice[1].children[0] = t
		for m in range( len(obj.children[1].children) ):
			try:
				tmpTex = imagetexture.ImageTexture( url = [urls[m]] ) 
			except IOError:
				print 'oops'
			obj.choice[1].children[1].children[m].children[0].children[0].children[0].appearance.texture = tmpTex
			"""
			
		
	def unRenderDetail( self, obj ):
		"""puts the simple geometry back into the passes object"""
		obj.whichChoice = 0
		"""
		obj.children[0].children = [
			basenodes.TouchSensor(),
			basenodes.Shape(
				geometry = basenodes.Box( size = (0.3,0.3,0.3) ),
				appearance = basenodes.Appearance(
					material = basenodes.Material( emissiveColor = (.8,.8,.8) ),
				),
			),
		]"""
		
	def rotatePlanets( self, ang ):	
		"""rotate all the planets"""
		for s in range( len( self.uni.children[0].children )):
			for p in range( 1, len( self.uni.children[0].children[s].children ) ):
				#get the set choice from the detail whitch in the planet
				choice = self.uni.children[0].children[s].children[p].whichChoice
				#rotate planet
				self.uni.children[0].children[s].children[p].choice[choice].children[0].rotation = ( 0,1,0,ang )
				#rotate all moons
				for m in self.uni.children[0].children[s].children[p].choice[choice].children[1].children:
					rotHolder = m.children[0].rotation
					rotHolder[3] = ang * m.name
					m.children[0].rotation = rotHolder		
						
	def rotateMoons( self, ang ):
		"""rotates the moons on all the planets"""
		
		
	def textureMoons( self,plainMoons,urls ):
		texMoons = []
		aspect = 1.0
		for m in plainMoons.children:
			try:
				imgURL = urls[ len(texMoons) ]
				tmpImg = Image.open( imgURL )
				aspect = tmpImg.size[1]/tmpImg.size[0]
				tmpTex = imagetexture.ImageTexture( url = [imgURL] ) 
			except IOError:
				print 'oops'
			
			#make the translation Transform for the moon and add it to the rotation Transform
			mTrans = basenodes.Transform(
				translation = m.children[0].children[0].translation,
				rotation = ( 0,0,0,0 ),
				children = [
					basenodes.Shape(
						geometry = basenodes.Box( size = ( 0.01,0.2*aspect,0.2) ),
						appearance = basenodes.Appearance(
							texture = tmpTex,
						),
					),
				],
			)
			#make the rotation Transforms for the moon
			mRotY = basenodes.Transform(
				translation = (0,0,0 ),
				rotation = (0,1,0,0),
				children = [ mTrans ],
			)
			mr = random.random()*math.radians(360) #rotation
			mRotX = basenodes.Transform(
				translation = (0,0,0 ),
				rotation = m.rotation,
				children = [ mRotY ],
			)
			speedMultiplyer = random.random()*2.5+0.5
			mRotX.name = m.name
			texMoons.append( mRotX )

		#make moons Transform
		moonsWithTexture = basenodes.Transform(
			translation = ( 0,0,0 ),
			rotation = ( 0,0,0,0 ),
			children = texMoons
		)
		return moonsWithTexture

			
	def makeSpiral( self,geom ):
		radi = 0.2
		sPoints = []
		zRot = 720
		while zRot<2880:
			xyRot = zRot/20
			zxRad = math.sin( math.radians( xyRot ) )*radi
			yD = math.cos( math.radians( xyRot ) )*radi
			zD = math.cos( math.radians( zRot ) )*zxRad
			xD = math.sin( math.radians( zRot ) )*zxRad

			t = basenodes.Transform(
				translation = ( xD,yD,zD ),
				rotation = ( 0,1,.05,math.radians( zRot ) ),
				children = [ 
					basenodes.Shape(
						geometry = geom[ len(sPoints) ],
						appearance = basenodes.Appearance(
							material = basenodes.Material( emissiveColor = (.8,.8,.8) ),
						),
					),
				],
			)
			sPoints.append( t )
			zRot += 11
			
		spher = basenodes.Transform(
			translation = ( 0,0,0 ),
			rotation = ( 0,0,0,0 ),
			children = [ 
				basenodes.Shape(
					geometry = basenodes.Sphere( radius = 0.17 ),
					appearance = basenodes.Appearance(
						material = basenodes.Material( diffuseColor = (0,0,0) ),
					),
				),
			],
		)
		sPoints.append( spher )

		spiral = basenodes.Transform(
			translation = ( 0,0,0 ),
			rotation = ( 0,0,0,0 ),
			children = sPoints
		)
		print "NUM NODES IN SPIRSL: ", len(sPoints)
		return spiral
		
		