
from kivy.uix.widget import Widget
from kivy.core.text import Label
from kivy.graphics.opengl import *
from kivy.graphics import *
from kivy.properties import ObjectProperty
from kivy.core.image import Image as KImage


class WidgetBubble(Widget):
	
	
	def __init__(self, **kwargs):
		super(WidgetBubble, self).__init__(**kwargs)
		
		self.pos = [0.0,0.0]
		self.orgSize = [512.0, 187.0]
		self.size = [self.orgSize[0],self.orgSize[1]]
		self.scale = 1.0
		self.rotation = 0.0 
		self.iLevelBg = KImage("icons/ico_level_bg_512_512.png")
		self.iLevelBubble = KImage("icons/ico_level_bubble_256_256.png")
		self.drawIt()
		
		
	def setLevel(self,level):
		#print("setLevel",level)
		self.bubRot.angle = -level
		
	def getSize(self):
		return self.orgSize
		
	def setPos(self, pos):
		print("bubble pos",self.pos," size",self.size)
		self.pos = pos
		
	def setScale(self, scale):
		self.scale = scale
		
	def setRot(self, rot):
		self.rotation = rot
		
	def setGui(self, gui):
		self.gui = gui
		
	def getWidget(self):
		return self
		
	def setColor(self,t):
		if t == "w":
			Color(1,1,1,1)
		elif t == "b":
			Color(1,1,1,1)
		elif t == "cog":
			Color(0,1,0,1)
		elif t == "hdg":
			Color(1,0,0,1)
		
	def drawIt(self):
		print("drawIt")
		#self.iLevelBg = KImage("icons/ico_level_bg_512_512.png")
		#self.iLevelBubble = KImage("icon/ico_level_bubble_256_256.png")

				
		with self.canvas:
			self.setColor('w')
			
			PushMatrix()
			self.centPos = Translate(0,0,0)
			self.comScale = Scale(1,1,1)
			self.comRot = Rotate(0,0,0,1)
			self.r = Rotate(0,0,0,1)
			
			Translate(-self.orgSize[0]*.5,-90.0,0)
			
			
			Rectangle(
                pos = (0,0),
                texture = self.iLevelBg.texture,
                size = self.iLevelBg.texture.size,
                )
			
			PushMatrix()
			poi = 450.0
			Translate(self.orgSize[0]*.5,poi,0)
			self.bubRot = Rotate(0,0,0,-1)
			Translate(0,-poi+20,0)
			Rectangle(
                pos = (0,0),
                texture = self.iLevelBubble.texture,
                size = [self.iLevelBubble.texture.size[0]*.3,self.iLevelBubble.texture.size[1]*.3]
                )
			PopMatrix()
			
			PopMatrix()
			
			
			self.bind(pos = self.updateIt)
	
	def updateOfSize(self,a='',b=''):
		print("bubble.update of size",self.size,"\na",a,"\nb",b)
			
	def setHdg(self, v):
		self.r.angle = v
		
	def setCog(self, v):
		self.rCog.angle = v
			
			
	def update(self, fromWho, vals):
		if self.gui.rl.current in [ 'Widgets']:
			pass
		else:
			return 0
		if fromWho == "orientation":
			#print("vals",vals)
			self.setLevel( vals[4] )
		
			
	def updateIt(self, *args):
		print("bubble.updateIt")
		try:
			aoeuobc = self.gui
		except:
			return 0
		
		if self.gui.rl.current in ["Widgets"]:
			pass
		else:
			return 0
		
		#self.size[0],self.size[1] = self.orgSize[0],self.orgSize[1]
		
		if 1:
			print("Screenbubble - > update_rect")
			print(" size parest ", self.parent.size)
			print("	self.orgSize",self.orgSize)
			print(" self size ",self.size)
			print("	self pos ",self.pos)
		#self.rec.pos = self.pos
		#self.rec.size = self.size
		if self.gui.rl.current == 'Widgets':
			self.centPos.x = self.pos[0]
			self.centPos.y = self.pos[1]
			self.comScale.x = self.scale
			self.comScale.y = self.scale
			self.comRot.angle = self.rotation
		#self.drawIt()
	