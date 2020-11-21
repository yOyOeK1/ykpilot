
from kivy.uix.popup import Popup
from kivy.lang import Builder
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import cm

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
			self.queryWidget = queryText
			
			
			lqp = self.ids.lquery.parent
			lqp.remove_widget(self.ids.lquery)
			print("make in ScrollView -------------------------")
			sv = ScrollView(
				pos_hint = {'center_x': .5, 'center_y': 1},
				do_scroll_x = False,
				height=500
				
				)
			lqp.add_widget(sv,1)
			sv.add_widget(self.queryWidget)
			self.queryWidget.size_hint_y = None
			
			self.queryWidget.height = 5000
			
			#sv.height = 3000
			#sv.height = sv.parent.height
			
			
		self.ids.bt_ok.text = bt_ok_text
		
		self.okCB = okCallback
		
		self.cancelCB = cancelCallback
		if cancelCallback == None:
			self.ids.bt_cancel.disabled = True
			self.ids.bt_cancel.text = ""
		else:
			self.ids.bt_cancel.text = bt_cancel_text
		
		
	def run(self,a='',b=''):
		try:
			hs = 0.0
			for c in self.queryWidget.children:
				hs+= c.height
			self.queryWidget.size = [self.queryWidget.size[0],hs+cm(1)]
			
			print("it will have ",hs," height")
			print("parnte is size ",self.queryWidget.parent.size)
			print("parnte2 is size ",self.queryWidget.parent.parent.size)
			print("parnte3 is size ",self.queryWidget.parent.parent.parnet.size)
		except:
			print("queryPopup - no need to resize scroll view")
		
		print("preopen")
		self.open()
		print("postopen")
		
		
	def on_bt_ok(self):
		print( "on_bt_ok" )
		self.dismiss()
		if self.okCB != None:
			self.okCB()
		
	def on_bt_cancel(self):
		print( "on_bt_cancel" )
		self.dismiss()
		
		if str(self.cancelCB) == "":
			pass
		elif self.cancelCB != None:
			self.cancelCB()
		