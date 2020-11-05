import math
from kivy.clock import Clock
import random
import sys

class waveObj:	
	def __init__(self, fps, direction=90, height=2, waveEverySec=15):
		self.fps = fps
		self.tikSize = 1.0/self.fps
		self.direction = direction
		self.height = height
		self.every = waveEverySec
		self.state = 0.0
		
		self.sog = 2.0 # m/s
		self.fullCycleInDistance =  0.0

	def tik(self):
		self.state+= 360.0 / ( self.every * self.fps )
		if self.state > 360.0:
			self.state = self.state-360.00

		
class simEngine:
	
	def angle(self, pa, pb):
		return math.atan2(pb[1]-pa[1], pb[0]-pa[0])
		
	def dist(self, pa, pb):
		return math.sqrt( (pb[0] - pa[0])**2 + (pa[1] - pb[1])**2 )
	
	def getW(self,x,y,deb=False):
		yy = 0.0
		rx = 0.0
		ry = 0.0
		zPos = [0.0,0.0]
		bPos = [self.boat['x'],self.boat['y']]
		xy = [x,y]
		
		
		dis = self.dist(bPos, xy)
		ang = self.angle(bPos, xy)
		if deb:
			print('boat',bPos,'tail',xy)
		#dis = self.dist([0,0], [x,y])
		#ang = self.angle([0,0], [x,y])
		
		ang = math.radians(self.targetCog) + ang   
		for w in self.waves:
			w.fullCycleInDistance = w.sog*w.every # m
			d = dis*math.sin( math.radians(w.direction)-ang )
			if d == 0.0:
				d = 0.000000001
			a = 360.0*((d%w.fullCycleInDistance)/w.fullCycleInDistance)
			
			
			b = math.sin(math.radians(w.state+a))
			#print("ang", angDif)
			rx = 0.0 if b < 0.0 else 15.0
			b = b*w.height
			#print("dis",dis,' for ',x,y,' y_',y_,' full',w.fullCycleInDistance)
			
			#sys.exit(0)
			yy+=b
		return [yy,rx, ry]
	
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
		self.waves = [
			waveObj(self.fps, 45,0.5,12),
			#waveObj(self.fps, 270,5,30),
			#waveObj(self.fps, 45,0.7,9),
			waveObj(self.fps, 0,1,10)
			]
		self.boat= {
			'weight': 6.5,	#tons
			'length': 12.9,	#meters
			'beam': 4.5,
			
			'aX': 0.0,
			'aY': 0.0,
			'aZ': 0.0,
			'gX': 0.0,
			'gY': 0.0,
			'gZ': 0.0,
	
			'sog': 7.00,	#kts
			'cog': 0.01,	#magnetic deg
			'cogError': 0.0,
			
			'lat': 0.00,
			'lon': 0.00,
			
			'x': 0.00,
			'y': -36.00,
			'z': 0.0,
			
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
		# cog start at 
		range = 0.001
		self.targetCog = -(range/2.0) + (random.random()*range)
		# rudder start at and gRot
		ruderStart  = 0.0001
		self.boat['ruderPos'] = (-ruderStart/2.0) + random.random()*ruderStart
		  
		self.boat['sog'] = 0.2
		#self.boat['sog'] += (random.random()*5.0)-5.0
		self.runTime = 0.0
		self.xte = 0.0
		self.xteDirection = ""
		self.offSetTiler = 0.0
		
		a = 10
		while a > 0:
			self.iter(0)
			a-=1
		
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
		
		for w in self.waves:
			w.tik()
		
		
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
		i+= " target: "+str(round(self.targetCog,2))
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
		
	def on_key_up(self, args):
		print("simEngine.on_key_up",args)
		try:
			k = args[3]
			if k == 'a':
				self.boat['sog']+= 0.1
			elif k == ';':
				self.boat['sog']-= 0.1
			if args[2] == 80: 
				self.boat['ruderPos']-=0.1
			elif args[2] == 79:
				self.boat['ruderPos']+=0.1
		except:
			print("EE - on_key_up",len(args))	
			
		