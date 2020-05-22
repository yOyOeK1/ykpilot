
import socket

class helperTCP:
	
	def __init__(self,ip):
		host = ip
		port = 11223
		self.deg = 1
		print (host)
		print (port)
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		print("tcp 1")
		self.s.bind((host, port))
		print("tcp bing")
		self.s.listen(1)
		print("tcp listen")
		self.c,a = self.s.accept()
		print("tcp accept")
		
	def sendToAll(self,msg):
		print("tcp send to all %s"%msg)
		r = "%s\n"%msg
		self.c.sendall(r.encode())
		