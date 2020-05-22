
from kivy.uix.widget import Widget
from kivy.core.text import Label
from kivy.graphics.opengl import *
from kivy.graphics import *

class ScreenCompass(Widget):
	
	def __init__(self, **kwargs):
		super(ScreenCompass, self).__init__(**kwargs)
		
		self.drawIt()
		
	def setGui(self, gui):
		self.gui = gui
		
		
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
			
			self.centPos = Translate(0,0,0)
			self.comScale = Scale(1,1,1)
			
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
			
			self.bind( 
				pos = self.updateIt, 
				size = self.updateIt
				)
			
	def setHdg(self, v):
		self.r.angle = v
		
	def setCog(self, v):
		self.rCog.angle = v
			
			
	def update(self, fromWho, vals):
		if self.gui.rl.current != "Compass":
			return 0
		
		if fromWho == 'gps':
			self.setCog( int(vals['bearing']) )
		elif fromWho == 'comCal':
			self.setHdg( int(vals) )
		else:
			print("ScreenCompass.update" ,fromWho, vals)
			
	def updateIt(self, *args):
		if self.gui.rl.current != "Compass":
			return 0
		print("ScreenCompass - > update_rect")
		print(" size parest ", self.parent.size)
		#self.rec.pos = self.pos
		#self.rec.size = self.size
		self.centPos.x = self.size[0]/2.0
		self.centPos.y = self.size[1]/2.0
		s = (self.size[0]/2.0)/140.0
		self.comScale.x = s
		self.comScale.y = s
		self.comScale.z = s
		#self.drawIt()
	