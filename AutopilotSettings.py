
from kivy.uix.popup import Popup
from kivy.lang import Builder

Builder.load_file('layoutAutopilotSettings.kv')

class AutopilotSettings(Popup):
	
	def setAction(self,gui):
		self.gui = gui
		config = self.gui.config
		self.title = "Autopilot settings"
		self.ids.cb_AutSetDirRev.active = True if config['apDirectionReverse'] == 1 else False
	
		self.apCommunicationMode = "audio jack" if config['apCommunicationMode'] == "audio jack" else "wifi udp"
		self.ids.sp_apConnectionMode.text = self.apCommunicationMode
		self.ids.ti_apWifiIp.text = "192.168.4.1" if config['apWifiIp'] == None else config['apWifiIp']
		
			
		
	def run(self):
		self.open()
	
	def on_bt_toDefault(self):
		print( "on_bt_toDefault" )
		self.gui.config['apDirectionReverse'] = self.gui.cDefVals['apDirectionReverse']
		self.gui.config['apCommunicationMode'] = self.gui.cDefVals['apCommunicationMode']
		self.gui.config['apWifiIp'] = self.gui.cDefVals['apWifiIp']
		
		self.gui.ap.on_updateSettings()
		self.dismiss()
		self.gui.on_configSave()
		
	def on_guiToConfig(self):
		print("on_guiToConfig")
		self.gui.config['apDirectionReverse'] = 1 if self.ids.cb_AutSetDirRev.active else 0
		self.gui.config['apCommunicationMode'] = self.ids.sp_apConnectionMode.text
		self.gui.config['apWifiIp'] = self.ids.ti_apWifiIp.text
		print("self.gui.config",self.gui.config)
		
		self.gui.ap.on_updateSettings()
		
	def on_bt_save(self):
		print( "on_bt_save" )
		self.on_guiToConfig()
		self.dismiss()
		self.gui.on_configSave()
		
		