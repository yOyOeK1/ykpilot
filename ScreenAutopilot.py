from kivy.clock import Clock
#from kivy.core.audio import SoundLoader

#import pyaudio
#import numpy as np
import time
import _thread
import math
from audiostream import get_output
from audiostream.sources.wave import SineSource
from AutopilotSettings import AutopilotSettings


class ScreenAutopilot:
	
	def __init__(self,gui):
		self.gui = gui
		self.working = True
		self.freqOrg = 	[50.00, 100.00, 200.00, 0.01]
		self.freq = 	[50.00, 100.00, 200.00, 0.01]
		self.status = "off"
		self.targetHdg = 0
		self.tilerPos = 0.0
		self.str = get_output( channels=2, rate=22050, buffersize=128)
		self.burstRunning = False
		self.on_updateSettings()
		
		self.cMin = 0.0
		self.cPlus = 0.0
		self.clickSize = 0.4
		_thread.start_new(self.sinWatchDog,())
		
	def sinWatchDog(self):
		sleepTime = 0.05
		actionSumtract = sleepTime*5.0
		is_alive = False
		self.sin = SineSource(self.str,self.freq[1])
		
		while True:
			if 0:
				print('min', round(self.cMin,1), 
					" plus", round(self.cPlus,1),
					" burst", self.burstRunning,
					" apStat", self.status,
					" sinfreq", self.sin.frequency,
					' is_alive', is_alive					
					)
			
			if self.cMin > 0.0 and self.cPlus > 0.0:
				if self.cPlus >= self.cMin:
					self.cPlus-= self.cMin
					self.cMin = 0
				elif self.cPlus <= self.cMin:
					self.cMin-= self.cPlus
					self.cPlus = 0
				
			if self.cMin > 0.0:
				if self.sin.frequency != self.freq[0]:
					self.sin.frequency = self.freq[0]
				self.cMin-= actionSumtract
				
			elif self.cPlus > 0.0: 
				if self.sin.frequency != self.freq[2]:
					self.sin.frequency = self.freq[2]
				self.cPlus-= actionSumtract
				
			if self.cMin <= 0.0 and self.cPlus <= 0.0 and self.status == 'on':
				if self.sin.frequency != self.freq[1]:
					self.sin.frequency = self.freq[1]
				
			if is_alive == False:
				if self.burstRunning or self.status == 'on':					
					self.sin.start()
					is_alive = True					
						
			
				
			time.sleep(sleepTime)
			
			if self.status == 'off' and self.burstRunning:
				if self.cMin <= 0.0 and self.cPlus <= 0.0:
					self.sin.stop()
					self.sin = SineSource(self.str,self.freq[1])
					is_alive = False
					self.burstRunning = False
					self.cMin = 0.0
					self.cPlus = 0.0
					
			if self.status == 'off' and is_alive and self.burstRunning == False:
				self.sin.stop()
				self.sin = SineSource(self.str,self.freq[1])
				is_alive = False
				self.cMin = 0.0
				self.cPlus = 0.0
			
	def update(self,fromWho, vals):
		if fromWho == "comCal":
			self.gui.rl.ids.lAutHdg.text = "%sº" % round(vals)
	
	def updateGui(self):
		if self.gui.rl.current != "Autopilot":
			return None
		
		i = self.gui.rl.ids
		i.lAutInf.text = 'STAND BY' if self.status == 'off' else ( "Auto to %sº" % int(self.targetHdg))
		i.pbAutRud.value = self.tilerPos+45.0
				
	def on_updateSettings(self):
		if self.gui.config['apDirectionReverse'] == 0:
			self.freq[0] = float(self.freqOrg[0])
			self.freq[2] = float(self.freqOrg[2])
			
		else:
			self.freq[0] = float(self.freqOrg[2])
			self.freq[2] = float(self.freqOrg[0])
		
	def on_settings(self):
		print("ap.on_settings")
		self.aps = AutopilotSettings()
		self.aps.setAction(self.gui)
		self.aps.run()
		
	def on_pressMin(self):
		self.cMin+= self.clickSize
	def on_pressPlus(self):
		self.cPlus+= self.clickSize
		
	def on_curseAdjustBy(self, val):
		print("on_curseAdjustBy",val)
		self.targetHdg+= val
		self.updateGui()
		if self.status == "off":
			for _ in range(int(math.fabs(val))):
				if val < 0 :
					self.on_pressMin()
				else:
					self.on_pressPlus()
				self.burstRunning = True
	
	def on_auto(self):
		if self.status == "on":
			return None
				
		try:
			self.targetHdg = self.gui.sen.comCal.hdg
		except:
			self.on_standby()
			return None
		
		self.status = "on"
		self.updateGui()
		
	def on_standby(self):
		if self.status == "off":
			return None
		self.status = "off"
		self.updateGui()
		
	def on_onOff(self, obj):
		if self.status == "off":
			self.on_auto()	
		elif self.status == "on":
			self.on_standby()
			
		
		
	
	
	