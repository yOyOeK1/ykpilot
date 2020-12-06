import network
from machine import Pin, I2C
import time
import socket
from machine import Timer


ap_essid = "svOiysh_ykpilot"
ap_passwd = "srytyfrytybangbang"


ap = network.WLAN(network.AP_IF) # create access-point interface
ap.active(True)         # activate the interface
ap.config(essid=ap_essid)



tcp_port = 19999
tcp_ip = "192.168.4.1"

pinInverted = True
#p0 = Pin(0,Pin.OUT)
p0 = None
#p1 = Pin(2,Pin.OUT)
p1 = None
#p2 = Pin(4,Pin.OUT)
p2 = None
#p3 = Pin(5,Pin.OUT)
p3 = None

"""
def setPin( p, status):
    if pinInverted:
        if status:
            p.off()
        else:
            p.on()
    else:
        if status:
            p.on()
        else:
            p.off()


def blink():
    setPin(p0, True)
    time.sleep(1)
    setPin(p0, False)
    
def setupBoard():    
    setPin(p0,False)
    setPin(p1,False)
    setPin(p2,False)
    setPin(p3,False)

mdeb = 0

apDir = ""
apPP = p0 
apPL = p1
apPR = p2

def apR():
    setPin(apPP, True)
    setPin(apPL, False)
    setPin(apPR, True)
    
def apL():
    setPin(apPP, True)
    setPin(apPL, True)
    setPin(apPR, False)
    
def apP():
    setPin(apPP, True)
    setPin(apPL, False)
    setPin(apPR, False)

def apOff():
    setPin(apPP, False)
    setPin(apPL, False)
    setPin(apPR, False)

def apChk( ):
    global apDir
    
    if apDir == 'R':
        apR()
    elif apDir == 'L':
        apL()
    elif apDir == 'P':
        apP()
    else:
        apOff()
        
    apDir = ""
    

t = Timer(-1)
t.init(period=200, mode=Timer.PERIODIC, callback=lambda tt:apChk())
"""
    
    
    
def i2cIter():
    
    i2c = I2C(scl=Pin(0), sda=Pin(2), freq=50000)
    print("i2c...")

    ii = 0
    while True:
        ii+=1
        print("iter")
    
        i2c.readfrom(0x08, 4)
        i2c.writeto(0x08, ii) # write '12' to slave device with address 0x3a
    
        #buf = bytearray(10)     # create a buffer with 10 bytes
        #i2c.writeto(0x3a, buf)  #
        time.sleep(1)


""" 
    
def mLoop():
    global mdeb
    global apDir
    mdeb = 1 
    setupBoard()
    print("board setup")
    time.sleep(5)
    print("going into socket loop....")
    mdeb = 2
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mdeb = 2.1
    
    while True:
        mdeb = 3
        print("iter")
        mdeb = 3.1
        s.bind((tcp_ip, tcp_port))
        mdeb = 3.2
        s.listen(2)
        mdeb = 3.3
        while True:
            conn, addr = s.accept()
            mdeb = 3.4
            mdeb = 3.5
            print('Connected by', addr)
            while True:
                data = conn.recv(1)
                if not data:
                    break
                #print("got",data)
                d = str(data)[2:3]
                #print("d[{}]".format(d))
                if d == 'R':
                    apDir = "R"
                elif d == 'L':
                    apDir = "L"
                elif d == 'P':
                    apDir = "P"
                conn.sendall('O')
            #blink()
      
    mdeb = 4
"""
if __name__ == "__main__":
    mdeb = -1
    #mLoop()
    i2cIter()
    mdeb = -2

