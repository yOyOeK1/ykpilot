import network
from machine import Pin, SOFTUART
import time
import socket
from machine import Timer


print('-')
print("flash time for arduino on uart line...")


ap_essid = "svOiysh_ykpilot"
ap_passwd = "srytyfrytybangbang"


ap = network.WLAN(network.AP_IF) # create access-point interface
ap.active(True)         # activate the interface
ap.config(essid=ap_essid,password=ap_passwd)




tcp_port = 19999
tcp_ip = "192.168.4.1"

time.sleep(5)
print("5..")
time.sleep(3)
print("2..")
time.sleep(2)
print("delay DONE!")

pinInverted = True
p0 = Pin(0,Pin.OUT)
#p0 = None
p1 = Pin(2,Pin.OUT)
#p1 = None
p2 = Pin(4,Pin.OUT)
#p2 = None
p3 = Pin(5,Pin.OUT)
#p3 = None

print("softuart...")
s = SOFTUART(tx=12,rx=14,baudrate=115200)   # default tx=14,rx=12,baudrate=115200
print("DONE")

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

pubBuf = []

auBuf = ""
auIter = 0
def auChk():
    #global s
    
    c = s.getcount()    
    if c == 0:
        return None 
    
    global auBuf
    global auIter 
    #print("auCh...")
    if auIter > 40000:
        print("nm>au")
        s.write('nodeMCU say hello :)\n')
        auIter = 0
    
    
    if c > 0:
        while True:
            res = s.get()
            if res == 0:
                break
            else:
                auBuf+= chr(res)
                if len(auBuf)>=64:
                    auBuf = ""
        if auBuf[-1] == "\n":
            auBuf = auBuf[:-1]
            #print("nm<au:",auBuf)
            global pubBuf
            pubBuf.append(("au>nm:%s"%auBuf))
            auBuf = ""
           
    auIter+=1   
    
    

t.init(period=1000, mode=Timer.PERIODIC, callback=lambda tt:auChk())

    
    
        
def mLoop():
    global mdeb
    global apDir
    global pubBuf
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
                print("got",data)
                d = str(data)[2:3]
                #print("d[{}]".format(d))
                if d == 'R':
                    apDir = "R"
                elif d == 'L':
                    apDir = "L"
                elif d == 'P':
                    apDir = "P"
                
                if len(pubBuf) > 0:   
                    while len(pubBuf):
                        conn.sendall(pubBuf[0])
                        pubBuf.pop()
                else:
                    conn.sendall('O')
            #blink()
      
    mdeb = 4

if __name__ == "__main__":
    mdeb = -1
    mLoop()
    mdeb = -2

