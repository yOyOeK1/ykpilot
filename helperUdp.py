import socket



class helperUdp:
	UDP_IP = "192.168.43.255"
	UDP_PORT = 11223
	MESSAGE = "$AAHDG,10,0,W,0,E"
	#$AAXDR,A,0.5,,PTCH,A,-10.0,,ROLL,
	
	def __init__(self,ip=None, port=None):
		if ip != None:
			self.UDP_IP = ip
		if port != None:
			self.UDP_PORT = port


	def setAsSender(self):
		print( "UDP target IP:", self.UDP_IP )
		print( "UDP target port:", self.UDP_PORT )
		self.sock = socket.socket(
			socket.AF_INET, # Internet
			socket.SOCK_DGRAM,
			socket.IPPROTO_UDP
			) # UDP
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT,1)
		self.sock.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST, 1)
		self.sock.settimeout(0.01)
		
	def send(self,msg):
		msg = ("%s\n"%msg).encode()
		self.sock.sendto(msg, (self.UDP_IP, self.UDP_PORT))
		
