
import numpy as np
import math as m
from kivy.clock import Clock
from simple_pid import PID
import simEngine
from TimeHelper import TimeHelper
from kivy.properties import NumericProperty,ObjectProperty
try:
	from PCPlot import PCPlot
except:
	pass
# pid? 

class driver10:
	fps = 30.0
	work = False
	lastValue = None
	
	
	def __init__(self, simEng):
		self.sim = simEng
		self.gui = self.sim.gui
		self.th = TimeHelper()
		self.actionHistory = [0]
		
		#self.Kp = 0.023
		self.pidP = 0.023
		self.pidI = 0.009
		self.pidD = 0.0018
		self.p = PID( self.pidP, self.pidI, self.pidD)#, setpoint=0,auto_mode=True )
		self.p.proportional_on_measurement = True
		self.resp = 0.0005
		#self.p.output_limits = (-1,1)
		
	def plotIt(self):
		self.gui.plt = PCPlot(self.gui)
		
	def updateGuiPIDVals(self):
		self.gui.rl.ids.ti_d10_p.text = str(self.p.Kp)
		self.gui.rl.ids.ti_d10_i.text = str(self.p.Ki)
		self.gui.rl.ids.ti_d10_d.text = str(self.p.Kd)
		self.gui.rl.ids.ti_d10_response.text = str(self.resp)
	
	def run(self,render = True):
		self.sim.reset()
		
		self.lc = 0
		self.work = True
		self.render = render
		d = 0.5
		self.updateGuiPIDVals()
		#self.p.proportional_on_measurement = True
		#self.p.set_auto_mode(True, last_output=8.0)
		if self.gui.platform == 'pc':
			self.plt = self.gui.plt
			
		self.mainLoop()
		
	def setPidPars(self):
		self.p.tunings = (
			float(self.gui.rl.ids.ti_d10_p.text),
			float(self.gui.rl.ids.ti_d10_i.text),
			float(self.gui.rl.ids.ti_d10_d.text)
			)
		self.resp = float(self.gui.rl.ids.ti_d10_response.text)
		self.updateGuiPIDVals()
	
	def setPar(self, par, obj):
		print("setPar",par,"->",obj)
		val = obj.value
		if par == 0:
			self.p.Kp = float(self.gui.rl.ids.ti_d10_p.text)
		if par == 1:
			self.p.Ki = float(self.gui.rl.ids.ti_d10_i.text)
		if par == 2:
			self.p.Kd = float(self.gui.rl.ids.ti_d10_d.text)
		
		print(self.p.Kp, self.p.Ki, self.p.Kd)
		
	def mainLoop(self,*a):
		s = self.sim
		b = s.boat
		
		#control = int(self.p(b['cogError'])*500)/500.000
		control = self.p(b['cogError'])
		action = 0
		
		if self.gui.platform == 'pc':
			t = self.th.getTimestamp(True)
			self.plt.simPID[0].append(t)
			self.plt.simPID[1].append(control*10.0)
			if 1:
				try:
					print("target from phone ",self.gui.sen.comCal.hdg)
					self.sim.targetCog = int(self.gui.sen.comCal.hdg)
				except:
					print("EE - no phone data no hdg in comCal")
			
		
		if self.lastValue == None:
			self.lastValue = control
		
		
		#print(
		#	"cogError",round(b['cogError'],6),
		#	"	pid",round(control,6),
		#	"	last",round(self.lastValue,6),
		#	"	diff",round((control-self.lastValue),6))

		
		#print("control %s for cogError %s"%(control, b['cogError']))
		
		if 1:
			if m.fabs( control-self.lastValue ) >= self.resp:
				if control > self.lastValue:
					action = -1
					#print("-")
				elif control < self.lastValue:
					action = 1 
					#print("+")
			
			
		elif 0:
			if -control < -0.2:
				action = -1
			elif -control > 0.2:
				action = 1
		
		else:
			gRot = 0.5
			if -control < -0.2 and b['gRot']>-gRot:
				action = -1
			elif -control > 0.2  and b['gRot']<gRot:
				action = 1
		
		self.lastValue = control
		
		#print(" pid return {}	{}	{}".format(action,control, b['cogError']))


		
		self.sim.iter(action)
		
		self.actionHistory.append( action )
		if len(self.actionHistory) > 500:
			self.actionHistory.pop(0)
		
		if self.render:
			self.sim.renderFrame()
		
		self.lc+=1
		
		if self.work:
			if self.render:
				Clock.schedule_once( self.mainLoop, 1.00 / self.fps )
			else:
				Clock.schedule_once( self.mainLoop, 0.0 )

		
