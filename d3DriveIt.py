'''
3D Rotating Monkey Head
========================

This example demonstrates using OpenGL to display a rotating monkey head. This
includes loading a Blender OBJ file, shaders written in OpenGL's Shading
Language (GLSL), and using scheduled callbacks.

The monkey.obj file is an OBJ file output from the Blender free 3D creation
software. The file is text, listing vertices and faces and is loaded
using a class in the file objloader.py. The file simple.glsl is
a simple vertex and fragment shader written in GLSL.
'''

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.image import Image
from kivy.graphics import BindTexture
from kivy.uix.widget import Widget
from kivy.resources import resource_find
from kivy.graphics.transformation import Matrix
from kivy.graphics.opengl import *
from kivy.graphics import *
import math as m
import random,sys
from kivy.properties import ListProperty, ObjectProperty, NumericProperty
from D3Helper import D3Helper
from kivy.animation import Animation
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.floatlayout import FloatLayout
from OdeBody import OdeBody as ob
import ode
#from panda3d.ode import OdeBallJoint

d3tex2RunAlone = False

class FObject:
	def __init__(self,l):
		print("FObject",l)
		for k in l:
			print("making k(",k,") value ",l[k])
			self.k = l[k]
			

class d3tex2(Widget):
		
	def __init__(self, **kwargs):
		self.gui = None
		
		self.boat = {
			'x':	0.0,
			'y':	0.0,
			'speed': 0.0,
			'direction': 0.0,
			'tiler': 0.0
			}
		
		self.odeBody = ob()
		
		self.odeWorld = ode.World()
		self.odeWorld.setGravity( (0,-9.81,0) )
		
		self.odeBoat = ode.Body(self.odeWorld)
		mas = ode.Mass()
		mas.setBox(10,10,10,10)
		mas.mass = 1.0
		self.odeBoat.setMass(mas)
		self.odeBoat.setPosition( (self.boat['x'],0,self.boat['y']) )
		
		
		
		self.odeR = ode.Body(self.odeWorld)
		M = ode.Mass()
		M.setBox(10,10,10,10)
		M.mass = 1.0
		self.odeR.setMass(M)
		self.odeR.setPosition( (self.boat['x']+2,0,self.boat['y']) )
		
		
		self.odeJR = ode.FixedJoint(self.odeWorld)
		self.odeJR.setFeedback(True)
		self.odeJR.attach(self.odeBoat, self.odeR)
		self.odeJR.setFixed()
		
		
		
		#j.setAnchor( (2.0,0,0) )
		
		
		self.dirAvg = self.boat['direction']
		self.heewCounter = 0.0
		self.pitchCounter = 0.0
		self.k = {
			'up': False,
			'down': False,
			'left': False,
			'right': False
			}
		
		
		self.canvas = RenderContext(compute_normal_mat=True)
		self.canvas.shader.source = resource_find('simple.glsl')
		
		self.d3h = D3Helper()
		self.d3h.loadObj([
			['boat',"./3dModels/boat2_3dex_boat.obj","./3dModels/oiysh_profile2.jpeg"],
			['roseta','./3dModels/3d_roseta.obj',''],
			['genoa',"./3dModels/boat2_3dex_sailGenoa_onPower.obj","./3dModels/3d_texture_genoa.jpg"],
			['main',"./3dModels/boat2_3dex_sailMain_sailup_onPower.obj","./3dModels/IMG_5410.jpg"],
			['boom',"./3dModels/boat2_3dex_boom.obj",""],
			['ruder',"./3dModels/boat2_3dex_ruder.obj",""],
			['tiler',"./3dModels/boat2_3dex_tiler.obj",""],
			#['hdr1','./3dModels/hdr1.obj','./3dModels/hdr1.png'],
			['xAxis','./3dModels/x-axis.obj','./3dModels/red.png'],
			['yAxis','./3dModels/y-axis.obj','./3dModels/green.png'],
			['zAxis','./3dModels/z-axis.obj','./3dModels/blue.png'],
			['box','./3dModels/3d_box.obj',''],
			['waterTile','./3dModels/waterTile.obj',"./3dModels/IMG_5410.jpg"],
			['hdr2','./3dModels/hdr2.obj',"./3dModels/PANO_20160311_160253.jpg"],
			['kap2','./3dModels/tile.obj',"./3dModels/kap2.png"],
			["infWat","./3dModels/infinityWater.obj",""]
			
			
			])
		
		super(d3tex2, self).__init__(**kwargs)
		
		with self.canvas:
			self.cb = Callback(self.setup_gl_context)
			PushMatrix()
			self.setup_scene()
			PopMatrix()
			self.cb = Callback(self.reset_gl_context)
		
		if d3tex2RunAlone:
			self.on_displayNow()
			
		Window.bind(on_key_down=self.on_key_down)
		Window.bind(on_key_up=self.on_key_up)
		Window.bind(on_touch_down=self.on_touchDown)
		Window.bind(on_touch_move=self.on_touchMove)
		Window.bind(on_touch_up=self.on_touchUp)
	
	
	def on_touchDown(self, touch, pos=0):
		ss = Window.size
		if ss[1]*0.5 > pos.pos[1]:
			self.touch = True
			self.touchCenter = pos.pos
		return False
	
	def on_touchMove(self, touch, pos=0):
		if self.touch:
			p = pos.pos
			acu = 20
			tcx = int(self.touchCenter[0]/acu)
			tcy = int(self.touchCenter[1]/acu)
			
			for k in self.k.keys():
				self.k[k] = False
			
			if tcy < int(p[1]/acu):
				print('up')
				self.k['up'] = True
			if tcy > int(p[1]/acu):
				print('down')
				self.k['down'] = True
		
			if tcx < int(p[0]/acu):
				print('right')
				self.k['right'] = True
			if tcx > int(p[0]/acu):
				print('left')
				self.k['left'] = True	
		
		return False
	
	def on_touchUp(self, touch, pos=0):
		self.touch = False
		for k in self.k.keys():
			self.k[k] = False
		return False
	
	
	
	def on_key_down(self, *args):
		#print("on_key_down",list(args))
		if args[2] == 82: # up
			self.k['up'] = True
		if args[2] == 81: # down
			self.k['down'] = True
		if args[2] == 79: # right
			self.k['right'] = True
		if args[2] == 80: # left
			self.k['left'] = True
			
	
	def on_key_up(self, *args):
		#print("on_key_up",list(args))
		if args[2] == 82: # up
			self.k['up'] = False
		if args[2] == 81: # down
			self.k['down'] = False
		if args[2] == 79: # right
			self.k['right'] = False
		if args[2] == 80: # left
			self.k['left'] = False
		
	def on_displayNow(self):	
		self.scheduler = Clock.schedule_interval(self.update_glsl, 1 / 30.)
		
		self.openScreenAnimation()
		
	def on_noMoreDisplayd(self):
		try:
			Clock.unschedule(self.scheduler)
		except:
			print("no running scheduler for boatRender")

	def setGui(self,gui):
		self.gui = gui
		

	def openScreenAnimation(self):
		print("openScreenAnimation")
		#self.cam = [9.586206896551722, -14.0, 0.0]		
		#self.update_glsl(forceUpdate=True)
		#self.update_glsl(forceUpdate=True)
		#self.update_glsl(forceUpdate=True)
		self.cam = [0.6028708133971286, -6.765550239234449, -14.0]
		

	def setup_gl_context(self, *args):
		glEnable(GL_DEPTH_TEST)
		

	def reset_gl_context(self, *args):
		glDisable(GL_DEPTH_TEST)

		
	def update_glsl(self, *largs, forceUpdate=False):
		if 1:
			if self.gui:
				if self.gui.rl.current != "3dtextures2":
					self.on_noMoreDisplayd()
					return None
		
		self.odeBody.makeTik(1.0/30.0)
		self.odeWorld.step(1.0/30.0)
		
		
		if self.k['up'] == True:
			if self.boat['speed']<1.7:
				self.boat['speed']+= 0.01
		if self.k['down'] == True:
			if self.boat['speed']>-1.7:
				self.boat['speed']-= 0.01
		if self.k['right'] == True:
			#self.boat['direction']+=1.0
			if self.boat['tiler']<55.0:
				self.boat['tiler']+= 1.0
		if self.k['left'] == True:
			#self.boat['direction']-=1.0
			if self.boat['tiler']>-55.0:
				self.boat['tiler']-= 1.0
		
		#print(self.k)
		#print(self.boat)
		self.ruderStockRot.angle = self.boat['tiler']
		
		rDir = m.radians(self.boat['direction']-90.0)
		self.boat['x']+= m.cos(rDir)*self.boat['speed']*0.1
		self.boat['y']+= m.sin(rDir)*self.boat['speed']*0.1
		
		self.boat['direction']+= (self.boat['tiler']*0.04)* \
			self.boat['speed']*0.5
			#(1.0 if self.boat['speed']<=0.0 else -1.0)* \
		
			
		#self.boatPos.x = self.boat['x']
		#self.boatPos.z = self.boat['y']
		
		ox,oy,oz = self.odeBoat.getPosition()
		self.boatPos.x = ox
		self.boatPos.y = oy
		self.boatPos.z = oz
		
		heewAddFromTilerMove = (self.boat['tiler']*-0.2)*self.boat['speed']
		self.boatRot.angle = -self.boat['direction']
		#self.boatHeew.angle = m.cos(m.radians(self.heewCounter))*7.0 + heewAddFromTilerMove
		#self.boatPitch.angle = m.cos(m.radians(self.pitchCounter))*2.0 + (self.boat['speed']*3.2)
		
		'''
		self.hdr2Pos.x = self.boatPos.x
		self.hdr2Pos.z = self.boatPos.z
		self.hdr2Rot.angle = -self.boatRot.angle
		self.hdr2Heew.angle = -self.boatHeew.angle
		self.hdr2Pitch.angle = -self.boatPitch.angle
		'''
		
		self.boatSMainAngle.angle-= (self.boatHeew.angle)*0.1
		if self.boatSMainAngle.angle < -80.0:
			self.boatSMainAngle.angle = -80.0
		elif self.boatSMainAngle.angle > 80.0:
			self.boatSMainAngle.angle = 80.0
		
		self.heewCounter+=1.5
		self.pitchCounter+=1.2
		
		ws = Window.size
		asp = ws[0] / float(ws[1])
		proj = Matrix().view_clip(
			-asp/2.0,asp/2.0,-1, 1, 1, 100, 1)
		self.canvas['projection_mat'] = proj
		#self.canvas['diffuse_light'] = (0.1, 0.0, 0.8)
		#self.canvas['ambient_light'] = (0.5, 0.5, 0.5)
		#self.canvas['texture1'] = 1
		#self.camRot.angle += 0.2
		
		#self.infWat
		wxy = {}
		for x in range(10):
			
			for y in range(10):
				
				yy = m.sin(m.radians((self.pitchCounter+(x*80))*0.5) )
				yy += m.sin(m.radians((self.heewCounter+(y*80))*0.5))
				self.wTiles["%s_%s"%(x,y)]['pos'].y = yy 
				if x == 5 and y == 5:
				#	self.boatPos.y = yy
					yForBoat = yy
				if x == 6 and y == 5:
				#	self.boatPos.y = yy
					yForR = yy
				yy = m.sin(m.radians(x+self.pitchCounter)*10.5) 
				yy += m.sin(m.radians(y+self.pitchCounter)*10.5) 
				
				wxy["%s_%s"%(x,y)] = yy
		
		
		self.odeBody.setForce(wxy,[5,5])
		
		#yForBoat = 0.0
		by = self.boatPos.y-2.0
		#print("by",by,"yForBoat",yForBoat,"force",self.odeBoat.getForce())
		if yForBoat>by:
			fy = (-4.0*(by-yForBoat))
			if fy > 12.0:
				fy = 12.0
			#print("+",(fy))
			
			self.odeBoat.setForce( ( 0.0, fy, 0.0 ) )
		else:
			self.odeBoat.setForce( ( 0.0, 0.0, 0.0 ) )
			print('-')
			
		if yForR>by:
			fy = (-4.2*(by-yForR))
			if fy > 12.0:
				fy = 12.0
			#print("+",(fy))
			
			self.odeR.setForce( ( 0.0, fy, 0.0 ) )
		else:
			self.odeR.setForce( ( 0.0, 0.0, 0.0 ) )
			#print('-')
			#self.odeBoat.setForce( ( 0.0, 0.0, 0.0) )
		#print("1by",by,"yForBoat",yForBoat,"force",self.odeBoat.getForce())
		
		orx,ory,orz = self.odeR.getPosition()
		self.oAxisPos.x = orx
		self.oAxisPos.y = ory
		self.oAxisPos.z = orz
		
			
		#print("b",self.odeBoat.getAngularVel())
		#print("j",self.odeJR.getFeedback())
				
		"""
		for i in self.meshs.keys():
			m = self.meshs[i]
			m[0].angle = m[0].angle*self.aniSteps+m[1]*(1.00-self.aniSteps)
		"""
		self.camPos.x = self.cam[0]-self.boat['x']
		self.camPos.y = self.cam[1]
		self.camPos.z = self.cam[2]-self.boat['y']
		#self.camRot.angle = self.boat['direction']
		
		for o in range(6):
			orx,ory,orz = self.odeBody.bList[o].getPosition()
			self.objBody[o]['pos'].x = orx
			self.objBody[o]['pos'].y = ory
			self.objBody[o]['pos'].z = orz
			
			oRotation = self.odeBody.bList[o].getRotation()
			#print(oRotation)
			#sys.exit()
			self.objBody[o]['rot'][0].angle = m.degrees(oRotation[0])
			self.objBody[o]['rot'][1].angle = m.degrees(oRotation[2])
			self.objBody[o]['rot'][2].angle = m.degrees(oRotation[1])
			#print("o",o," -> ",oRotation)
			
		#print("2by",by,"yForBoat",yForBoat,"force",self.odeBoat.getForce())
		
	def makeAxis(self):
		PushMatrix()
		pos = Translate(0,0,0)
		rot = [Rotate(1,0,1,0),
			Rotate(1,0,0,1),
			Rotate(1,1,0,0)]
			
		sca = Scale(0.2,0.2,0.2)
		self.d3h.makeMesh("xAxis")
		self.d3h.makeMesh("yAxis")
		self.d3h.makeMesh("zAxis")
		PopMatrix()
		return {
			'pos':pos,
			'rot':rot,
			'sca':sca
			}
			
	def setup_scene(self):
		Color(0.5, 0.5, 0.5,1)
		self.camPos = Translate(1,1,1)
		Rotate(90,90,0)
		PushMatrix()
		Translate(0, -3, -12)
		self.camRot = Rotate(1, 0, 1, 0)
		UpdateNormalMatrix()
		
		PushMatrix()
		self.hdr2Pos = Translate(0,10,0)
		self.hdr2Rot = Rotate(1,0,1,0)
		self.hdr2Heew = Rotate(1,0,0,1)
		self.hdr2Pitch = Rotate(1,1,0,0)		
		Scale(5.0, 4, 5.0)
		self.d3h.makeMesh("hdr2")
		PopMatrix()
		
		print('''
			0 - Center
			1 - B
			2 - S
			3 - Transom
			4 - P
			5 - mast
			''')
		self.objBody = []
		
		for o in range(6):
			PushMatrix()
			ma = self.d3h.makeMesh("box")
			ma['sca'] = [0.1, 0.1, 0.1]
			self.objBody.append( ma )
			PopMatrix()
		#sys.exit()
		
		PushMatrix()
		Scale(0.1,0.1,0.1)
		self.centerAxis = self.makeAxis()
		self.centerAxis['pos'] = [0,0,0]
		print(self.centerAxis.keys())
		print(self.centerAxis['pos'])
		PopMatrix()
		self.oAxisPos = FObject({'x' : self.centerAxis['pos']}) 
		#sys.exit()
		
		# obj to mesh 
		PushMatrix()
		self.boatPos = Translate(0,0,0)
		self.boatRot = Rotate(1,0,1,0)
		self.boatHeew = Rotate(1,0,0,1)
		self.boatPitch = Rotate(1,1,0,0)
		
		boatScale = 0.1
		Scale(boatScale,boatScale,boatScale)
		self.d3h.makeMesh("boat")
		self.d3h.makeMesh("genoa")
		
		PushMatrix()
		self.boatSMainAngle = Rotate(1,0,1,0)
		Scale(boatScale,boatScale,boatScale)
		self.d3h.makeMesh("main")
		self.d3h.makeMesh("boom")
		PopMatrix()
		
		PushMatrix()
		Translate(0,0,6.5)
		self.ruderStockRot = Rotate(1,0,1,0)
		Translate(0,0,-6.5)
		Scale(boatScale,boatScale,boatScale)
		self.d3h.makeMesh("tiler")
		self.d3h.makeMesh("ruder")
		PopMatrix()
		#self.d3h.makeMesh('roseta')
		
		PopMatrix()
		
		
		#box
		
		PushMatrix()
		boxSize = [2.5, 10, 10]
		boxOffset = boxSize[1]*-0.5*boxSize[0]
		bW = boxSize[0]
		Translate(0,-2,0)
		#Scale(10,10,10)
		#self.infWat = self.d3h.makeMesh("infWat")
		
		self.wTiles = {}
		
		if True:
			for x in range(boxSize[1]):
				for y in range(boxSize[2]):
					PushMatrix()
					Translate(boxOffset+(x*bW),-0.5,boxOffset+(y*bW))
					self.wTiles["%s_%s"%(x,y)] = self.d3h.makeMesh("waterTile")
					PopMatrix()
		boxS = 16
		Translate(0,-2,0)
		Scale(boxS*0.89,boxS,boxS*2.44)
		#self.d3h.makeMesh("kap2")
		
		PopMatrix()


		if True:
			#slalom
			PushMatrix()
			boxSize = [2.5, 10, 15]
			boxOffset = boxSize[1]*-0.5*boxSize[0]
			bW = boxSize[0]*10
			if True:
				for y in range(50):
					PushMatrix()
					xRan = random.random()*15.0
					Translate(boxOffset+xRan,-1, boxOffset+(-y*bW) )
					self.d3h.makeMesh("box")
					Translate(10.0, -1, 0.0 )
					self.d3h.makeMesh("box")
					
					
					PopMatrix()
			boxS = 16
			Translate(0,-0,0)
			Scale(boxS*0.89,boxS,boxS*2.44)
			#self.d3h.makeMesh("kap2")
			PopMatrix()

		
		
		

		PopMatrix()

		#self.setArrowsAccel()

class InputsPad(Widget):
	
	def on_changeSettings(self, checkbox, value):
		print("on_changeSettings",value)
	
	def getPadWidget(self):
		cbKeyScreen = CheckBox(
			size_hint=(.1, .1),
			pos=(20, Window.size[1]-100)
			)
		cbKeyScreen.bind( active=self.on_changeSettings )
		
		self.root = cbKeyScreen
		return cbKeyScreen
		

class RendererApp(App):
	def build(self):
		print("Window.size",Window.size)
		lb = FloatLayout(size=Window.size)
		self.d3tex2 = d3tex2()
		self.inputsPad = InputsPad()
		self.pad = self.inputsPad.getPadWidget()
		lb.add_widget(self.d3tex2)
		lb.add_widget(self.pad)
		self.root = lb
		self.lb = lb
		return self.lb

if __name__ == "__main__":
	d3tex2RunAlone = True
	Window.size = (480,640)
	RendererApp().run()
