
import json
from twisted.internet import protocol


class MyServer( protocol.Protocol ):
	
	def connectionMade(self):
		print("connection made !")
		self.factory.clients.append(self.transport)
		self.transport.write("hello you areconnected".encode('utf-8'))
		
	
	def dataReceived(self, data):
		print("dataReceived")
		res = self.factory.handle_message(data)
		if res:
			print("write %s"%res)
			self.transport.write(res)
			
class MyServerFactory( protocol.Factory ):
	protocol = MyServer
	
	clients = []
	
	def __init__(self, app): 
		self.app = app
		
	def handle_message(self, msg):
		msg = msg.decode('utf-8')
		print("recive msg [%s]"%msg)
		
		if msg == "ping":
			msg = "Pong"
		if msg == "plop":
			msg = "Kivy Rocks!!!"
		return msg.encode('utf-8')
	
	def sendToAll(self, msg):
		#print("send To All (%s) ->[%s]"%(len(self.clients),msg))
		msg = ("%s\n"%msg).encode('utf-8')
		for t in self.clients:
			t.write(msg)
		#print("send to all DONE")
	
class MyClient( protocol.Protocol ):
	
	def as_complex(dct):
		if '__complex__' in dct:
			return complex(dct['real'], dct['imag'])
		return dct
	
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
					self.factory.app.sen.gpsD.update(j['data'])
				elif j["type"] == "gyro":
					self.factory.app.sen.gyro.setVal( j['data'] )
				elif j["type"] == "accel":
					self.factory.app.sen.accel.setVal( j['data'] )
				elif j["type"] == "comCal":
					self.factory.app.sen.comCal.setVal( j['data'] )
				elif j["type"] == "spacorientation":
					self.factory.app.sen.spacialOrientation.setVal( j['data'] )
				elif j["type"] == 'gyroFlipt':
					self.factory.app.sen.gyroFlipt.setVal( j['data'])
			
	
class MyClientFactory( protocol.ClientFactory ):
	protocol = MyClient
	
	def __init__(self, app):
		self.app = app


import urllib.request
def DownloadFile(url,targetFile):
	c = urllib.request.urlopen(url)
	f = open(targetFile,"wb")
	f.write(c.read())
	f.close()
	

		
	