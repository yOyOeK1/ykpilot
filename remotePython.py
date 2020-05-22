import socket
import code
import sys

class remotePython:
	def run(self):
		print("remote python is running !!")
		host = '0.0.0.0'
		port = 2002
		
		s = socket.socket()
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		s.bind((host,port))
		s.listen(1)
		c = s.accept()[0] # client socket
		
		def sread(s, len):
			return s.recv(len)
		
		def swrite(s, str):
			return s.sendall(str)
		
		def sreadline(s):
			return sread(s, 256) # lazy implementation for quick testing
		
		socket.socket.read = sread
		socket.socket.write = swrite
		socket.socket.readline = sreadline
		sys.stdin = c
		sys.stdout = c
		sys.stderr = c
		code.interact()
