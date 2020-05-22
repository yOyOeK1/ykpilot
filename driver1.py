
import numpy as np
import math as m
from kivy.clock import Clock

# dummy bot turn tu direction off error 

class driver1:
	fps = 30.0
	work = False
	
	
	def __init__(self, simEng):
		self.sim = simEng
	
	
	def run(self,render = True):
		self.sim.reset()
		
		self.render = render
		self.work = True
		
		self.mainLoop()
		
		
	def mainLoop(self,*a):
		s = self.sim
		b = s.boat
		
		action = 0
		gRot = 0.1
		if b['cogError'] < 0.0 and b['gRot']>-gRot:
			action = -1
		elif b['cogError'] > 0.0  and b['gRot']<gRot:
			action = 1

		
		
		self.sim.iter(action)
		
		if self.render:
			self.sim.renderFrame()
		
		if self.work:
			if self.render:
				Clock.schedule_once( self.mainLoop, 1.00 / self.fps )
			else:
				Clock.schedule_once( self.mainLoop, 0.0 )
		