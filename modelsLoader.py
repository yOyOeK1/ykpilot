import os
from objloader import ObjFile

class modelsLoader:
	
	name = ""
	
	
	def __init__(self,modelsGroupName):
		self.name = modelsGroupName
		self.files = './3dModels/'+self.name+"_3dex_files.list"
		self.objNames = './3dModels/'+self.name+"_3dex_objNames.list"
		
	def getObjects(self):
		tr = {}
		
		ff = open(self.files)
		fo = open(self.objNames)
		
		filesList = []
		objList = []
		
		while True:
			lf = str(ff.readline()[:-1])
			on = str(fo.readline()[:-1])
			if lf == "":
				break
			
			filesList.append('./3dModels/'+lf+'.obj')
			objList.append(on)
			
		
		scene = ObjFile( filesList )
		for i,o in enumerate(objList):
			#print(o)
			keys = list(scene.objects.keys())
			tr[ o ] = scene.objects[keys[i]]
				
		#print("loadet [%s] objects"%len(tr))
		#print(tr)
				
		return tr
			
			
		
		