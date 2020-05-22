
import math as m
import time
from TimeHelper import *
from kivy.clock import Clock


class waveCicleHolder:
	pi = m.pi
	piHalf = pi/2.0
	pi2 = pi*2.0
	
	# memorySize - seconds of memory back
	def __init__(self,gui, name, memorySize=4, internalHz=30.0):
		self.gui = gui
		self.name = name
		self.th = TimeHelper()
		
		self.memorySize = memorySize
		self.internalHz = internalHz
		
		self.history = []
		self.updateTime = []
		self.inStatus = 0.0
		self.hz = 0.7
		
		self.syncDone = False
		self.syncStep = 0
		
		Clock.schedule_interval(self.internalLoop, 1.0 / self.internalHz )

		
	def internalLoop(self,a):
		if len(self.history)> 10:
			if self.syncDone == False:
				print("sync ",self.name)
				res = self.gui.sen.sinWaveAnalitic( self.history )
				if self.history[-2] < res['avg'] and res['last'] > res['avg']:
					if self.syncStep == 0:
						self.downTime = self.th.getTimestamp(True)
						self.syncStep = 1
						print("	got 1")
						time.sleep(0.4)
					elif self.syncStep == 1:
						cycleTime = self.th.getTimestamp(True)-self.downTime
						self.inStatus = self.piHalf
						self.syncDone = True
						print(" got 2")
						print(cycleTime)
					
			else:
				add = self.pi2/self.internalHz*self.hz
				inStatusOld = self.inStatus
				self.inStatus = (self.inStatus+add)%self.pi2
				
				res = self.gui.sen.sinWaveAnalitic( self.history )
				if inStatusOld <= self.piHalf and self.inStatus > self.piHalf:
					if res['last'] > res['avg']:
						self.hz-= 0.005
					else:
						self.hz+= 0.005
				
				dir = m.sin(self.inStatus)
				
				
				#print(round(dir,2), round(self.hz,5), self.inStatus, len(self.history))
			
		
	def update(self,v):
		timeNow = self.th.getTimestamp()
		self.updateTime.append( timeNow )
		self.history.append( v )
		
		
		toOld = timeNow-self.memorySize
		while True:
			if self.updateTime[0] < toOld:
				self.updateTime.pop(0)
				self.history.pop(0)
			else:
				break
				
		
		
