import json
from FileActions import *
from zipfile import ZipFile as zf

def DataSR_save(data,file, zip=False):
	
	if zip:
		try:
			z = zf(file,mode="w",compression=0)
			z.writestr('myData',str(data))
			z.close()
			return 1
		except:
			return 0
	else:	
		try:
			fa = FileActions()
			fa.writeFile(file,str(data))
			return 1
		except:
			return 0
	
def DataSR_restore(file,zip=False):
	if zip:
		try:
			z = zf(file,mode="r")
			s = str(z.read("myData"))[2:-1]
			#print("data from file[",s,"]")
			forJson = str(str(s).replace("'",'"') )
			j = json.loads(forJson)
			#print("---------j----------\n",j)
			return j 
		except:
			print("yyy json error ?")
			return None
		
	else:
		try:
			fa = FileActions()
			fc = fa.loadFile(file)
			if fc != None:
				forJson = str("\n".join(fc)).replace("'",'"')
				#print("sssssssssssssssss")
				#print(forJson)
				#print("-----------")
				j = json.loads(forJson)
				return j
			else:
				print("no file")
				return None
		except:
			print("EE - no json on restore !")
			j = []
			exec("j = list({})".format(forJson))
			print("type",type(forJson))
			print("type",type(list(forJson)))
			print( list(forJson))
			print(forJson[270:])
			j = json.loads(str(forJson))
			
			print("j",j)
			
			None
		