import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager

from kivy.uix.button import Button
from kivy.uix.label import Label

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.actionbar import ActionBar, ActionPrevious, ActionView,\
	ActionOverflow, ActionButton
from kivy.properties import NumericProperty
from kivy.core.window import Window


from kivy_garden.graph import Graph, MeshLinePlot

from kivy.support import install_twisted_reactor
from kivy.uix.floatlayout import FloatLayout

from shaderTree import ShaderWidget
from shadersDefinition import *
from TimeHelper import *
from FileActions import *
from ScreenAutopilot import *

install_twisted_reactor()

from twisted.internet import reactor
from twisted.internet import protocol

import _thread

from sensors import *
from helperUdp import *
from remotePython import remotePython
from helperTCP import helperTCP
from helperTwistedTcp import *
from boatRender import Renderer
from simRender import simRender
from simEngine import *
from DataSaveRestore import *
from ScreenRace import *
from ScreenCompass import *

from driver1 import *
from driver2 import *
from driver3 import *
from driver4 import *
from driver5 import *
from driver6 import *
from driver7 import *
from driver8 import *
from driver9 import *

if kivy.platform == 'android':

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
		Context.mActivity.getWindow().addFlags( Params.PARTIAL_WAKE_LOCK )
		print( "OK will not go sleep !")	


else:
	Window.size = (480,640)
	Window.set_title( "ykpilot" )
	#pass

class RootLayout(ScreenManager):
	def passGuiApp(self,gui):
		self.gui = gui


class gui(App):
	
	testHDG = 10
	remotePythonPid = None
	
	#npTest = NumericProperty(1)
	
	btH = kivy.metrics.cm(1)
	lineH = kivy.metrics.cm(0.7)
	
	
	
	def __init__(self, *a, **kw):
		super(gui, self).__init__(*a, **kw)
		
		if kivy.platform == 'android':
			self.sensorsRemoteTcp = "host:port" 
		else:
			#self.sensorsRemoteTcp = "192.168.43.208:11223"
			self.sensorsRemoteTcp = "192.168.43.208:11223"
		
		
		self.colorTheme = "day"
	
		
	def build(self):			
		Builder.load_file('layoutMain.kv')

		self.th = TimeHelper()
		self.timeAppStart = self.th.getTimestamp()

		self.config = DataSR_restore('ykpilot.conf')
		if self.config == None:
			self.config = {}
		
		self.sRace = ScreenRace(self)
		self.sCompass = ScreenCompass()
		self.sCompass.setGui(self)
		self.rl = RootLayout()
		self.sRace.setupGui()
		self.rl.ids.blCompass.add_widget( self.sCompass )
		
		
		self.cDefVals = {
			'screenCurrent': 'Sensors', 
			'totalUptime' : 0,
			'totalMiles': 0.0,
			'apDirectionReverse': 0,
			'apDriver': 'driver9'
			}
		
		for k in self.cDefVals.keys():
			try:
				print("config  			",k," -- > ",self.config[k] )
			except:
				print("config default - > no value [",k,"] setting [",self.cDefVals[k],"]")
				self.config[k] = self.cDefVals[k]
		
		self.ap = ScreenAutopilot(self)
		
		if kivy.platform == 'android':
			self.platform = 'android'
			ip = '192.168.43.208'
			senderPort = 11223
			makeRender = True
			"""
			from android import AndroidService
			service = AndroidService("ykpilot background","running ....")
			service.start("service started")
			self.service = service
			"""
			self.workingFolderAdress = '/storage/emulated/0/ykpilot/'

		else:
			self.platform = 'pc'
			ip = '192.168.43.55'
			senderPort = 11225
			makeRender = True
			Clock.schedule_once(self.connectToSensorsRemoteTcp, 2 )
			self.workingFolderAdress = './ykpilot/'

		wfa = self.workingFolderAdress.split("/")
		dirName = wfa[-2]
		self.fa = FileActions()
		try:
			print("working folder adres ",
				self.fa.mkDir(self.workingFolderAdress[:-1])
				)
		except:
			pass
	
	
		#self.tcp = helperTCP(ip)
		self.rl.passGuiApp(self)
		self.sen = sensors(self)
		self.sen.gpsD.addCallBack( self.sRace )
		self.sen.gpsD.addCallBack( self.sCompass )
		self.sen.comCalAccelGyro.addCallBack( self.sCompass )
		self.sen.comCal.addCallBack( self.ap )
		#self.sen.run()


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

		if makeRender:
			#self.rl.current= "Sensors"
			self.senBoat = Renderer()
			self.senBoat.setGui(self)
			self.rl.ids.blModelScreen.add_widget( self.senBoat )


		if True:
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



		print("Sender Server is on port[%s]"%senderPort)
		self.sf = MyServerFactory(self)
		reactor.listenTCP(senderPort, self.sf )
		
		
		
		#action bar
		if True:
			self.mw = BoxLayout(orientation="vertical")
			a = ActionBar()
			av = ActionView()
			a.add_widget(av)
			ap = ActionPrevious( 
				title="ykpilot", with_previous=False,
				app_icon = "icons/ico_sailboat_256_256.png"
				)
			ap.bind(on_release=self.screenChange)
			av.add_widget(ap)

			ao = ActionOverflow()
			ab = ActionButton(text="Sensors",
				icon = "icons/ico_find_256_256.png")
			ab.bind(on_release=self.screenChange)
			av.add_widget(ab)
			ab = ActionButton(text="Model Screen",
				icon = "icons/ico_sailboat_256_256.png")
			ab.bind(on_release=self.screenChange)
			av.add_widget(ab)
			ab = ActionButton(text="Simulator",
				icon = "icons/ico_sum_256_256.png")
			ab.bind(on_release=self.screenChange)
			av.add_widget(ab)

			ab = ActionButton(text="Compass")
			ab.bind(on_release=self.screenChange)
			av.add_widget(ab)
			ab = ActionButton(text="Race",
				icon = "icons/ico_time_256_256.png")
			ab.bind(on_release=self.screenChange)
			av.add_widget(ab)
			ab = ActionButton(text="Autopilot")
			ab.bind(on_release=self.screenChange)
			av.add_widget(ab)


			ab = ActionButton(text="Mic Screen")
			ab.bind(on_release=self.screenChange)
			av.add_widget(ab)

			"""
			ao = ActionOverflow()
			ab = ActionButton(text="Day")
			ab.bind(on_release=self.screenNight)
			av.add_widget(ab)
			ao = ActionOverflow()
			ab = ActionButton(text="Night")
			ab.bind(on_release=self.screenDay)
			av.add_widget(ab)
			"""
			av.add_widget(ao)
			
			self.mw.add_widget(a)
			self.mw.add_widget(self.rl)

			toreturn = self.mw
		else:
			toreturn = self.rl
		# actionbar
		
		#play from file
		toreturn = self.sen.buidPlayer(toreturn)
		#play from file

		#self.ap.setupDriver()
		self.sen.run()
		self.screenChange(self.config['screenCurrent'])
		#Window.set_title("ykpilot")

		#return self.rl 
		return toreturn 


		"""		
		#SHADER TREE
		self.shader_index = 0
		root = FloatLayout()
		self.sw = ShaderWidget()
		root.add_widget(self.sw)
		#bl = BoxLayout(orientation="vertical")
		#bl.add_widget(toreturn)
		#self.sw.add_widget(bl)
		self.sw.add_widget(Button(text="abc"))
		#self.sw.fs = shader_monochrome
		print("sw pos",self.sw.pos)
		print("sw size",self.sw.size)
		return root
		"""		

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
		print( "--------- on pause")
		try:
			self.sen.gps_stop()
		except:
			pass
			
		self.on_configSave()
		
		return True
	
	def on_resume(self):
		print( "------- on resume")
		self.sen.gps_start(1000, 0)
	
	
	def on_configSave(self):
		self.config['screenCurrent'] = self.rl.current
		self.config['totalUptime']+= self.th.getTimestamp()-self.timeAppStart
		
		print("save config res", 
			DataSR_save(self.config, 'ykpilot.conf')
			)
	
	
	# Screen: "Welcome"
	
	def on_push_udp_msg(self):
		udp = helperUdp()
		udp.setAsSender()
		self.testHDG+=1 
		udp.send("$AAHDG,%s,0,W,0,E"%self.testHDG)
	
	def on_push_tcp_msg(self):
		self.testHDG+=1
		self.tcp.sendToAll("$AAHDG,%s,0,W,0,E"%self.testHDG)
		
		
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
	def screenChange(self, screenName):
		if type(screenName) == str:
			sn = screenName
		else:
			try:
				sn = screenName.text
			except:
				sn = screenName.title
				
				
		if self.rl.current == "Model Screen":
			self.senBoat.on_noMoreDisplayd()
				
		self.rl.current = sn
		
		print("screenChange to [%s]"%sn)
		if sn == "Model Screen":
			self.senBoat.on_displayNow()
		if sn == "Autopilot":
			self.ap.updateGui()

		
	def screenNight(self, a):
		self.corolTheme = "night"
		self.sw.fs = shader_red
	def screenDay(self, a):
		self.colorTheme = "day"
		self.sw.fs = shader_red
		
	def screenNightDay(self, a):
		if self.colorTheme == "day":
			self.corolTheme = "night"
		elif self.colorTheme == "night":
			self.colorTheme = "day"
		print("screenNightDay!",self.colorTheme)
		
	
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
		