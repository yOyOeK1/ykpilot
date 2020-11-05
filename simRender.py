from kivy.app import App
 
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.resources import resource_find
from kivy.graphics.transformation import Matrix
from kivy.graphics.opengl import *
from kivy.graphics import *
from objloader import ObjFile
import random


class simRender(Widget):
	
	boards = [0,0,0]
	
	def __init__(self, **kwargs):
		self.canvas = RenderContext(compute_normal_mat=True)
		self.canvas.shader.source = resource_find('simple.glsl')
		self.scene = ObjFile([
#			resource_find("3d_roseta.obj"),
#			resource_find("3d_phone_textured.obj")
			resource_find("./3dModels/3d_board.obj"),
			resource_find("./3dModels/boat.obj"),
			resource_find('./3dModels/3d_box.obj')
			])
		
		self.useWavas = True
		
		if self.useWavas:
			self.waveSize = [15,20,2.5]
			self.wave = []
			for c in range(0,self.waveSize[0]*self.waveSize[1],1):
				self.wave.append(self.scene.objects['Cube'])
		
		else:
			self.scene.objects['board0'] = self.scene.objects['board_Cube']
			self.scene.objects['board1'] = self.scene.objects['board_Cube']
			self.scene.objects['board2'] = self.scene.objects['board_Cube']
			
		self.o = self.scene.objects
		super(simRender, self).__init__(**kwargs)
		with self.canvas:
			self.cb = Callback(self.setup_gl_context)
			PushMatrix()
			self.setup_scene()
			PopMatrix()
			self.cb = Callback(self.reset_gl_context)
		#Clock.schedule_interval(self.update_glsl, 1 / 60.)



	def setSim(self,sim):
		self.sim = sim
	def setGui(self,gui):
		self.gui = gui

	def openScreenAnimation(self):
		print("openScreenAnimation")
		pass

	def setup_gl_context(self, *args):
		glEnable(GL_DEPTH_TEST)

	def reset_gl_context(self, *args):
		glDisable(GL_DEPTH_TEST)

	def AnimateValue(self, sv, ev):
		return sv*self.aniSteps+ev*(1.00-self.aniSteps)

	def update_glsl(self, *largs):
		
		#print("simRender")
		asp = 200.00 / float(200.00)
		proj = Matrix().view_clip(
			-asp,asp,-1, 1, 1, 100, 1)
		self.canvas['projection_mat'] = proj
		self.canvas['diffuse_light'] = (1.0, 1.0, 0.8)
		self.canvas['ambient_light'] = (0.5, 0.5, 0.5)
		#self.rot.angle += 0.2
		
		o = self.scene.objects
		s = self.sim
		b = self.sim.boat

		
		self.gui.rl.ids.sSimRuder.value = s.boat['ruderPos']

		#o['boat'].mrot[1].angle = s.boat['cog']  
		
		if self.useWavas:
			by = self.sim.getW(b['x'],b['y'])[0]
			o['boat'].pos.y = by
			#self.camPos.y = by
			w = 0
			xoff = self.waveSize[0]*-(self.waveSize[2]*0.5)
			yoff = self.waveSize[1]*-(self.waveSize[2]*0.5)
			for x in range(0,self.waveSize[0],1):
				for y in range(0,self.waveSize[1],1):
					ny = yoff+((b['y']%(self.waveSize[2]*1))+(y*self.waveSize[2]))
					nx = xoff-(b['x']%(self.waveSize[2]*1))+(x*self.waveSize[2])
					
					self.wavePos[w].z = ny
					self.wavePos[w].x = nx
						
					wy, wrx, wry = self.sim.getW( nx, ny )
					self.wavePos[w].y = wy
					
					self.waveAngle[w][1].angle = b['cog']-s.targetCog

					
					#self.waveAngle[w][0].angle = wrx
					w+= 1
		else:
			self.boardR.angle = s.boat['cog']-s.targetCog
			self.boards[0].z = -36.00+(s.boat['y']%16.00)
			self.boards[0].x = -s.boat['x']
		
		
	def setup_scene(self):
	
		def _draw_element(m):
			m.mrot = [Rotate(0,1,0,0),Rotate(0,0,1,0),Rotate(0,0,0,1)]
			m.mrot = [Rotate(0,-1,0,0),Rotate(0,0,-1,0),Rotate(0,0,0,-1)]
			m.mrot[0].angle = 0.0
			m.mrot[1].angle = 0.0
			m.mrot[2].angle = 0.0
			
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
		Translate(-1, -6, -16)
		self.rot = Rotate(1, 0, 1, 0)
		UpdateNormalMatrix()
		
		o = self.o
		
		# what to display
		if True:
			if not self.useWavas:
				PushMatrix()
				self.boardR = Rotate(0,0,1,0)
				PushMatrix()
				bDis = 16			
				self.boards[0] = Translate(0,-0.5,-(bDis*2))
				_draw_element(o['board0'])
				self.boards[1] = Translate(0,0,bDis)
				_draw_element(o['board1'])
				self.boards[2] = Translate(0,0,bDis)
				_draw_element(o['board2'])
				PopMatrix()
				PopMatrix()
			
			
			
			
		else:
			PushMatrix()
			_draw_element(o['Cube'])
			PopMatrix()
		
		if self.useWavas:
			PushMatrix()
			Translate(self.waveSize[0]*-(self.waveSize[2]*0.5), 0, self.waveSize[1]*-(self.waveSize[2]*0.5))
			PopMatrix()
			w = 0
			self.wavePos = []
			self.waveAngle = []
			for x in range(0,self.waveSize[0],1):
				for y in range(0,self.waveSize[1],1):
					PushMatrix()
					self.waveAngle.append([
						Rotate(0,0,0,1),
						Rotate(0,0,1,0),
						Rotate(0,1,0,0)
						])
					PushMatrix()
					self.wavePos.append( Translate(x*self.waveSize[2],-0.5,y*self.waveSize[2]) )
					_draw_element( self.wave[w] )
					PopMatrix()
					PopMatrix()
					w+= 1
		
		PushMatrix()
		o['boat'].pos = Translate(0,0,0)
		_draw_element(o['boat'])
		_draw_element(o['sailsMain_Plane'])
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

