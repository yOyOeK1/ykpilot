
from kivy.uix.popup import Popup
from kivy.lang import Builder

Builder.load_file('layoutQueryPopup.kv')

class QueryPopup(Popup):
	
	def setAction(self,
		title, queryText,
		okCallback, bt_ok_text,
		cancelCallBack,	bt_cancel_text				
				):
		self.title = title
		self.ids.lquery.text = queryText
		self.ids.bt_ok.text = bt_ok_text
		
		self.okCB = okCallback
		self.cancelCB = cancelCallBack
		if cancelCallBack == None:
			self.ids.bt_cancel.disabled = True
		else:
			self.ids.bt_cancel.text = bt_cancel_text
		
	def run(self):
		self.open()
	
	def on_bt_ok(self):
		print( "on_bt_ok" )
		self.dismiss()
		if self.okCB != None:
			self.okCB()
		
	def on_bt_cancel(self):
		print( "on_bt_cancel" )
		self.dismiss()
		if self.cancelCB != None:
			self.cancelCB()
		