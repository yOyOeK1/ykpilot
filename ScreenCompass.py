
from kivy.uix.widget import Widget
from kivy.core.text import Label
from kivy.graphics.opengl import *
from kivy.graphics import *
from kivy.properties import ObjectProperty
from kivy.core.window import Window

class ScreenCompass(Widget):
	
	
	def __init__(self, **kwargs):
		super(ScreenCompass, self).__init__(**kwargs)
		
		self.pos = [0.0,0.0]
		self.orgSize = [145.0*2.0, 145.0*2.0]
		self.size = [self.orgSize[0],self.orgSize[1]]
		self.scale = 1.0
		self.rotation = 0.0 
		self.drawIt()
		
	def getSize(self):
		return self.orgSize
		
	def setPos(self, pos):
		print("comapass pos",self.pos," size",self.size)
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
		
	def drawArrow(self,w):
		w = w*0.5+3
		points = [
			-w,145, w, 145,
			w, 130, 0,125,
			-w,130, -w,145
			]
		Line( points=points )
			
	def drawIt(self):
				
		with self.canvas:
			self.setColor('w')
			
			PushMatrix()
			self.centPos = Translate(0,0,0)
			self.comScale = Scale(1,1,1)
			self.comRot = Rotate(0,0,0,1)
			
			# HDG
			PushMatrix()
			self.rHdg = Rotate(0,0,0,-1)
			self.setColor("hdg")
			l = Label(text="HDG", font_size=12)
			l.refresh()
			Rectangle(
				size = l.size, 
				pos = ((0-l.size[0]/2.0),130),
				texture = l.texture
				)
			self.drawArrow(l.size[0])
			self.setColor("w")
			PopMatrix()
			#HDG
			
			self.r = Rotate(0,0,0,1)

			# COG
			PushMatrix()
			self.rCog = Rotate(0,0,0,-1)
			self.setColor("cog")
			l = Label(text="COG", font_size=12)
			l.refresh()
			Rectangle(
				size = l.size, 
				pos = ((0-l.size[0]/2.0),130),
				texture = l.texture
				)
			self.drawArrow(l.size[0])
			self.setColor('w')
			PopMatrix()
			
			# COG
			
			# NESW
			PushMatrix()
			comDir = "NESW"
			for d in comDir:
				l = Label(text=d, font_size=20)
				l.refresh()
				Rectangle(
					size = l.size, 
					pos = ((0-l.size[0]/2.0),70),
					texture = l.texture
					)
				Rotate(-90,0,0,1)
			PopMatrix()
			# NESW
			
			for d in range(0,360,30):
				l = Label(text=str(d), font_size=12)
				l.refresh()
				Rectangle(
					size = l.size, 
					pos = ((0-l.size[0]/2.0),90),
					texture = l.texture
					)
				Rotate(-30,0,0,1)
			
			
			for l5 in range(0,360,5):
				Rotate(5,0,0,1)
				Rectangle(
					pos = (0, 120),
					size = (1, 2)
					)
			
			for l10 in range(0,360,10):
				Rotate(10,0,0,1)
				Rectangle(
					pos = (-1, 106),
					size = (2, 10)
					)
				
			for l45 in range(0,360,45):
				Rotate(45,0,0,1)
				Rectangle(
					pos = (-3, 120),
					size = (6, 10)
					)
			
			self.bind( pos = self.updateIt )
			#self.bind( size = self.updateOfSize )
			#self.bind( scale = self.scale )
			#self.bind( rotation = self.rotation )
			
			PopMatrix()
	
	def updateOfSize(self,a='',b=''):
		print("compass.update of size",self.size,"\na",a,"\nb",b)
			
	def setHdg(self, v):
		self.r.angle = v
		
	def setCog(self, v):
		self.rCog.angle = v
			
			
	def update(self, fromWho, vals):
		if self.gui.rl.current in [ "Compass", 'Widgets']:
			pass
		else:
			return 0
		ms = self.gui.th.getTimestamp(True)
		
		if ( self.gui.sen.comCalAccelGyro.lastTimeIter + 5000000.0 ) < ms:
			#print("comCalAccel not comming old")
			if fromWho == "comCal":
				#print("screenCompass.update got comCal[",vals,"]")
				self.setHdg( int(vals) )
		
		
		if fromWho == 'gps':
			self.setCog( int(vals['bearing']) )
		elif fromWho == 'comCalAccelGyro':
			self.setHdg( int(vals[2]) )
			
	def updateIt(self, *args):
		print("compass.updateIt")
		try:
			aoeuobc = self.gui
		except:
			return 0
		
		if self.gui.rl.current in ["Compass","Widgets"]:
			pass
		else:
			return 0
		
		#self.size[0],self.size[1] = self.orgSize[0],self.orgSize[1]
		
		if 1:
			print("ScreenCompass - > update_rect")
			print(" size parest ", self.parent.size)
			print("	self.orgSize",self.orgSize)
			print(" self size ",self.size)
			print("	self pos ",self.pos)
		#self.rec.pos = self.pos
		#self.rec.size = self.size
		if self.gui.rl.current == 'Compass':
			ws = Window.size
			self.centPos.x = ws[0]*.5
			self.centPos.y = ws[1]*.5-self.gui.btH
			s = (ws[0]/2.0)/140.0
			self.comScale.x = s
			self.comScale.y = s
			self.comScale.z = s
		elif self.gui.rl.current == 'Widgets':
			self.centPos.x = self.pos[0]
			self.centPos.y = self.pos[1]
			self.comScale.x = self.scale
			self.comScale.y = self.scale
			self.comRot.angle = self.rotation
		#self.drawIt()
	