from kivy.clock import Clock
from kivy.uix.spinner import Spinner
#from kivy.core.audio import SoundLoader

#import pyaudio
#import numpy as np
import time
import _thread
import math
from audiostream import get_output
from audiostream.sources.wave import SineSource
from AutopilotSettings import AutopilotSettings
from driver9 import *
from threading import _start_new_thread
from simple_pid import PID
from apWifiCommunication import apWifiCommunication




class ScreenAutopilot:
	
	def __init__(self,gui):
		self.gui = gui
		self.working = True
		self.freqOrg = 	[50.00, 100.00, 200.00, 0.01]
		self.freq = 	[50.00, 100.00, 200.00, 0.01]
		self.status = "off"
		self.targetHdg = 0
		self.tilerPos = 0.0
		self.burstRunning = False
		self.on_updateSettings()
		
		self.driverQRL = None
		
		self.cMin = 0.0
		self.cPlus = 0.0
		self.clickSize = 0.15
		
		self.Kp = 0.023
		self.Ki = 0.009
		self.Kd = 0.0018
		self.response = 0.0008
		self.pid = PID( self.Kp, self.Ki, self.Kd )
		self.pid.proportional_on_measurement = True
		self.pidLast = None
		self.lastValue = 0
		
		self.pid2 = PID( self.Kp, self.Ki, self.Kd)
		self.p2Last = None
		
		self.driverType = self.gui.config['apDriver']
		self.sDriTyp = Spinner(
			values = ['driver9 3kts', 'driver9 11kts', 'PID', 'PID2'],
			text = self.driverType,
			)
		self.gui.rl.ids.blAutDri.add_widget(self.sDriTyp)
		self.sDriTyp.bind(text=self.on_driverChange)
		
		#self.apCommunicationMode = self.gui.config['apCommunicationMode']
		_thread.start_new(self.sinWatchDog,())
		
	def on_driverChange(self, obj, text):
		self.driverType = text
		self.gui.config['apDriver'] = text
		
		
	def initSine(self):
		self.str = get_output( channels=2, rate=22050, buffersize=128)
		self.sin = SineSource(self.str,self.freq[1])
		
	def apAction(self,v):
		#print("apAction",v)
		if v == -1:
			self.on_pressMin()
		elif v == 1:
			self.on_pressPlus()
		
	def apIter(self):
		
		if self.driverQRL == None:
			self.setupDriver()
		
		while self.status == 'on':
			pidVal = 0.0
			boat = self.gui.sen.boat
			boat['sog'] = 11.0
			boat['cog'] = boat['hdg']
			if boat['cog'] >= 180.00:
				boat['cog'] = boat['cog'] - 360.0
			boat['cogError'] = (self.targetHdg-boat['hdg'])%360.0
			if boat['cogError'] >= 180.0:
				boat['cogError'] = boat['cogError']-360.0
			
			#print(boat)
			
			action = 0
			if self.driverType == 'driver9 11kts':
				boat['sog'] = 11.0
				ds = self.driverQRL.get_discrete_state( boat )
				aa = max(self.driverQRL.q_table[ds])
				action = self.driverQRL.q_table[ds].index(aa)-1
			
			elif self.driverType == 'driver9 3kts':
				boat['sog'] = 3.0
				ds = self.driverQRL.get_discrete_state( boat )
				aa = max(self.driverQRL.q_table[ds])
				action = self.driverQRL.q_table[ds].index(aa)-1			
			
			elif self.driverType == 'PID':
				c = self.pid( boat['cogError'] )
				pidVal = c
				if self.pidLast == None:
					self.pidLast = c
				
				if m.fabs( c-self.pidLast ) >= self.response:
					if c > self.lastValue:
						action = -1
					elif c < self.lastValue:
						action = 1 
				
				self.pidLast = c
				#print("PID action ",action," c",c)
					
			elif self.driverType == 'PID2':
				c = int(self.pid2( boat['cogError'] )*500)/500.00
				pidVal = c
				if self.p2Last == None:
					self.p2Last = c
				
				if self.p2Last < c:
					action = -1
				elif self.p2Last > c:
					action = 1 
				
				self.p2Last = c
				print("PID2 action",action)
				
					
			#print("driver",self.driverType,' action ',action)
				
			self.apAction(action)
			
			self.gui.rl.ids.pbAutRud.value = self.tilerPos+45.0
			if self.gui.config['nmeBAutopilot']:
				self.gui.sf.sendToAll( str({
                    "type": "autopilot",
                    "data": {
						'hdg': boat['hdg'],
						'pid': pidVal,
						'cogError': boat['cogError'],
						'targetCOG': self.targetHdg,
						'tilerPos': self.tilerPos,
						'action': action
						}
                    }) )	
				
			time.sleep(1.0/15.0)
			
		
	def sinWatchDog(self):
		sinRunning = 0
		sleepTime = 0.45
		actionSumtract = sleepTime*2.0
		is_alive = False
		
		print("apCommunicationMode",self.apCommunicationMode)
		
		if self.apCommunicationMode == 'audio jack':
			self.initSine()
			
		while True:
			#print("ap iter ?")
			
			
			if 0:
				print('min', round(self.cMin,1), 
					" plus", round(self.cPlus,1),
					" burst", self.burstRunning,
					" apStat", self.status,
					" sinfreq", self.sin.frequency,
					' is_alive', is_alive,
					' sinCo', sinRunning					
					)
			
			if is_alive == False and self.apCommunicationMode == 'audio jack':
				if self.burstRunning or self.status == 'on':					
					try:
						self.sin.start()
					except:
						self.initSine()
						self.sin.start()
					sinRunning+=1
					is_alive = True		
							

			
			if self.cMin > 0.0 and self.cPlus > 0.0:
				if self.cPlus >= self.cMin:
					self.cPlus-= self.cMin
					self.cMin = 0
				elif self.cPlus <= self.cMin:
					self.cMin-= self.cPlus
					self.cPlus = 0
				
			if self.cMin > 0.0:
				if self.apCommunicationMode == 'audio jack':
					if self.sin.frequency != self.freq[0]:
						self.sin.frequency = self.freq[0]
				elif self.apCommunicationMode == 'wifi udp':
					self.udp.send(self.apWifiCmdL)
				elif self.apCommunicationMode == 'wifi tcp':
					self.tcp.send(self.apWifiCmdL)
				elif self.apCommunicationMode == 'mqtt ap switch':
					self.gui.hbc.pub('esp01/ap',self.mqCmdL)
					
				self.cMin-= actionSumtract
				
			elif self.cPlus > 0.0: 
				if self.apCommunicationMode == 'audio jack':
					if self.sin.frequency != self.freq[2]:
						self.sin.frequency = self.freq[2]
				elif self.apCommunicationMode == 'wifi udp':
					self.udp.send(self.apWifiCmdR)
				elif self.apCommunicationMode == 'wifi tcp':
					self.tcp.send(self.apWifiCmdR)
				elif self.apCommunicationMode == 'mqtt ap switch':
					self.gui.hbc.pub('esp01/ap',self.mqCmdR)
					
				self.cPlus-= actionSumtract
				
			if self.cMin <= 0.0 and self.cPlus <= 0.0 and self.status == 'on':
				if self.apCommunicationMode == 'audio jack':
					if self.sin.frequency != self.freq[1]:
						self.sin.frequency = self.freq[1]
					elif self.apCommunicationMode == 'wifi tcp':
						self.tcp.send(self.apWifiCmdPing)
					elif self.apCommunicationMode == 'mqtt ap switch':
						self.hbc.mqc.pub('esp01/ap',self.mqCmdPing)
				
				
			time.sleep(sleepTime)
			
			if self.status == 'off' and self.burstRunning:
				if self.cMin <= 0.0 and self.cPlus <= 0.0:
					if self.apCommunicationMode == 'audio jack':
						self.sin.stop()
					sinRunning-=1
					is_alive = False
					self.burstRunning = False
					self.cMin = 0.0
					self.cPlus = 0.0
					
			if self.status == 'off' and is_alive and self.burstRunning == False:
				if self.apCommunicationMode == 'audio jack':
					self.sin.stop()
				sinRunning-=1
				is_alive = False
				self.cMin = 0.0
				self.cPlus = 0.0

	def setupDriver(self):
		print("---------- setup driver ----------")
		self.driverQRL = qrlAtomizer("atomizer")
		self.driverQRL.epsilon = 0.0
		self.driverQRL.reset()
		self.driverQRL.startEpisode()		
		print("---------- setup driver ----------DONE")	
			
	def update(self,fromWho, vals):
		if fromWho == "comCal":
			self.gui.rl.ids.lAutHdg.text = "%sº" % round(vals[0])
	
	def updateGui(self):
		if self.gui.rl.current != "Autopilot":
			return None
		
		i = self.gui.rl.ids
		i.lAutInf.text = 'STAND BY' if self.status == 'off' else ( "Auto to %sº" % int(self.targetHdg))
		i.pbAutRud.value = self.tilerPos+45.0
				
	def on_updateSettings(self):
		self.mqCmdPing = 0
		if self.gui.config['apDirectionReverse'] == 0:
			self.freq[0] = float(self.freqOrg[0])
			self.freq[2] = float(self.freqOrg[2])
			self.apWifiCmdL = 'L'
			self.apWifiCmdR = 'R'
			self.mqCmdR = 2
			self.mqCmdL = 1
			
			
		else:
			self.freq[0] = float(self.freqOrg[2])
			self.freq[2] = float(self.freqOrg[0])
			self.apWifiCmdL = 'R'
			self.apWifiCmdR = 'L'
			self.mqCmdR = 1
			self.mqCmdL = 2

		
		self.apWifiCmdPing = "P"
			
		self.apCommunicationMode = self.gui.config['apCommunicationMode']
		if self.apCommunicationMode == "wifi udp":
			self.udp = apWifiCommunication()
			self.udp.connect(
				self.gui.config['apWifiIp'], 
				18889
				)
		elif self.apCommunicationMode == "wifi tcp":
			#self.startTcp()
			pass
				
		
	def startTcp(self):
		self.tcp = self.gui.tcp4ap
		if self.tcp.workStatus == False:
			self.tcp.work()
						
		
	def on_settings(self):
		print("ap.on_settings")
		self.aps = AutopilotSettings()
		self.aps.setAction(self.gui)
		self.aps.run()
		
	def on_pressMin(self):
		self.cMin+= self.clickSize
		self.tilerPos-=0.25
		self.gui.rl.ids.pbAutRud.value = self.tilerPos+45.0
		
	def on_pressPlus(self):
		self.cPlus+= self.clickSize
		self.tilerPos+=0.25
		self.gui.rl.ids.pbAutRud.value = self.tilerPos+45.0
		
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
		
		_thread.start_new(self.apIter,())
		
	def on_standby(self):
		if self.status == "off":
			return None
		self.status = "off"
		self.tilerPos = 0.0
		self.updateGui()
		
	def on_onOff(self, obj):
		self.tilerPos = 0.0
		if self.status == "off":
			self.on_auto()	
		elif self.status == "on":
			self.on_standby()
			
		
		
	
	
	