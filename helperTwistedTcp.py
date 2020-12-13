
import json
from twisted.internet import protocol


class MyServer( protocol.Protocol ):
	
	def connectionMade(self):
		print("connection made !")
		self.factory.clients.append(self.transport)
		self.transport.write("hello you areconnected".encode('utf-8'))
		
	
	def dataReceived(self, data):
		print("dataReceived from transport",self.transport)
		res = self.factory.handle_message(data, self.transport)
		if res:
			print("write %s"%res)
			self.transport.write(res)
			
	def connectionLost(self, reason):
		print("connectionLost",reason)
		print("trying to remove client from list ...")
		for i,c in enumerate(self.factory.clients):
			if c == self.transport:
				self.factory.clients.pop(i)
				break
				
		
class Nmea:
	def __init__(self,factory):
		self.factory = factory
		
	def messageParse(self,msg,client):
		print("messageParse",msg)
		
		
		msg = "$YK{}".format(msg[3:])
		msgs = msg.split("\r\n")
		if len(msgs)>0:
			print("more then one message!",len(msgs))
			for m in msgs:
				self.factory.sendToAll(m, skipClient=[client])
		else:
			self.factory.sendToAll(msg)
		return False
			
class MyServerFactory( protocol.Factory ):
	protocol = MyServer
	
	clients = []
	
	def __init__(self, gui): 
		self.gui = gui
		self.nmea = Nmea(self)
		
	def handle_message(self, msg, client = None):
		msg = msg.decode('utf-8')
		print("recive msg [%s]"%msg)
		
		if msg[0] == '$' and msg[6] == ',':
			return self.nmea.messageParse(msg, client)
		if msg == "ping":
			msg = "Pong"
		if msg == "plop":
			msg = "Kivy Rocks!!!"
		return msg.encode('utf-8')
	
	def sendToAll(self, msg, skipClient=None):
		#print("send To All (%s) ->[%s]"%(len(self.clients),msg))
		if msg == "":
			print("skip it's empty")
			return True
		
		if skipClient != None:
			print("sendToAll with skipClient",skipClient)
		
		msg = ("%s\n"%msg).encode('utf-8')
		for t in self.clients:
			if skipClient == None:
				print("send t",t," msg",msg)
				t.write(msg)
			elif t in skipClient:
				print("skiping client ",t)
			else:
				print("send t",t," msg",msg)
				t.write(msg)
		#print("send to all DONE")
	
class MyClient( protocol.Protocol ):
	
	'''def as_complex(dct):
		if '__complex__' in dct:
			return complex(dct['real'], dct['imag'])
		return dct
	'''
	def dataReceived(self, data):
		msg = data.decode('utf-8')
		lines = []
		if msg.count("\n") == 0:
			lines = [msg]
		else:
			lines = msg.split("\n")
		msg = ""
		for msg in lines:
			#print("C: recive msg [%s]"%msg)
			if len(msg) > 3 and msg[0] == '{' and msg[-1] == "}":
				s = msg
				json_acceptable_string = s.replace("'", "\"").replace("(","[").replace(")","]")
				j = json.loads(json_acceptable_string)

				
				#print("C: json[%s]"%j)
				
				if j["type"] == "gps":
					self.factory.gui.sen.gpsD.update(j['data'])
				elif j["type"] == "gyro":
					self.factory.gui.sen.gyro.setVal( j['data'] )
				elif j["type"] == "accel":
					self.factory.gui.sen.accel.setVal( j['data'] )
				elif j["type"] == "gravity":
					self.factory.gui.sen.gravity.setVal( j['data'] )
				elif j["type"] == "comCal":
					self.factory.gui.sen.comCal.setVal( j['data'] )
				elif j["type"] == "spacorientation":
					self.factory.gui.sen.spacialOrientation.setVal( j['data'] )
				#elif j["type"] == 'gyroFlipt':
				#	self.factory.gui.sen.gyroFlipt.setVal( j['data'])
			
	
class MyClientFactory( protocol.ClientFactory ):
	protocol = MyClient
	
	def __init__(self, gui):
		self.gui = gui


import urllib.request
def DownloadFile(url,targetFile):
	c = urllib.request.urlopen(url)
	f = open(targetFile,"wb")
	f.write(c.read())
	f.close()
	

		
	