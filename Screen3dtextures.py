
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.core.text import Label
from kivy.resources import resource_find
from kivy.graphics.transformation import Matrix
from kivy.properties import ListProperty, ObjectProperty, NumericProperty
from kivy3dgui.layout3d import *
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.label import Label

from kivy.uix.boxlayout import BoxLayout
import sys,math
from kivy.uix.slider import Slider
from kivy3dgui import node


class boatPos:
	def __init__(self):
		self.pos = [0.45,-6.8, -31.0]
		self.rot = [0.0, 0.0, 0.0,0.0]
		self.sailG = 0.0
		self.sailM = 0.0
		self.sailT = 0.0
		
	
	def setMain(self, s3d,angle):
		self.sailM = angle
		self.setObjAsArray(s3d)
			
		
	def update( self, s3d, what, where, by ):
		if what == 'pos':
			if where == 'x':
				self.pos[0]+= by
			elif where == 'y':
				self.pos[1]+= by
			elif where == 'z':
				self.pos[2]+= by
		if what == 'rot':
			if where == 'x':
				self.rot[0]+= by
			elif where == 'y':
				self.rot[1]+= by
			elif where == 'z':
				self.rot[2]+= by
	
		self.setObjAsArray(s3d)
	
	def setObjAsArray(self,s3d):
		print("boat coordinates set to ")
		print(self.pos)
		print(self.rot)				
		for o in s3d.objs:
			add = 0.0
			rot = self.rot
			xc = math.cos(math.radians(rot[0]))
			xs = math.sin(math.radians(rot[0]))
			yc = math.cos(math.radians(rot[1]))
			ys = math.sin(math.radians(rot[1]))
			zc = math.cos(math.radians(rot[2]))
			zs = math.sin(math.radians(rot[2]))
			print("xc",xc,"	xs",xs,"	yc",yc,"	ys",ys,"	zc",zc,"	zs",zs)

			if "N%s"%o[0] in ["Nmain", "Nboom"]:
				print("main",self.sailM)
				rot = [
					self.rot[0]+self.sailM,
					self.rot[1],
					self.rot[2]
					]
			
			
			
			
			s3d.l.ids["N%s"%o[0]].yaw = rot[0]
			s3d.l.ids["N%s"%o[0]].roll = rot[1]
			s3d.l.ids["N%s"%o[0]].pitch = rot[2]
		
			s3d.l.ids["N%s"%o[0]].translate = self.pos
		
			
class Screen3dtextures:
	
	mesh_texture = ObjectProperty(None)
	
	def __init__(self, **kwargs):
		
		print("make l3d")
		
		self.boatCoor = boatPos()
		self.kShift = False
		
		self.oBoxFile = "./3dModels/3d_box.obj"
		self.objs = [
			['boat',"./3dModels/boat2_3dex_boat.obj","./3dModels/oiysh_profile2.jpeg"],
			#['genoa',"./3dModels/boat2_3dex_sailGenoa_onPower.obj","./3dModels/3d_texture_genoa.jpg"],
			['main',"./3dModels/boat2_3dex_sailMain_sailup_onPower.obj","./3dModels/IMG_5410.jpg"]
			#['boom',"./3dModels/boat2_3dex_boom.obj",""],
			#['ruder',"./3dModels/boat2_3dex_ruder.obj",""],
			#['tiler',"./3dModels/boat2_3dex_tiler.obj",""],
			#['roseta','./3dModels/3d_roseta.obj','']
			
			]

		tp = '''#:kivy 1.0
#: import Layout3D kivy3dgui.layout3d
#: import Animation kivy.animation.Animation
Layout3D:
    id: par
    size_hint: (1.0, 1.0)
    post_processing: True
    
		
    	'''		
		
		for i,oo in enumerate(self.objs):
			tp+= self.kvStr4Obj(oo[0],oo[1],oo[2])
		"""
		boardSize = [3,9]
		tileSize = 4
		xOff = boardSize[0]*tileSize*0.5
		for x in range(0,boardSize[0],1):
			for y in range(0,boardSize[1],1):
				print("tile ",x,"x",y)
				tp+= self.kvStr4Obj(
					"b_%s_%s"%(x,y), 
					self.oBoxFile, 
					"",
					pos=[-xOff+x*tileSize,-8,-y*tileSize]
					)
		"""	
			
		#print("-------------------------")
		#print(tp+"\n--------------------------")
		self.l = Builder.load_string(tp)
		#print("DONE")
		#sys.exit(11)
		
		self.root = self.l
		
		bl = BoxLayout(orientation="vertical")
		b = Button(
			size_hint = (0.1,0.1),
			text="r90",
			size = (10,10
				))
		b.bind(on_release=self.btClick)
			
		bl.add_widget(b)
		
		
		if True:
			axis = ["x","y","z"]
			
			## pos
			blS = BoxLayout(orientation="vertical")
			blS.add_widget(Label(text="Position:"))
			for i,a in enumerate(axis):
				objTid = "sb3dp%s"%a
				objT = Slider(
					id = objTid,
					min = -100.0,
					value = self.boatCoor.pos[i],
					max = 100.0
					)
				objT.bind(on_touch_move=self.onsBTouch)
				blS.add_widget(objT)
			
			## rot
			blS.add_widget(Label(text="Rotation:"))
			for a in axis:
				objTid = "sb3dr%s"%a
				objT = Slider(
					id = objTid,
					min = -180.0,
					value = self.boatCoor.rot[i],
					max = 180.0
					)
				objT.bind(on_touch_move=self.onsBTouch)
				blS.add_widget(objT)
				
				
			## sails
			blS.add_widget(Label(text="Genoa:"))
			objT = Slider(
				id = "sb4dg",
				min = -90.0,
				value = self.boatCoor.rot[i],
				max = 90.0
				)
			objT.bind(on_touch_move=self.onsBTouch)
			blS.add_widget(objT)
			
			blS.add_widget(Label(text="Main:"))
			objT = Slider(
				id = "sb4dm",
				min = -90.0,
				value = self.boatCoor.rot[i],
				max = 90.0
				)
			objT.bind(on_touch_move=self.onsBTouch)
			blS.add_widget(objT)
			
			blS.add_widget(Label(text="Tiller:"))
			objT = Slider(
				id = "sb4dt",
				min = -45.0,
				value = self.boatCoor.rot[i],
				max = 45.0
				)
			objT.bind(on_touch_move=self.onsBTouch)
			blS.add_widget(objT)
			
			
			
			self.l.add_widget(blS)
		
		self.l.add_widget(bl)
		
		self.l.bind(on_touch_down = self.on_touch_down)
		self.l.bind(on_touch_move = self.on_touch_move)
		self.l.bind(on_touch_up = self.on_touch_up)
		
		self.boatCoor.setObjAsArray(self)
		
		print("------------------------------")
		#print(self.l.ids.Nboat)
		#print(self.l.ids.Nboat.rotate)
		#print(self.l.ids.Nboat.yaw)
		#print(self.l.ids.Nboat.roll)
		#print(help(self.l.ids.Nboat))
		
		print("make l3d DONE")
	
	def kvStr4Obj(self,name,filePath, texPath, pos = [0,0,0]):
		print("texPath- ------------",name)
		print(texPath)
		print("type:",type(texPath))
		tr = '''
	Node:
		id: N'''+str(name)+'''
		name: 'N'''+str(name)+''''
		rotate: (0, 0, 0)
		translate: ('''+str(pos[0])+","+str(pos[1])+","+str(pos[2])+''')
		scale: (1.0, 1.0, 1.0)
		min_light_intensity:0.2
		receive_shadows: True
		meshes: ("'''+str(filePath)+'''", )
		Button:
			on_press: app.s3dtextures.onTouchObj("'''+str(name)+'''")
		FloatLayout:
			canvas:
				Color:
					rgb: 1, 1, 1,0.1
				Rectangle:
					size: self.size
					pos: self.pos
					source: "'''+str(texPath)+'''"
				
				'''
		#print("----------returning-----\n",tr,"\n---------------DONE")
		return tr
	
	def onsBTouch(self,obj,v):
		print("onsBtouch",obj," v ",v)
		v = obj.value
		a = obj.id[-1]
		
		if obj.id == 'sb4dg':
			self.boatCoor.sailG = v
		if obj.id == 'sb4dm':
			self.boatCoor.setMain(self, v)
			
		if a == 'x': 
			ai = 0
		elif a == 'y':
			ai = 1
		else:
			ai = 2
			
		print(obj.id[-2]," -- >> v",v," -> a",a)
		
		if obj.id[-2] == 'p':
			self.boatCoor.pos[ai] = v
		elif obj.id[-2] == 'r':
			self.boatCoor.rot[ai] = v
			#pass
		self.boatCoor.setObjAsArray(self)
		
	
	def btClick(self,a=1):
		print("btClick")
		#print(self.l.ids.Nseapod)
		#print(self.l.ids.Nseapod.rotate)
		#print(self.l.ids.Nseapod.translate)
		self.boatCoor.update( self, 'rot', 'x', 10.0 )
	
	def on_touch_down(self, a,b):
		print("on_touch_down",a,b,"pos:",b.x)
		self.mS = [b.x,b.y]
	
	def on_touch_move(self, a,b):
		print("on_touch_move",a,b)
		dx = self.mS[0]-b.x
		dy = self.mS[1]-b.y
		#self.boatCoor.update(self, 'pos', 'x', -dx/10.0)
		#self.boatCoor.update(self, 'pos', 'y', -dy/10.0)
		
		self.mS = [b.x, b.y]
		
		
	def on_touch_up(self, a,b):
		print("on_touch_up",a,b)
		
	def onTouchObj(self,objName):
		print("onTouchObj:",objName)
		
		
	def on_key_up(self,args):
		keyCode = args[2]
		if keyCode == 225:
			print("shift up")
			self.kShift = False
		
		
	def on_key_down(self, args):
		keyCode = args[2]
		
		if self.kShift:
			what = 'rot'
		else:
			what = 'pos'
		
		if keyCode == 225:
			print("shift down")
			self.kShift = True
		
		
		elif keyCode == 82:
			print("up")
			self.boatCoor.update( self, what, 'z', 5 )
		elif keyCode == 81:
			print("down")
			self.boatCoor.update( self, what, 'z', -5 )
		elif keyCode == 80:
			print("left")
			self.boatCoor.update( self, what, 'x', 5 )
		elif keyCode == 79:
			print("right")
			self.boatCoor.update( self, what, 'x', -5 )
		elif keyCode == 75:
			print("left")
			self.boatCoor.update( self, what, 'y', -5 )
		elif keyCode == 78:
			print("right")
			self.boatCoor.update( self, what, 'y', 5 )
			
		
	def setGui(self, gui):
		self.gui = gui
		
		
	def drawIt(self):
		print("Screen3dtextures.drawIt()")
		
		
	# kivyMD
	def fbind(self, *k):
		pass
		