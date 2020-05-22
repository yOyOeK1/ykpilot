
import numpy as np
import math as m
from kivy.clock import Clock
from simple_pid import PID

# pid? 

class driver2:
	fps = 30.0
	work = False
	
	
	def __init__(self, simEng):
		self.sim = simEng
	
	
	def run(self,render = True):
		self.sim.reset()
		
		self.lc = 0
		self.work = True
		self.render = render
		d = 0.5
		self.Kp = 0.05*d
		self.Ki = 0.02*d
		self.Kd = 0.2*d
		self.p = PID( self.Kp, self.Ki, self.Kd, setpoint=0,auto_mode=True )
		self.p.proportional_on_measurement = True
		#self.p.set_auto_mode(True, last_output=8.0)
		self.mainLoop()
		
	def setPar(self, par, obj):
		val = obj.value
		if par == 0:
			self.p.Kp = self.Kp+(self.Kp*val)
		if par == 1:
			self.p.Ki = self.Ki+(self.Ki*val)
		if par == 2:
			self.p.Kd = self.Kd+(self.Kd*val)
		
		print(self.p.Kp, self.p.Ki, self.p.Kd)
		
	def mainLoop(self,*a):
		s = self.sim
		b = s.boat
		
		action = 0
		
		control = self.p(b['cogError'])
		#print("control %s for cogError %s"%(control, b['cogError']))
		
		if True:
			pidError = 0.75
			if -control < pidError:# and b['ruderPos'] > -20.00:
				action = -1
			elif -control > pidError:# and b['ruderPos'] < 20.00:
				action = 1 
		else:
			gRot = 0.5
			if -control < -0.2 and b['gRot']>-gRot:
				action = -1
			elif -control > 0.2  and b['gRot']<gRot:
				action = 1
		


		
		self.sim.iter(action)
		if self.render:
			self.sim.renderFrame()
		
		self.lc+=1
		
		if self.work:
			if self.render:
				Clock.schedule_once( self.mainLoop, 1.00 / self.fps )
			else:
				Clock.schedule_once( self.mainLoop, 0.0 )