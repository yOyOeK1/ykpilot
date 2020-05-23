import math
from kivy.clock import Clock
import random


class simEngine:
	
	ktsToMetersPerSec = 0.514444
	
	boat = {}
	distToTrac = 0.0
	targetCog = 0.0
	
	runLoop = False
	renderFrames = True
	fps = 30.00
	iterTime = 1.00/fps
	runTime = 0.0
	
	def __init__(self, gui, render):
		self.gui = gui
		self.renderEngine = render
		self.reset()
	
	def reset(self):
		self.boat= {
			'weight': 6.5,	#tons
			'length': 12.9,	#meters
	
			'sog': 7.00,	#kts
			'cog': 0.01,	#magnetic deg
			'cogError': 0.0,
			'lat': 0.00,
			'lon': 0.00,
			'x': 0.00,
			'y': -36.00,
			
			'velocity': None,	# meters / sec
			'gRot': 0.0,		# rad / sec off turn
			'cogOld': 0.0,
			'angleSpeed': 0.0,
			'ruderPos': 0.0,
			'ruderRatio': 0.2,	# ratio ruder to boat best conditions
			'armToRuderDelay': 0.95,	# retio of sofftning (windvane and hardware part)
			'ruderD': 0.0,
			' ': None
		}
		self.boat['velocity'] = self.boat['sog']*self.ktsToMetersPerSec
		range = 359.999
		self.targetCog = -(range/2.0) + (random.random()*range)  
		self.boat['sog'] = 11.00
		#self.boat['sog'] += (random.random()*5.0)-5.0
		self.runTime = 0.0
		self.xte = 0.0
		self.xteDirection = ""
		self.offSetTiler = 0.0
		
		
	def mainLoop(self,*a):
		#print("mainLoop frame render [%s]"%self.renderFrames)
		self.iter()
		
		if self.renderFrames:
			self.renderFrame()
		
		if self.runLoop:
			Clock.schedule_once( self.mainLoop, 1.00 / self.fps )
		
	
	
	def newXY(self, X,Y,angle,distance):                #defines function
		# 0 degrees = North, 90 = East, 180 = South, 270 = West
		dY = distance*math.cos(math.radians(angle))   #change in y 
		dX = distance*math.sin(math.radians(angle))   #change in x 
		Xfinal = X + dX                               
		Yfinal = Y + dY
		return Xfinal, Yfinal
			
	# action: (ruder) -1 - left 0 - no diff 1 - right 
	def iter(self, action=0):
		intRunTime = int(self.runTime)
		intRunTime = 1
		
		
		if intRunTime == 5:
			self.targetCog = 25.00
		elif intRunTime == 7:
			self.targetCog = 45.00
		
		elif intRunTime == 15:
			self.targetCog = 25.00
		elif intRunTime == 17:
			self.targetCog = 0.00
		elif intRunTime == 19:
			self.targetCog = -25.00
		elif intRunTime == 21:
			self.targetCog = -45.00
		
		elif intRunTime == 30:
			self.targetCog = -25.00
		elif intRunTime == 32:
			self.targetCog = 0.00
		elif intRunTime == 34:
			self.targetCog = 25.00
		elif intRunTime == 36:
			self.targetCog = 45.00
			
		elif intRunTime == 40:
			self.offSetTiler = 10-random.random()*20.0
		
		
		b = self.boat

		"""
		offWave = 0.0
		if random.random()>0.99:
			offWave = 25.0
		b['cog']+= offWave
		"""
		
		#print("action [%s]"% action)
		if action == -1:
			b['ruderPos']-= 10.0/self.fps
			if b['ruderPos']<-45.0:
				b['ruderPos'] = -45.0
		elif action == 1:
			b['ruderPos']+= 10.0/self.fps
			if b['ruderPos']>45.0:
				b['ruderPos'] = 45.0
			
		
		
		defOff = (b['ruderRatio']*(b['ruderPos']+self.offSetTiler))*(b['velocity']*0.05)
		b['angleSpeed'] = b['angleSpeed']*b['armToRuderDelay']+defOff*(1.0-b['armToRuderDelay'])
		b['cog'] = (b['cog']+b['angleSpeed'])%360.00
		if b['cog'] >= 180.0:
			b['cog'] = b['cog'] - 360.0
		
		
		b['x'], b['y'] = self.newXY(
			b['x'], b['y'], b['cog']-self.targetCog, b['sog']/self.fps)
		
		self.xte = b['x']
		if self.xte < 0.0:
			self.xteDirection = "S"
		elif self.xte > 0.0:
			self.xteDirection = "P"
		else:
			self.xteDirection = ""
		b['cogError'] = (self.targetCog-b['cog'])%360
		#print(b['cogError'])
		if b['cogError'] >= 180.0:
			b['cogError'] = b['cogError']-360.0
		
		b['gRot'] = (math.radians(b['cog'])-math.radians(b['cogOld']))*self.fps
		b['cogOld'] = b['cog']
	
		self.runTime+= 1.0/self.fps
	
	def renderFrame(self):
		b = self.boat
		i = "sog: "+str(b['sog'])+"\n"
		i+= "velocity: "+str(round(b['velocity'],2))+"\n"
		i+= "cog: "+str(round(b['cog'],1))
		i+= " target: "+str(self.targetCog)
		i+= " error: "+str(round(b['cogError'],2))+"\n"
		i+= "gRot: "+str(round(b['gRot'],3))+"\n"
		i+= "XTE: "+str(round(math.fabs(self.xte),2))
		i+= " ("+self.xteDirection+")"+"\n"
		#i+= "lat: "+str(b['lat'])+"\n"
		#i+= "lon: "+str(b['lon'])+"\n"
		i+= 'rudder: '+str(round(b['ruderPos'],2))
		i+= " offset: "+str(round(self.offSetTiler,2))+"\n"
		self.gui.rl.ids.lSimInf.text = i
		
		self.renderEngine.update_glsl()
	
	def on_ruderSet(self,w):
		self.boat['ruderPos'] = round(float(w.value),1)
	
	def on_reset(self):
		self.reset()
	
	def on_run(self,renderFrames = True):
		self.renderFrames = renderFrames
		self.runLoop = True
		self.mainLoop()
		
	def on_stop(self):
		self.runLoop = False
		
	def on_iter(self):
		self.iter()
		self.renderFrame()
		