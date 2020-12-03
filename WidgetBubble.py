
from kivy.uix.widget import Widget
from kivy.core.text import Label
from kivy.graphics.opengl import *
from kivy.graphics import *
from kivy.properties import ObjectProperty
from kivy.core.image import Image as KImage
from kivy.animation import Animation, AnimationTransition
from WidgetValFunctionHandler import WidgetValFunctionHandler


class WidgetBubble(Widget):
	
	
	def __init__(self, **kwargs):
		super(WidgetBubble, self).__init__(**kwargs)
		
		self.pos = [0.0,0.0]
		self.orgSize = [512.0, 160.0]
		self.size = [self.orgSize[0],self.orgSize[1]]
		self.scale = 1.0
		self.rotation = 0.0 
		self.iLevelBg = KImage("icons/ico_level_bg_512_512.png")
		self.iLevelBubble = KImage("icons/ico_level_bubble_256_256.png")
		self.drawIt()
		self.myValue = None
		self.stat = {
            'skip': 0,
            'update': 0
            }
		self.wvfh = WidgetValFunctionHandler()
		#self.wvfh.setParameters()

	def setValuesFromDic(self,dic):
		print("setValuesFromDic",dic)
		self.ImOnScreen = str(dic['screen'])
		self.wvfh.setParametersFromDict(dic['valHandler'])

	def settingsNeedIt(self):
		return True
	
	def getAttrFromDialog(self):
		return {}
	
	def addSettingsDialogPart(self,bl,inWConf=None):
		return bl
		
	def setLevel(self,level):
		#print("setLevel",level)
		if self.gui.animation:
			Animation.cancel_all(self.bubRot,'angle')
			anim = Animation(angle=-level,t='out_quad' )
			anim.start( self.bubRot )
			
		else:
			self.bubRot.angle = -level
		
	def getSize(self):
		return [self.orgSize[0],self.orgSize[1], 1.0, -1.0 ]
		#return self.orgSize
		
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
		with self.canvas:
			self.setColor('w')
			
			PushMatrix()
			self.centPos = Translate(self.size[0]*.5, self.size[1]*.5,0)
			self.comScale = Scale(1,1,1)
			self.comRot = Rotate(0,0,0,1)
			self.r = Rotate(0,0,0,1)
			
			Translate(-self.orgSize[0]*.5,-110.0,0)
			
			
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
			
				
	def update(self, fromWho, vals):
		if( self.gui.rl.current[:7] != 'Widgets' or
			self.ImOnScreen != self.gui.rl.current[7:]
             ):
			return 0
		
		v = self.wvfh.updateVal(fromWho, vals)
		if v != None:
			if self.myValue == None or self.myValue != v:
				self.myValue = v
				self.setLevel( v )
				self.stat['update']+=1
			else:
				self.stat['skip']+=1
				if (self.stat['skip']%50)==0:
					print("widget stat bubble level -> ",self.stat)


	def updateIt(self, *args):
		#print("bubble.updateIt")
		try:
			aoeuobc = self.gui
		except:
			return 0
		
		if self.gui.rl.current[:7] in ["Widgets"]:
			pass
		else:
			return 0
		
	