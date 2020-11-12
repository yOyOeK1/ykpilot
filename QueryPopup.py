
from kivy.uix.popup import Popup
from kivy.lang import Builder

Builder.load_file('layoutQueryPopup.kv')

class QueryPopup(Popup):
	
	def setAction(self,
				title, queryText,
				okCallback, bt_ok_text,
				cancelCallback,	bt_cancel_text				
				):
		self.title = title
		
		print("[%s]"%str(type(queryText)))
		if str(type(queryText)) == "<class 'str'>":
			print("query witch str content")
			self.ids.lquery.text = queryText
		else:
			print("query witch widget content")
			lqp = self.ids.lquery.parent
			lqp.clear_widgets()
			lqp.add_widget( queryText )
			
			
		self.ids.bt_ok.text = bt_ok_text
		
		self.okCB = okCallback
		
		self.cancelCB = cancelCallback
		if cancelCallback == None:
			self.ids.bt_cancel.disabled = True
			self.ids.bt_cancel.text = ""
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
		