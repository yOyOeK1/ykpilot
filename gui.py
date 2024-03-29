import kivymd
import kivy
#/home/yoyo/.local/share/python-for-android/dists/Aykp7__armeabi-v7a/_python_bundle/_python_bundle/site-packages/kivy/weakmethod.py

import _thread
import sys

#kivymd main stream
from kivymd.app import MDApp as App
from kivy import platform as kplatform
from kivy import metrics as kmetrics
from kivy.support import install_twisted_reactor
#from kivy_garden.graph import Graph, MeshLinePlot, LinePlot, SmoothLinePlot,\
#	ContourPlot, BarPlot, ScatterPlot, PointPlot, VBar, HBar
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.list import ILeftBodyTouch
from kivymd.uix.button import MDIconButton
from kivymd.toast import toast as mdtoast
from kivy.uix.image import Image


install_twisted_reactor()

from twisted.internet import reactor
from twisted.internet import protocol

from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.actionbar import ActionBar, ActionPrevious, ActionView,\
	ActionOverflow, ActionButton
from kivy.properties import NumericProperty,ObjectProperty,StringProperty
from kivy.core.window import Window
#from kivy.core.image import Image
#from kivy_garden.graph import Graph, MeshLinePlot
from kivy.graphics.instructions import RenderContext
mkservice = False


from kivy.core.image import Image as CoreImage

#from shaderTree import ShaderWidget
from shadersDefinition import *

#from odeRTB import odeRTB
	
#from d3DriveIt import d3tex2

#from ScreenVirtualButtons import ScreenVirtualButtons
#try:
#	from ScreenVirtualButtons import ScreenVirtualButtons
#except:
#	pass



from twistedTcpClient import *

from helperUdp import *
from remotePython import remotePython
from helperTCP import helperTCP
from helperTwistedTcp import *
from DataSaveRestore import *

#from Screen3dtextures import *


if kplatform == 'android':

	from jnius import autoclass, PythonJavaClass, java_method, cast
	from android import activity
	from android.runnable import run_on_ui_thread 
	
	
	@run_on_ui_thread
	def dont_go_sleep():
		print( "platform android doing dont go sleep !" )
		Params = autoclass('android.view.WindowManager$LayoutParams')
		if kivy.__version__ == "1.9.1":
			pyactivity = 'org.renpy.android.PythonActivity'
		else:
			pyactivity = 'org.kivy.android.PythonActivity'
		Context = autoclass(pyactivity)	
		Context.mActivity.getWindow().addFlags( 
			#Params.PARTIAL_WAKE_LOCK 
			Params.FLAG_KEEP_SCREEN_ON
			)
		print( "OK will not go sleep !")	


else:
	Window.size = (408,680)
	Window.set_title( "ykpilot" )
	from PCPlot import *
					
	#pass

class LoaderLayout(GridLayout):
	pass

class IconLeftSampleWidget(ILeftBodyTouch, MDIconButton):
	pass

class ykpActionBar(ActionBar):
	pass

class DLabel(MDLabel):
	color = [1,1,1,1]


class MDDLabel(Label):
	pass
	
class MSTitLabel(MDDLabel):
	pass



class RootLayout(ScreenManager):
	
	fs = StringProperty(None)
	
	def __init__(self, **kwargs):
		self.canvas = RenderContext(use_parent_projection=True,
                                    use_parent_modelview=True,
                                    use_parent_frag_modelview=True)
		super(RootLayout, self).__init__(**kwargs)
		

	def update_glsl(self, *largs):
		print("RL.update_glsl")
		
	def on_fs(self, instance, value):
		print("RL.on_fs")
		# set the fragment shader to our source code
		shader = self.canvas.shader
		old_value = shader.fs
		print("old_value",old_value)
		shader.fs = value
		if not shader.success:
			shader.fs = old_value
			#raise Exception('failed')
	
	def passGuiApp(self,gui):
		self.gui = gui


	
class ImageFromTexture(BoxLayout):
	
	
	def __init__(self, **kwargs):
		self.myCanvas = self.canvas
		
		super(ImageFromTexture, self).__init__(**kwargs)
		self.imgTexture = Image(source='./icons/ico_find_64_64.png')
		self.canvas.add(Color(1,.5,1))
		self.r = Rectangle(
			size=self.size, 
			pos = self.pos
			)
		self.canvas.add(self.r)
		self.imgTexture.bind(texture=self.update_texture)
		
	
	def update_texture(self, instance, value):
		print("update_texture",instance," value ",value)
		self.r.texture = value
		#sys.exit(1)


class gui(App):
	
	testHDG = 10
	remotePythonPid = None
	
	
	#npTest = NumericProperty(1)
	
	btH = kmetrics.cm(1)
	lineH = kmetrics.cm(0.7)
	lDynamicLable = ObjectProperty(1)
	
	wifiTcpStatusOpts = {
		'on': "icons/ico_armG_256_256.png",
		'off': "icons/ico_armR_256_256.png"
		}
	wifiTcpStatus = StringProperty("icons/ico_manZle_256_256.png")
		
		
	def __init__(self, *a, **kw):
		super(gui, self).__init__(*a, **kw)
		Builder.load_file('layoutPresets.kv')
		
		if kplatform == 'android':
			self.sensorsRemoteTcp = "host:port" 
		else:
			#self.sensorsRemoteTcp = "192.168.43.208:11223"
			#self.sensorsRemoteTcp = "192.168.43.208:11223"
			self.sensorsRemoteTcp = "192.168.49.199:11223"
		
		self.windowSize = Window.size
		self.isReady = False
		self.plt = None
		self.ips = []
		
		
		
	
	def doLocalIp(self):
		print("- do local ips")
		import subprocess
		
		
		r = subprocess.Popen(['ip','address'], stdout=subprocess.PIPE)
		so,se = r.communicate()
		self.ips = []
		l = so.split()
		print("	got elements",len(l))
		for ii,i in enumerate(l):
			i = str(i)[2:-1]
			#print("i:[",i,']')
			if len(i)>2:
				#if i[-1] == ":":
				#	print("	interface: ",i)
				
				if str(l[ii-1])[2:-1] == 'inet':
					ip = i
					ip = ip.split("/")
					ip = ip[0]
					print("		ip:",ip)
					if ip == "127.0.0.1":
						print("	skip it's local")
					else:
						self.ips.append(ip)
		
		self.rl.ids.l_phoLocIps.text = "{}".format(", ".join(self.ips))
	
		#sys.exit(0)
	
	def build(self):	
		
		print("layoutMyWidgets...")
		Builder.load_file('layoutMyWidgets.kv')
		print("layoutLoader...")
		Builder.load_file('layoutLoader.kv')

		Window.bind(on_key_down=self.on_key_down)
		Window.bind(on_key_up=self.on_key_up)
		
		self.ll = LoaderLayout()
		
		
		#sys.exit(9)
		
		self.loaderStep = 0
		Clock.schedule_once( self.loaderNextStep, 0.1 )
		
		self.colorTheme = "day"
		self.theme_cls.theme_style = "Dark"
		

		
		
		return self.ll
	
	def makeIFT(self,a=1):
		self.ift = ImageFromTexture()
		self.iftii = 0
		self.iftI = [
			'/home/yoyo/Pictures/IMG_20200927_084635.jpg',
			'/home/yoyo/Pictures/filamentChopt.jpg',
			#'/tmp/fig.png'
			]
		self.rl.ids.l_forMfd.add_widget(self.ift)
		
		self.iftIter()

	def iftIter(self,a=0):
		if self.iftii >= 2:
			self.iftii = 0
		
		print("iftIter", self.iftii)
		data = BytesIO(open(self.iftI[self.iftii], "rb").read())
		im = CoreImage(data, ext="jpg", filename="image.jpg")
		#self.ift.canvas.clear()
		self.ift.imgTexture = CoreImage( im, ext='jpg', filename='yy.jpg' )
		self.iftii+=1
	
		Clock.schedule_once(self.iftIter, 1.0)
	
	
	def loaderNextStep(self,a=0,b=0):
		self.loaderStep+=1 
		print("loaderNextStep step now",self.loaderStep)
		
		
		if self.loaderStep == 1:
			if kplatform == 'android':
				self.platform = 'android'
			else:
				self.platform = 'pc'
			
			self.ll.ids.l_loaMaiWin.text = "DONE"
			Clock.schedule_once( self.loaderNextStep, 0.1 )
			
		
		elif self.loaderStep == 2:
			from TimeHelper import TimeHelper
			from FileActions import FileActions
			self.th = TimeHelper()
			self.fa = FileActions()
			self.homeDirPath = self.fa.getHomeDirectoryForApp(
				'ykpilot', 
				kplatform
				)
			print("homeDir",self.homeDirPath)
			#sys.exit(0)
			self.timeAppStart = self.th.getTimestamp()
			Clock.schedule_once( self.loaderNextStep, 0.1 )
			
		elif self.loaderStep == 3:
			self.ll.ids.l_loaHel.text = "DONE"
			Clock.schedule_once( self.loaderNextStep, 0.1 )
			
				
			
		
		elif self.loaderStep == 4:
			bS = self.th.benStart()
			Builder.load_file('layoutMain.kv')
			self.rl = RootLayout()
			self.bE = self.th.benDone(bS,'')
			Clock.schedule_once( self.loaderNextStep, 0.1 )
			
		elif self.loaderStep == 5:
			self.ll.ids.l_appRooLay.text = "DONE in %s sec."%self.bE
			Clock.schedule_once( self.loaderNextStep, 0.1 )
			
				
		elif self.loaderStep == 6:
			bS = self.th.benStart()
			Builder.load_file('layoutActionBar.kv')
			self.ab = ykpActionBar()
			self.bE = self.th.benDone(bS,'')
			Clock.schedule_once( self.loaderNextStep, 0.1 )
			
		elif self.loaderStep == 7:
			self.ll.ids.l_actBarLay.text = "DONE in %s sec."%self.bE
			Clock.schedule_once( self.loaderNextStep, 0.1 )
			
			
			
		elif self.loaderStep == 8:
			bS = self.th.benStart()
			self.config = DataSR_restore(
				self.fa.join( self.homeDirPath,'ykpilot.conf')
				)
			if self.config == None:
				self.config = {}
			self.doLocalIp()
			self.bE = self.th.benDone(bS, "")
			Clock.schedule_once( self.loaderNextStep, 0.1 )
			
		elif self.loaderStep == 9:
			self.ll.ids.l_loaCon.text = "DONE in %s sec."%self.bE
			Clock.schedule_once( self.loaderNextStep, 0.1 )
			
		
		elif self.loaderStep == 10:
			bS = self.th.benStart()
			if kplatform == 'android':
				self.platform = 'android'
				self.animation = False
				ipSens = '192.168.43.56'
				if len(self.ips)>0:
					ipSens = self.ips[0]			
				ip = ipSens
				self.senderIp = ip
				self.senderPort = 11223
				makeRender = True
				print("- setting up a sensor server at ",ipSens,":",self.senderPort)
				
				# android service
				if mkservice:
					from android import AndroidService
					service = AndroidService("ykpilot background","running ....")
					service.start("service started")
					self.service = service
				# android service
	
				self.workingFolderAdress = '/storage/emulated/0/ykpilot/'
				self.virtualButtons = False
	
			else:
				self.platform = 'pc'
				self.animation = True
				ipSens = '192.168.43.56'
				if len(self.ips)>0:
					ipSens = self.ips[0]			
				ip = ipSens
				self.senderIp = ip
				self.senderPort = 11225
				makeRender = True
				self.workingFolderAdress = './ykpilot/'
				self.virtualButtons = False
	
			self.bE = self.th.benDone(bS, "")
			Clock.schedule_once( self.loaderNextStep, 0.1 )
			
		elif self.loaderStep == 11:
			self.ll.ids.l_loaPlaChk.text = "DONE in %s sec."%self.bE
			Clock.schedule_once( self.loaderNextStep, 0.1 )
			
		
		elif self.loaderStep == 12:
			bS = self.th.benStart()
			print("preloaderStep0")
			self.loaderStep0()
			print("postloaderStep0")
			self.bE = self.th.benDone(bS, "")
			#Clock.schedule_once( 
			self.loaderNextStep()#, 0.1 )
			
		elif self.loaderStep == 13:
			self.ll.ids.l_loaRest.text = "DONE in %s sec."%self.bE
			Clock.schedule_once( self.loaderNextStep, 0.5 )
			
			
			
		elif self.loaderStep == 14:
			bS = self.th.benStart()
			from sensors import sensors
			self.sen = sensors(self)
			print("pre ask for permissions")
			self.sen.askForPermissions()
			print("post ask for permissions")
			self.bE = self.th.benDone(bS, "")
			
			Clock.schedule_once( self.loaderNextStep, 0.5 )
			
		elif self.loaderStep == 15:
			if self.platform == 'android' and self.sen.permissonsStatus == False:
				self.loaderStep-=1
			else:
				self.ll.ids.l_permissions.text = "DONE in %s sec."%self.bE
				
				
			Clock.schedule_once( self.loaderNextStep, 0.1 )
			


		elif self.loaderStep == 16:
			bS = self.th.benStart()
			
			self.sen.makeSensors()
			p = self.rl.parent
			p.remove_widget(self.rl)
			rl = self.sen.buidPlayer(self.rl)
			p.add_widget(rl)
			#self.sen.run()
			#try:
			#	self.sen.gps_start(1000, 0)
			#except:
			#	print("EE - can't start sen.gps")
			#	print(sys.exc_info())
			#	pass
			
			self.bE = self.th.benDone(bS, "")
			Clock.schedule_once( self.loaderNextStep, 0.1 )
			
		elif self.loaderStep == 17:
			self.ll.ids.l_sensors.text = "DONE in %s sec."%self.bE
			Clock.schedule_once( self.loaderNextStep, 0.1 )
			
		
		
		elif self.loaderStep == 18:
			bS = self.th.benStart()
			from ScreenWidgets import ScreenWidgets
			self.sWidgets = ScreenWidgets(self)
			self.sWidgets.setGui()
			self.bE = self.th.benDone(bS, "")
			Clock.schedule_once( self.loaderNextStep, 0.1 )
			
		elif self.loaderStep == 19:
			self.ll.ids.l_loaSWid.text = "DONE in %s sec."%self.bE
			Clock.schedule_once( self.loaderNextStep, 0.1 )
		
		
		
		elif self.loaderStep == 20:
			bS = self.th.benStart()
			from ScreenAutopilot import ScreenAutopilot
			self.ap = ScreenAutopilot(self)
			self.bE = self.th.benDone(bS, "")
			Clock.schedule_once( self.loaderNextStep, 0.1 )
			
		elif self.loaderStep == 21:
			self.ll.ids.l_loaSAut.text = "DONE in %s sec."%self.bE
			Clock.schedule_once( self.loaderNextStep, 0.1 )
		
		
		
		elif self.loaderStep == 22:
			bS = self.th.benStart()
			from ScreenRace import ScreenRace
			self.sRace = ScreenRace(self)
			self.sRace.setupGui()
			self.bE = self.th.benDone(bS, "")
			Clock.schedule_once( self.loaderNextStep, 0.1 )
			
		elif self.loaderStep == 23:
			self.ll.ids.l_loaSRac.text = "DONE in %s sec."%self.bE
			Clock.schedule_once( self.loaderNextStep, 0.1 )
			
			
			
		elif self.loaderStep == 24:
			bS = self.th.benStart()
			from ScreenCompass import ScreenCompass
			self.sCompass = ScreenCompass()
			self.sCompass.setGui(self)
			self.rl.ids.blCompass.add_widget( self.sCompass )
			self.bE = self.th.benDone(bS, "")
			Clock.schedule_once( self.loaderNextStep, 0.1 )
			
		elif self.loaderStep == 25:
			self.ll.ids.l_loaSCom.text = "DONE in %s sec."%self.bE
			Clock.schedule_once( self.loaderNextStep, 0.1 )
		
		
		
		elif self.loaderStep == 26:
			bS = self.th.benStart()
			from ScreenNMEAMultiplexer import ScreenNMEAMultiplexer
			self.sNMEAMul = ScreenNMEAMultiplexer()
			self.sNMEAMul.setGui(self)
			self.bE = self.th.benDone(bS, "")
			Clock.schedule_once( self.loaderNextStep, 0.1 )
			
		elif self.loaderStep == 27:
			self.ll.ids.l_loaSMul.text = "DONE in %s sec."%self.bE
			Clock.schedule_once( self.loaderNextStep, 0.1 )


		
		elif self.loaderStep == 28:
			bS = self.th.benStart()	
			from boatRender import Renderer		
			self.senBoat = Renderer()
			self.senBoat.setGui(self)
			self.rl.ids.blModelScreen.add_widget( self.senBoat )
			self.bE = self.th.benDone(bS, "")
			Clock.schedule_once( self.loaderNextStep, 0.1 )
			
		elif self.loaderStep == 29:
			self.ll.ids.l_loaMScr.text = "DONE in %s sec."%self.bE
			Clock.schedule_once( self.loaderNextStep, 0.1 )

		
		
		elif self.loaderStep == 30:
			bS = self.th.benStart()
			from simRender import simRender
			from simEngine import simEngine
			from driver1 import driver1
			from driver2 import driver2
			from driver3 import driver3
			from driver4 import driver4
			from driver5 import driver5
			from driver6 import driver6
			from driver7 import driver7
			from driver8 import driver8
			from driver9 import driver9
			from driver10 import driver10

			self.simRen = simRender()
			self.simEng = simEngine(self,self.simRen)
			self.simRen.setSim(self.simEng)
			self.simRen.setGui(self)
			self.simEng.renderFrame()

			self.rl.ids.blSimulator.add_widget( self.simRen )

			self.driver1 = driver1(self.simEng)
			self.driver2 = driver2(self.simEng)
			self.driver3 = driver3(self.simEng)
			self.driver4 = driver4(self.simEng)
			self.driver5 = driver5(self.simEng)
			self.driver6 = driver6(self.simEng)
			self.driver7 = driver7(self.simEng)
			self.driver8 = driver8(self.simEng)
			self.driver9 = driver9(self.simEng)
			self.driver10 = driver10(self.simEng)
			
			self.bE = self.th.benDone(bS, "")
			Clock.schedule_once( self.loaderNextStep, 0.1 )
			
		elif self.loaderStep == 31:
			self.ll.ids.l_loaSSim.text = "DONE in %s sec."%self.bE
			Clock.schedule_once( self.loaderNextStep, 0.1 )
		

		
		
		elif self.loaderStep == 32:
			bS = self.th.benStart()
			print("Sender Server is on port[%s]"%self.senderPort)
			self.sf = MyServerFactory(self)
			reactor.listenTCP(self.senderPort, self.sf )
			self.bE = self.th.benDone(bS, "")
			Clock.schedule_once( self.loaderNextStep, 0.1 )
			
		elif self.loaderStep == 33:
			self.ll.ids.l_loaTcpSer.text = "DONE in %s sec."%self.bE
			Clock.schedule_once( self.loaderNextStep, 0.1 )
		
		
		
		elif self.loaderStep == 34:
			bS = self.th.benStart()
			self.tcp4ap = ttc(self)
			self.bE = self.th.benDone(bS, "")
			Clock.schedule_once( self.loaderNextStep, 0.1 )
			
		elif self.loaderStep == 35:
			self.ll.ids.l_AutoWifiArmTCP.text = "DONE in %s sec."%self.bE
			Clock.schedule_once( self.loaderNextStep, 0.1 )
		
	
	
		elif self.loaderStep == 36:
			bS = self.th.benStart()
			from ScreenTriangulacja import Triangulacja, TrianAddDialog
			self.triangulacja = Triangulacja(self)
			self.bE = self.th.benDone(bS, "")
			Clock.schedule_once( self.loaderNextStep, 0.1 )
			
		elif self.loaderStep == 37:
			self.ll.ids.l_Tri.text = "DONE in %s sec."%self.bE
			Clock.schedule_once( self.loaderNextStep, 0.1 )
	
	
		elif self.loaderStep == 38:
			bS = self.th.benStart()
			from ScreenTakePhoto import ScreenTakePhoto
			self.stp = ScreenTakePhoto(self)
			self.bE = self.th.benDone(bS, "")
			Clock.schedule_once( self.loaderNextStep, 0.1 )
			
		elif self.loaderStep == 39:
			self.ll.ids.l_takPho.text = "DONE in %s sec."%self.bE
			Clock.schedule_once( self.loaderNextStep, 0.1 )
	
		
		elif self.loaderStep == 40:
			bS = self.th.benStart()
			from ScreenSensors import ScreenSensors
			self.sSensors = ScreenSensors()
			self.sSensors.setGui(self)
			self.bE = self.th.benDone(bS, "")
			Clock.schedule_once( self.loaderNextStep, 0.1 )
			
		elif self.loaderStep == 41:
			self.ll.ids.l_screSen.text = "DONE in %s sec."%self.bE
			Clock.schedule_once( self.loaderNextStep, 0.1 )
			
		
		
		
		
		elif self.loaderStep == 999:
			bS = self.th.benStart()
			
			self.bE = self.th.benDone(bS, "")
			Clock.schedule_once( self.loaderNextStep, 0.1 )
			
		elif self.loaderStep == 1000:
			#self.ll.ids.l_loaSWid.text = "DONE in %s sec."%self.bE
			Clock.schedule_once( self.loaderNextStep, 0.1 )
		
		
		
		
		
		
		else:
			print(" loader finished ?")
				
				
			print(" starting main loop for sensors ")
			self.sen.run()
		
		
		
			
		
		
			if self.sen.gpsD.androidServiceStatus == False:
				try:
					self.sen.gps_start(1000, 0)
				except:
					print("EE - can't gps_start :(")
			
			
			
			self.sen.gpsD.addCallBack( self.sCompass,'Compass' )
			self.sen.comCal.addCallBack( self.sCompass,'Compass' )
			self.sen.comCalAccelGyro.addCallBack( self.sCompass,'Compass' )
			self.sen.gpsD.addCallBack( self.sRace )
			self.sen.comCal.addCallBack( self.ap )
			self.sen.comCal.addCallBack( self.sen )
			self.sen.comCal.addCallBack( self.senBoat )
			#self.gui.senBoat.setRoseta( self.hdg )
			
			#Clock.schedule_once(self.sen.on_PlayFromFile_play, 1.0)
			#Clock.schedule_once(self.sWidgets.on_addEditDelButton, 1.0)
			#Clock.schedule_once(self.sWidgets.rebuildWs, 5.0)
		
			print("starting listener for sensors :) if pc")
			if self.platform == 'pc':
				Clock.schedule_once(self.connectToSensorsRemoteTcp, 1 )
				
				#if 1:
				#	self.plt = PCPlot(self)
				
		
			print('flip layouts....')
			par = self.ll.parent
			par.remove_widget(self.ll)
			par.add_widget(self.rootLayout)
			self.ll = None
			print("	DONE")
			
			
			if self.config['apCommunicationMode'] == 'wifi tcp':
				self.ap.startTcp()
			
			print("config",self.config)
			defScreen = 'ykpilot'
			goToScreen = defScreen
			dontStartAt = ['Loader','EditWidget', 'SettingUpWidget', 'SelectWidgetToAdd']
			try:
				goToScreen = self.config['screenCurrent']
			except:
				print("EE - no def  config['screenCurrent'] :/")
			
			if goToScreen in dontStartAt:
				print("goToScreen is in dont start list")
				goToScreen = defScreen
				
			print("go to screen is ",goToScreen)
			try:
				self.screenChange(goToScreen)
			except:
				print("EE - no screen [",goToScreen,"] in screenmanager")
				self.screenChange(defScreen)
			
		
			#multiplexer screen
			self.rl.ids.cb_nmeBSensors.active = True if self.config['nmeBSensors'] else False
			self.rl.ids.cb_nmeBAutopilot.active = True if self.config['nmeBAutopilot'] else False
			self.rl.ids.cb_nmeBNmea.active = True if self.config['nmeBNmea'] else False
			
			self.triangulacja.isReady()	
			
			
			#self.makeIFT()
			
			self.isReady = True
			
		
		
	def on_gotECPUStr(self,buf):
		print("on_gotECPUStr",buf)
		
	def loaderStep0(self):
		
		#self.s3dtextures = Screen3dtextures()
		#self.s3dtextures.setGui(self)
		#self.rl.ids.bl3dtextures.add_widget( self.s3dtextures.l )
				
		self.cDefVals = {
			'screenCurrent': 'Sensors', 
			'totalUptime' : 0,
			'totalMiles': 0.0,
			'apDirectionReverse': 0,
			'apDriver': 'driver9',
			'apCommunicationMode': "audio jack",
			'apWifiIp': '192.168.4.1',
			'nmeBSensors': 0,
			'nmeBAutopilot': 0,
			'nmeBNmea': 1
			}
		
		for k in self.cDefVals.keys():
			try:
				print("config  			",k," -- > ",self.config[k] )
			except:
				print("config default - > no value [",k,"] setting [",self.cDefVals[k],"]")
				self.config[k] = self.cDefVals[k]
		
		
		
		print(1)
		#if self.virtualButtons:
		#	self.vBut = ScreenVirtualButtons(self)
		#
		print(2)
		'''
		wfa = self.workingFolderAdress.split("/")
		dirName = wfa[-2]

		try:
			print("working folder adres ",
				self.fa.mkDir(self.workingFolderAdress[:-1])
				)
		except:
			pass
		'''
	
		#self.tcp = helperTCP(ip)
		self.rl.passGuiApp(self)
		print(4)
		
		#self.sen.run()

		

		"""
		self.graph = Graph(xlabel='time', ylabel="angle", x_ticks_minor=1,
			ymax=1.0,ymin=0.0			
			)
		self.pPitch = MeshLinePlot(color=[1,1,0,1])
		self.pHeel = MeshLinePlot(color=[1,0,1,1])
		self.graph.add_plot(self.pPitch)
		self.graph.add_plot(self.pHeel)
		self.rl.ids.blModSimGra.add_widget(self.graph)

		self.graphGyro = Graph(xlabel='time', ylabel="gyro", x_ticks_minor=1,
			ymax=1.0,ymin=0.0			
			)
		self.pgx = MeshLinePlot(color=[1,1,0,1])
		self.pgy = MeshLinePlot(color=[1,0,1,1])
		self.pgz = MeshLinePlot(color=[1,0,0,1])
		self.graphGyro.add_plot(self.pgx)
		self.graphGyro.add_plot(self.pgy)
		self.graphGyro.add_plot(self.pgz)
		self.rl.ids.blModSimGra.add_widget(self.graphGyro)


		self.graphFFT = Graph(xlabel="Hz Heel", ylabel="Db Heel", ymax=1.0, ymin=0.0)
		self.pFFTHeel = MeshLinePlot(color=[1,0,0,1])
		self.pFFTPitch = MeshLinePlot(color=[0,1,0,1])
		self.pFFTUD = MeshLinePlot(color=[0,0,1,1])

		self.graphFFT.add_plot(self.pFFTHeel)
		self.graphFFT.add_plot(self.pFFTPitch)
		self.graphFFT.add_plot(self.pFFTUD)
		self.rl.ids.blModSimFFT.add_widget( self.graphFFT )

		self.compasGyro = Graph(xlabel='time', ylabel="compas", x_ticks_minor=1,
			ymax=1.0,ymin=0.0			
			)
		self.pc = MeshLinePlot(color=[1,1,0,1])
		self.compasGyro.add_plot(self.pc)
		self.rl.ids.blModSimGra.add_widget(self.compasGyro)

		self.graphMic = Graph(xlabel="Hz mic", ylabel="Db mic", ymax=1.0, ymin=0.0)
		self.pMic = MeshLinePlot(color=[1,0,0,1])
		self.pMic1 = MeshLinePlot(color=[0,1,0,1])
		self.pMic2 = MeshLinePlot(color=[0,0,1,1])
		self.graphMic.add_plot(self.pMic)
		self.graphMic.add_plot(self.pMic1)
		self.graphMic.add_plot(self.pMic2)
		self.rl.ids.blMicScre.add_widget(self.graphMic)
		"""
		
		
		#self.d3tex2 = d3tex2()
		#self.d3tex2.setGui(self)
		#self.rl.ids.bl3dtextures2.add_widget( self.d3tex2 )

		
		
		
		
		print(5)
		#action bar
		if True:
			self.mw = BoxLayout(orientation="vertical")
			
			print(7)
			
			self.mw.add_widget(self.ab)
			self.mw.add_widget(self.rl)
			print(8)
			self.rootLayout = self.mw
		else:
			self.rootLayout = self.rl
		# actionbar
		print(9)
		
			
		#self.sWidgets.setUpGui()


		#self.ap.setupDriver()
		
		#Window.set_title("ykpilot")



		#self.ode = odeRTB(self)
		#self.sen.accel.addCallBack(self.ode)

	
	def hide_widget(self, wid, dohide=True):
		if hasattr(wid, 'saved_attrs'):
			if not dohide:
				wid.height, wid.size_hint_y, wid.opacity, wid.disabled = wid.saved_attrs
				del wid.saved_attrs
		elif dohide:
			wid.saved_attrs = wid.height, wid.size_hint_y, wid.opacity, wid.disabled
			wid.height, wid.size_hint_y, wid.opacity, wid.disabled = 0, None, 0, True


	def on_start(self):
		print( "-------- on_start" )
		try:
			dont_go_sleep()
		except:
			pass
		
		
	def on_pause(self):
		if self.isReady:
			print( "--------- on pause")
			try:
				self.sen.gps_stop()
			except:
				pass
				
			self.on_configSave()
		
		return True
	
	def on_resume(self):
		print( "------- on resume")
		try:
			abcaa = self.sen
			self.sen.gps_start(1000, 0)
		except:
			print("EE - no self.sen or other gps error")
	
	
	def on_configSave(self):
		if self.rl.current not in ['TriangulateDialogs']:
			self.config['screenCurrent'] = self.rl.current
		self.config['totalUptime']+= self.th.getTimestamp()-self.timeAppStart
		
		print("save config res", DataSR_save(
				self.config, 
				self.fa.join( self.homeDirPath,'ykpilot.conf')
				)
			)
		
		print("odometer....")
		try:
			abcue = self.sen
			self.sen.odometer.saveData()
		except:
			pass
	
		print("save widgets config")
		try:
			print("	res",self.sWidgets.saveConfig())
		except:
			print("EE - trying to save sWidget but it is not there yet !")
	
	
	def on_makeToast(self, msg):
		mdtoast(msg)
	
	def on_takePhotoTest(self):
		print("on_takePhotoTest")
		d = DLabel(text="abc")
		self.stp.takePhoto(
			self.on_takePhotoTestDone,
			d
			)
	
	def on_takePhotoTestDone(self, status, fileName):
		print("on_takePhotoTestDone<",status)
	
	
	def on_fullScreen(self, status):
		print("on_fullScreen status",status)
		if status:
			self.gui_ab_height = self.ab.height
			self.ab.height = 0.0
		else:
			self.ab.height = self.gui_ab_height
	
	def on_toggleFullScreen(self):
		print("on_toggleFullScreen",self.ab.height)
		if self.ab.height > 0.0:
			self.on_fullScreen(True)
		else:
			self.on_fullScreen(False)
	
	# Screen: "Welcome"
	
	def on_push_udp_msg(self):
		udp = helperUdp()
		udp.setAsSender()
		self.testHDG+=1 
		udp.send("$AAHDG,%s,0,W,0,E"%self.testHDG)
	
	def on_triAddPress(self, a=0,b=0):
		print("on_triAddPress")
	
	def on_push_tcp_msg(self):
		self.testHDG+=1
		self.tcp.sendToAll("$AAHDG,%s,0,W,0,E"%self.testHDG)
		
	def doBranch(self,widget,level,search):
		p = ""
		for i in range(level):
			p+= " "
			
		for i,c in enumerate(widget.walk(restrict=True)):
			if i >= 1:
				print(p,level,"i",i," - id:",c.id,"	",c)
				parent = None
				#while True:
				#	try:
				#		if parent == None:
				#			parent = c
						
						#print(p,"parent",parent)
						#print(p,"id:",parent.id)
						#print(p,"pos",parent.pos)
						#print(p,"size:",parent.size)
				#		parent = parent.parent
						
				#	except:
				#		break
						
						
				try:
					abc = str(c).index(search)
					print(p,"got IT!")
					return None
				except:
					self.doBranch(c, level+1, search)
		
		''''p = ""
		for i in range(level):
			p+= " "
		print(p,"doBranch children",len(widget.content.children))
		for c in widget.content.chirdren:
			print(p,"-",c)
			try:
				abc = c.index(search)
				print(p," got it !")
				return None
			except:
				if len(c.content.chirdren) > 0:
					self.doBranch(c, level+1, search)
		'''	
		
	def on_findWidgetByAdres(self, text):
		print("on_findWidgetByAdres",text)
		print("search for [",text,"]")
		self.doBranch(self.rootLayout, 0, text)
		
		
	def on_cb_nmeB(self, what, obj):
		status = 1 if obj.active else 0
		print("on_cb_nmeB",what," - >",status)
		if what == 'sensors':
			self.config['nmeBSensors'] = status
		elif what == 'autopilot':
			self.config['nmeBAutopilot'] = status
		elif what == 'nmea':
			self.config['nmeBNmea'] = status
			
		self.on_configSave()
		
		
	def on_cb_remotePython(self,checkbox):
		print( checkbox.active )
		if checkbox.active:
			rp = remotePython()
			_thread.start_new(rp.run,())
			
	def on_cb_twistedTcp(self,checkobx):
		pass
	
	def on_push_sensorsInit(self):
		print("android host ------------------")
		self.sen.gps_start(1000,0)
		print("sensors object !")
		
		print("sensors running :)")
	
	# actionbar
	def screenChange(self, screenName = '',b=''):
		print("screenChange",screenName,' b:',b)
		if type(screenName) == str:
			sn = screenName
		else:
			try:
				sn = screenName.text
			except:
				sn = screenName.title
				
				
		if self.rl.current == "Model Screen":
			self.senBoat.on_noMoreDisplayd()
		if self.virtualButtons and self.rl.current == "Virtual Buttons":
			self.vBut.on_noMoreDisplayd()
			
				
		self.rl.current = sn
		
		print("screenChange to [%s]"%sn)
		if sn == "Model Screen" :
			self.senBoat.on_displayNow()
		if sn[:7] in ['Compass','Widgets']:
			print("make updateIt on sn change")
			if sn == 'Compass':
				self.sCompass.updateIt()
			elif sn[:7] == 'Widgets':
				self.sWidgets.updateIt()
				
		if self.virtualButtons and sn == "Virtual Buttons":
			self.vBut.on_displayNow()
		if sn == "Autopilot":
			self.ap.updateGui()
		if self.rl.current == "3dtextures2":
			self.d3tex2.on_displayNow()

		

		
	def screenNight(self, a=0):
		print("screenNight")
		self.corolTheme = "night"
		self.rl.fs = shader_red
		
	def screenDay(self, a=0):
		print("screenDay")
		self.colorTheme = "day"
		self.rl.fs = shader_day
				
		
	def screenNightDay(self, a=0):
		if self.colorTheme == "day":
			self.corolTheme = "night"
		elif self.colorTheme == "night":
			self.colorTheme = "day"
		print("screenNightDay!",self.colorTheme)
		
	
	def on_touch_down(self, touch):
		print('down',touch.x, touch.y)
		if 0:#collide_point:
			return True
		return False

	def on_touch_up(self, touch):
		print('up',touch.x, touch.y)
		if 0:#collide_point:
			return True
		return False

	
	def on_key_down(self, *args):
		print("on_key_down",list(args))
		if self.isReady:
			if self.rl.current == '3dtextures':
				self.s3dtextures.on_key_down(list(args))
		
	
	
	def on_key_up(self, *args):
		print("on_key_up",list(args))
		if self.isReady:
			if self.rl.current == 'Simulator':
				self.simEng.on_key_up(list(args))
			elif self.rl.current == '3dtextures':
				self.s3dtextures.on_key_up(list(args))
		
	
	
	# screen: "Model Screen"
	def on_touchSail(self, slider):
		self.senBoat.setSail(slider.value)
	def on_touchHeel(self, slider):
		self.senBoat.setHeel(slider.value)
		
	# screen: "Sensors"
	def on_cb_sensorsRemoteTcp(self, checkbox):
		if checkbox.active:
			self.connectToSensorsRemoteTcp(0)
			
	def connectToSensorsRemoteTcp(self,a):
		self.rl.ids.cb_sensorsRemoteTcp.active = True
		self.cf = MyClientFactory(self)
		ip,port = str(self.rl.ids.ti_sensorsRemoteTcp.text).split(":")
		reactor.connectTCP(str(ip),int(port),self.cf)
		