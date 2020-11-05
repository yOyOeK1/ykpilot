		
from TimeHelper import *
from kivy_garden.graph import Graph, MeshLinePlot

		
class ScreenRace:
	
	sogMemory = 30 # seconds
	sogHistory = []
	
	def __init__(self, gui = None):
		if gui == None:
			print("ScreenRace __init__ with gui == None - need to set it up!")
		else:	
			self.gui = gui
		
		self.th = TimeHelper()
		
	def setGui(self, gui):
		self.gui = gui
	
	def setupGui(self):
		self.sogG = Graph(
			ymax=1.0, ymin=-1.0,
			)
		self.sogP = MeshLinePlot(color=[1,1,0,1])
		self.sogG.add_plot(self.sogP)
		self.gui.rl.ids.flRace.add_widget( self.sogG )
		
		
	def on_settings(self, o=None):
		print("on_settings")
		
	def update(self, fromWho, vals):
		#print("sogUpdate" ,fromWho, vals)
		self.sogHistory.append(vals['speed'])