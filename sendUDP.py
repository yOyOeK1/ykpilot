import socket

UDP_IP = "0.0.0.0"
UDP_PORT = 2947
MESSAGE = "$AAHDG,10,0,W,0,E"
#$AAXDR,A,0.5,,PTCH,A,-10.0,,ROLL,

print( "UDP target IP:", UDP_IP )
print( "UDP target port:", UDP_PORT )
print( "message:", MESSAGE )

sock = socket.socket(socket.AF_INET, # Internet
             socket.SOCK_DGRAM) # UDP
sock.sendto(("%s\n"%MESSAGE), (UDP_IP, UDP_PORT))