from machine import SoftUART, Pin
import time
from simple2 import *
import network
import json
import select

poll = select.poll()

time.sleep(2)
print("3")
time.sleep(1)
print("2")
time.sleep(1)
print("1")
time.sleep(1)
print("gogogo")

print("SoftUart")
s1 = SoftUART(Pin(2), Pin(4), baudrate=57600, timeout=0)  # tx=2 rx=4



nic = None
c = None
mqpc = 0 # mq pub count
mqAddToStacDumpCount = 0
uartc = 0 # uart count lines

def wifiConectToAp( essid='', passwd='' ):
    global nic
    nic = network.WLAN( network.STA_IF)
    nic.active(True)
    nic.connect(essid,passwd) 
    
def getIp():
    return nic.ifconfig()

def mqConnect(client_id,ip, port, callback):
    global c
    print("mqConnect1")
    try:
        c = MQTTClient(client_id, ip, port)
        print("mqConnect2")
        res = c.connect()
        print("mqConnect3")
        c.set_callback(callback)
        c.subscribe("esp01/in")
        c.subscribe("esp01/led/in")
        print("mq connect results:",res)
    except:
        print("EE - mqConnect error :(")
    
    
def gotIp():
    return nic.isconnected()


mqStack = []
def mqConnect(client_id,ip, port, callback):
    global c
    print("mqConnect1")
    try:
        c = MQTTClient(client_id, ip, port)
        print("mqConnect2")
        res = c.connect()
        print("mqConnect3")
        c.set_callback(callback)
        c.subscribe("esp01/in")
        c.subscribe("esp01/led/in")
        print("mq connect results:",res)
    except:
        print("EE - mqConnect error :(")
 
    
def mqCon():
    mqConnect("esp01","192.168.49.220",12883,mqCB)

def mqCB(a1=0,a2=0,a3=0,a4=0):
    global c
    print("a:{}\nb:{}\nc:{}\nd:{}\n-----------".format(a1,a2,a3,a4))
    if( a1 == b"esp01/led/in" ):
        if a2 == b"1":
            mqPub("esp01/led","0", True)
        elif a2 == b"0":
            mqPub("esp01/led","1",True)

mqSsmax = 0
def mqChkStack():
    global mqStack,mqSsmax
    if len(mqStack) > 0:
        popC = 0
        while True:
            ss = len(mqStack)
            m = mqStack[0]
            
            #print("mqStack t:{} msg:{}".format(m[0],m[1]))
            if mqPub(m[0], m[1], False) == None:
                mqStack.pop(0)
                ss-=1
                popC+=1
            else:
                print("EE - mqchkstack:/ t:({}) m:({})".format(m[0],m[1]))
            
            if ss == 0 or popC > 25:
                #print("pusht",popC," stack size",len(mqStack))
                if mqSsmax < ss:
                    mqSsmax = ss 
                if ss > 15:
                    print("mqStack(",ss,")")
                break
            
            
def mqChk():
    global c,mqStack
    c.check_msg()    
    
    try:
        return True
    except:
        return False

def mqPub(topic,msg,r=False):
    global c,mqpc
    mqpc+=1
    try:
        topic_ = topic
        msg_ = "{}".format(msg)
    except:
        print("EE - in msg")
    
    try:
        respu = c.publish(topic_,msg_,retain=r)
        return respu
        
    except:
        return False
    
def mqPing():
    global c
    try:
        c.ping()
        return True
    except:
        return False
'''
 add to stack
 '''
def mqAts(topic, msg, r=False):
    global mqStack,mqAddToStacDumpCount
    if len(mqStack) < 50:
        mqStack.append([topic,msg,r])
    else:
        mqAddToStacDumpCount+=1
    
    

def mqBroadJson(j, pref = ""):
    #print("broadcast",j," --> ",type(j))
    
    if isinstance(j, dict):
        for k in j.keys():
            #print("pref:",pref,"key:",k," -> ",str(j[k])[:10])
            mqBroadJson(j[k], "{}/{}".format(pref,k))
            
    else:
        #print("is it a leaf ? :))")
        #print("mq:",pref," (",j,")")
        mqAts("uart{}".format(pref), j, False)
        
def uParse( buf ):
    global mqStack
    
    if buf[-1] == "\r" or buf[-1] == "\n":
        buf = buf[:-1]
    if buf[-1] == "\r" or buf[-1] == "\n":
        buf = buf[:-1]
    
    #print("uParse: len({}) [0]){}) newList{} [-2]({}) [-1]({})".format(
    #    len(buf),buf[0],buf.count("\n"),buf[-2],buf[-1]        
    #    ))
    
    for l in buf.split("\r\n"):
        if len(l)>1:
            if l[0] == '{' and l[-1] == '}':
                try:
                    j = json.loads(l.replace("'",'"'))
                    #print("jOK")
                    mqBroadJson(j)
                    #print("json YES stackSize:",len(mqStack))
                    
                except:
                    print("json NO :(",l)
            else:
                #print("uartNaN:",l)
                abbbe = 0

wifiConectToAp('DIRECT-v7-SecureTether-PPA-LX3','zLzoqbNU')

while True:
    if nic.isconnected():
        break
    else:
        print("connecting ....")
    time.sleep(.5)

print( "my ifconfig ",getIp() )

time.sleep(1)
mqConnect("esp01","192.168.49.220",12883,mqCB)


uart = None
mIter = 0
while True:
    if (mIter%100) == 0:
        uart = s1.readline()
        if uart != None:
            try:
                buf = uart.decode('UTF-8')
                uParse(buf)
            except:
                print("EE - ua")
                try:
                    mqAts("esp01/uart/parseE","err41:{}".format(uart))
                except:
                    pass
   
    if (mIter%100) == 0:
        if mqChk() == False:
            print("EE - mqChk error :(")
        
    
    if (mIter%10) == 0:
        mqChkStack()
    
    
    
    if (mIter%50000) == 0:
        print( "wifi ok:",nic.isconnected())
        print( "ip: ",getIp() )
    
    if (mIter%10000) == 0:
        if mqPing() == False:
            print("EE - ping error reconnect ?")
            mqConnect("esp01","192.168.49.220",12883,mqCB)
        else:
            print("mqtt.pong")
            if mqPub("esp01/load/mqStack",len(mqStack)) == False:
                print("EE - pub iter ")
            if mqPub("esp01/stats/uartLines",uartc) == False:
                print("EE - pub iter ")
            if mqPub("esp01/stats/mqStackSizeMax",mqSsmax) == False:
                print("EE - pub iter ")
            if mqPub("esp01/stats/dumptPubs",mqAddToStacDumpCount) == False:
                print("EE - pub iter ")
            
            if mqPub("esp01/stats/mqpub",mqpc) == False:
                print("EE - pub iter ")
            if mqPub("esp01/iter",mIter) == False:
                print("EE - pub iter ")
    
    
    mIter+=1
    #time.sleep(.5)
    
