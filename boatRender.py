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
from objloader import ObjFile
from modelsLoader import modelsLoader
import math as m

from kivy.properties import ListProperty, ObjectProperty, NumericProperty


class Renderer(Widget):

	mesh_texture = ObjectProperty(None)

	r = 0.0
	aniSteps = 0.86
	aniApli = 1.0
	sailG = 0.0
	meshs = {
		'heel': [None, 0.0 ],
		'pitch': [None, 0.0 ]
		}
	cam = [0.8965517241379324, -0.8965517241379324, -0.6206896551724128]
	boatRot = [0.0,0.0,0.0]
	camPon = None
	objs = {}
	objRot = {}
	
	
	
	
	def __init__(self, **kwargs):
		self.canvas = RenderContext(compute_normal_mat=True)
		self.canvas.shader.source = resource_find('simple.glsl')
		ml = modelsLoader("boat2")
		self.o = ml.getObjects()
		scenRos = ObjFile(resource_find("./3dModels/3d_roseta.obj"))
		self.o['roseta'] = scenRos.objects[ list(scenRos.objects.keys())[0] ]
		print("roseta[%s]"%self.o['roseta'])
		
		
		super(Renderer, self).__init__(**kwargs)
		with self.canvas:
			self.cb = Callback(self.setup_gl_context)
			PushMatrix()
			self.setup_scene()
			PopMatrix()
			self.cb = Callback(self.reset_gl_context)
		
	def on_displayNow(self):	
		self.scheduler = Clock.schedule_interval(self.update_glsl, 1 / 60.)
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
		self.cam = [9.586206896551722, -14.0, 0.0]		
		aniStepsOld = self.aniSteps
		self.aniSteps = 0.00
		self.update_glsl(forceUpdate=True)
		self.update_glsl(forceUpdate=True)
		self.update_glsl(forceUpdate=True)
		#self.cam = [0.8965517241379324, -0.8965517241379324, -0.6206896551724128]
		self.cam = [0.6028708133971286, -6.765550239234449, -14.0]
		self.aniSteps = aniStepsOld
		

	def setCamera(self,axis,angle):
		self.cam[axis] = angle
		print(self.cam)
		
	def setBoatRotation(self,axis, val):
		self.boatRot[axis] = val
	
	def getMainSailObj(self):
		return self.o['sailMain_sailup_onPower']
	
	def setSail(self, angle):
		#self.getMainSail().mrot[1].angle = -angle
		self.o['boom'].mrot[1].angle = -angle
		
		self.o['sailGenoa'].sailAngle.angle = angle*1.1
		if angle > 0:
			self.sailGenoa_scale.x = 1 
			self.sailMain_scale.x = 1
		else:
			self.sailGenoa_scale.x = -1 
			self.sailMain_scale.x = -1
			
	def setHeel(self, angle):
		self.setBoatRotation(2,  angle )
	def setPitch(self,angle):
		self.setBoatRotation(0,  angle )
	def setRoseta(self, angle):
		self.o['roseta'].mrot[1].angle = self.AnimateValue(self.o['roseta'].mrot[1].angle, -angle)
	
	def update(self, fromWho, vals):
		#print("boatRender.update fromWho",fromWho," - ",vals)
		if self.gui.rl.current == "Model Screen" and fromWho == 'comCal':
			self.setRoseta(vals[0])
	
	def setArrowsAccel(self, axis=[]):
		#print("\n\nsetArrowsAccel",axis)
		for i,a in enumerate("XYZ"):
			axis_ = axis[i]
			#print(" -- > ",i,a)
			dif = axis_['last']-axis_['avg']
			fdif = m.fabs(dif)*10.0
			#print(i,a,fdif)
			
			if a == "X":
				self.arrowAxisN_scale = self.arrowAxisX_scale
				self.arrowAxisNm_scale = self.arrowAxisXm_scale
			elif a == "Y":
				self.arrowAxisN_scale = self.arrowAxisY_scale
				self.arrowAxisNm_scale = self.arrowAxisYm_scale
			elif a == "Z":
				self.arrowAxisN_scale = self.arrowAxisZ_scale
				self.arrowAxisNm_scale = self.arrowAxisZm_scale
				
			
			if dif > 0.0:
				self.arrowAxisN_scale.x = 0.0
				self.arrowAxisN_scale.y = 0.0
				self.arrowAxisN_scale.z = 0.0
				self.arrowAxisNm_scale.x = fdif
				self.arrowAxisNm_scale.y = fdif
				self.arrowAxisNm_scale.z = 1.0
			else:
				self.arrowAxisN_scale.x = -fdif
				self.arrowAxisN_scale.y = -fdif
				self.arrowAxisN_scale.z = -fdif
				self.arrowAxisNm_scale.x = 0.0
				self.arrowAxisNm_scale.y = 0.0
				self.arrowAxisNm_scale.z = 0.0
				
	
	def setup_gl_context(self, *args):
		glEnable(GL_DEPTH_TEST)

	def reset_gl_context(self, *args):
		glDisable(GL_DEPTH_TEST)

	def AnimateValue(self, sv, ev):
		return sv*self.aniSteps+ev*(1.00-self.aniSteps)

	def update_glsl(self, *largs, forceUpdate=False):
		if forceUpdate == False:
			if self.gui:
				if self.gui.rl.current != "Model Screen":
					return None
		#print("Model Screen")
		
		
		asp = 200.00 / float(200.00)
		proj = Matrix().view_clip(
			-asp,asp,-1, 1, 1, 100, 1)
		self.canvas['projection_mat'] = proj
		self.canvas['diffuse_light'] = (1.0, 1.0, 0.8)
		self.canvas['ambient_light'] = (0.5, 0.5, 0.5)
		self.rot.angle += 0.2
		
		"""
		for i in self.meshs.keys():
			m = self.meshs[i]
			m[0].angle = m[0].angle*self.aniSteps+m[1]*(1.00-self.aniSteps)
		"""
		self.camPos.x = self.AnimateValue(self.camPos.x,self.cam[0])
		self.camPos.y = self.AnimateValue(self.camPos.y,self.cam[1])
		self.camPos.z = self.AnimateValue(self.camPos.z,self.cam[2])
		
		boat = self.o["boat"]
		for i in range(0,3,1):
			boat.mrot[i].angle = self.AnimateValue(boat.mrot[i].angle, self.boatRot[i])
		#print(self.cam)


		sa = self.o['boom'].mrot[1].angle
		if sa <= 0.0:
			self.getMainSailObj().scale = (1,-1,1,1)
		else:
			self.getMainSailObj().scale = (1,1,1,1)
		self.setSail( -sa - self.sailG )
		if 70.00 > sa > -70.0:
			self.sailG-= self.boatRot[2]*0.01
		else:
			self.sailG = 0.0
			if sa > 0:
				self.setSail(-69.99)
			else:
				self.setSail(69.99)
		#print(".")
	
	def setup_scene(self):
	
		def _draw_element(m):
			m.mrot = [Rotate(0,1,0,0),Rotate(0,0,1,0),Rotate(0,0,0,1)]
			m.mrot = [Rotate(0,-1,0,0),Rotate(0,0,-1,0),Rotate(0,0,0,-1)]
			m.mrot[0].angle = 0.0
			m.mrot[1].angle = 0.0
			m.mrot[2].angle = 0.0
			texture = None
			
			if 0:#m.textureFile != -1:
				
				print("- mesh with texture ",m.textureFile)
				print("	1",self.mesh_texture)
				self.mesh_texture = Image.load('/tmp/g.jpg').texture
				self.mesh_texture.wrap = 'repeat'
				print(" 2",self.mesh_texture)
				mm = Mesh(
					vertices=m.vertices,
					indices=m.indices,
					fmt=m.vertex_format,
					mode='triangles',
					texture = self.mesh_texture
					)
			else:
				print("- mesh without texture")
				Mesh(
					vertices=m.vertices,
					indices=m.indices,
					fmt=m.vertex_format,
					mode='triangles',
				)
			
		Color(1, 1, 1,1)
		self.camPos = Translate(1,1,1)
		Rotate(90,90,0)
		PushMatrix()
		Translate(0, -3, -12)
		self.rot = Rotate(1, 0, 1, 0)
		UpdateNormalMatrix()
		
		o = self.o
		
		# what to display
		if True:
		
			
			PushMatrix()
			_draw_element(o['boat'])

			PushMatrix()
			_draw_element(o['boom'])
			self.sailMain_scale = Scale(1,1,1)
			_draw_element(o['sailMain_sailup_onPower'])
			PopMatrix()
			
			
			PushMatrix()
			UpdateNormalMatrix()
			o['sailGenoa'] = o['sailGenoa_onPower']
			#Rotate(24,-1,0,0)
			Translate(0,0,-7)
			o['sailGenoa'].sailAngle = Rotate(1,0,1,0.39)

			
			Translate(0,0,7)
			self.sailGenoa_scale = Scale(1,1,1)
			_draw_element(o['sailGenoa'])
			PopMatrix()
			
			PushMatrix()
			_draw_element(o['ruder'])
			_draw_element(o['tiler'])
			PopMatrix()
			
			PopMatrix()
			
			
			"""
			keysAxis = "XYZ"
			keysSufix = " m"
			
			for axis in keysAxis:
				print("c",axis)
				for sufix in keysSufix:
					if sufix == " ":
						sufix = ""
					o["aAcc%s%s"%(axis,sufix)] = o['arrowAccel']
			
			
			
			PushMatrix()
			Translate(10,0,0)
			PushMatrix()
			self.arrowAxisX_scale = Scale(1,1,1)
			_draw_element(o['aAccX'])
			PopMatrix()
			Translate(-20,0,0)
			Rotate(180,0,1,1)
			PushMatrix()
			self.arrowAxisXm_scale = Scale(1,1,1)
			_draw_element(o['aAccXm'])
			PopMatrix()
			PopMatrix()
			
			PushMatrix()
			Translate(0,0,-10)
			Rotate(90,0,1,0)
			PushMatrix()
			self.arrowAxisY_scale = Scale(1,1,1)
			_draw_element(o['aAccY'])
			PopMatrix()
			Translate(-20,0,0)
			Rotate(180,0,1,1)
			PushMatrix()
			self.arrowAxisYm_scale = Scale(1,1,1)
			_draw_element(o['aAccYm'])
			PopMatrix()
			PopMatrix()
			
			PushMatrix()
			Translate(0,10,0)
			Rotate(90,0,0,1)
			PushMatrix()
			self.arrowAxisZ_scale = Scale(1,1,1)
			_draw_element(o['aAccZ'])
			PopMatrix()
			Translate(-10,0,0)
			Rotate(180,0,1,1)
			PushMatrix()
			self.arrowAxisZm_scale = Scale(1,1,1)
			_draw_element(o['aAccZm'])
			PopMatrix()
			PopMatrix()
			
			"""
			
			PushMatrix()
			Translate(0,-0.5,0)
			Scale(10.5,1,5,1.5)
			_draw_element(o['roseta'])
			o['roseta'].z = -50.0
			PopMatrix()
		else:
			PushMatrix()
			_draw_element(o['Cube'])
			PopMatrix()
		
		
		
		"""
		for ok in self.scene.objects:
			PushMatrix()
			print(" draw obj [%s]"%ok)
			o = self.scene.objects[ok]			
			_draw_element( o )
			PopMatrix()
		"""
		"""
		boat = self.scene.objects['boat']
		_draw_element(boat)

		sail = self.scene.objects['sailsMain_Plane']
		_draw_element(sail)
		"""
		
		PopMatrix()


		#self.setArrowsAccel()

class RendererApp(App):
	def build(self):
		return Renderer()

if __name__ == "__main__":
	RendererApp().run()
