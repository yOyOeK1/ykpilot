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

from kivy.properties import ListProperty, ObjectProperty, NumericProperty
from D3Helper import D3Helper
from kivy.animation import Animation

d3tex2RunAlone = False

class d3tex2(Widget):
		
	def __init__(self, **kwargs):
		self.gui = None
		
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
			['kap2','./3dModels/tile.obj',"./3dModels/kap2.png"]
			
			
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
		
		
		asp = 200.00 / float(200.00)
		proj = Matrix().view_clip(
			-asp,asp,-1, 1, 1, 100, 1)
		self.canvas['projection_mat'] = proj
		#self.canvas['diffuse_light'] = (0.1, 0.0, 0.8)
		#self.canvas['ambient_light'] = (0.5, 0.5, 0.5)
		#self.canvas['texture1'] = 1
		self.camRot.angle += 0.2
		
		"""
		for i in self.meshs.keys():
			m = self.meshs[i]
			m[0].angle = m[0].angle*self.aniSteps+m[1]*(1.00-self.aniSteps)
		"""
		self.camPos.x = self.cam[0]
		self.camPos.y = self.cam[1]
		self.camPos.z = self.cam[2]
		
			
	def setup_scene(self):
		Color(0.5, 0.5, 0.5,1)
		self.camPos = Translate(1,1,1)
		Rotate(90,90,0)
		PushMatrix()
		Translate(0, -3, -12)
		self.camRot = Rotate(1, 0, 1, 0)
		UpdateNormalMatrix()
		
		PushMatrix()
		Translate(0,10,0)
		Scale(5.0, 4, 5.0)
		#self.d3h.makeMesh("hdr2")
		PopMatrix()
		
		PushMatrix()
		Translate(0,0,0)
		Rotate(0,0,0)
		Scale(0.2,0.2,0.2)
		self.d3h.makeMesh("xAxis")
		self.d3h.makeMesh("yAxis")
		self.d3h.makeMesh("zAxis")
		PopMatrix()
		
		
		# obj to mesh 
		self.d3h.makeMesh("roseta")
		self.d3h.makeMesh("boat")
		self.d3h.makeMesh("genoa")
		self.d3h.makeMesh("main")
		self.d3h.makeMesh("boom")
		self.d3h.makeMesh("ruder")
		self.d3h.makeMesh("tiler")
		#self.d3h.makeMesh('roseta')
		
		
		
		#box
		
		PushMatrix()
		boxSize = [2.5, 10, 15]
		boxOffset = boxSize[1]*-0.5*boxSize[0]
		bW = boxSize[0]
		if True:
			for x in range(boxSize[1]):
				for y in range(boxSize[2]):
					PushMatrix()
					Translate(boxOffset+(x*bW),-1,boxOffset+(y*bW))
					self.d3h.makeMesh("waterTile")
					PopMatrix()
		boxS = 16
		Translate(0,-0,0)
		Scale(boxS*0.89,boxS,boxS*2.44)
		#self.d3h.makeMesh("kap2")
		PopMatrix()
		

		PopMatrix()

		#self.setArrowsAccel()

class RendererApp(App):
	def build(self):
		return d3tex2()

if __name__ == "__main__":
	d3tex2RunAlone = True
	Window.size = (480,640)
	RendererApp().run()
