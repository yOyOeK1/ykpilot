
from kivy.uix.popup import Popup
from kivy.lang import Builder

Builder.load_file('layoutAutopilotSettings.kv')

class AutopilotSettings(Popup):
	
	def setAction(self,gui):
		self.gui = gui
		config = self.gui.config
		self.title = "Autopilot settings"
		self.ids.cb_AutSetDirRev.active = True if config['apDirectionReverse'] == 1 else False
			
		
	def run(self):
		self.open()
	
	def on_bt_toDefault(self):
		print( "on_bt_toDefault" )
		self.gui.config['apDirectionReverse'] = self.gui.cDefVals['apDirectionReverse']
		
		self.gui.ap.on_updateSettings()
		self.dismiss()
		
	def on_guiToConfig(self):
		print("on_guiToConfig")
		self.gui.config['apDirectionReverse'] = 1 if self.ids.cb_AutSetDirRev.active else 0
		print("self.gui.config['apDirectionReverse']",self.gui.config['apDirectionReverse'])
		
		self.gui.ap.on_updateSettings()
		
	def on_bt_save(self):
		print( "on_bt_save" )
		self.on_guiToConfig()
		self.dismiss()
		
		