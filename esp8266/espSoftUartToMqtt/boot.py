
import time


import json



time.sleep(2)
print("3")
time.sleep(1)
print("2")
time.sleep(1)
print("1")
time.sleep(1)
print("gogogo")

print("loading libs...")
from MyWifi import MyWifi
from MySUart import MySUart
from MyMqttClient import MyMqttClient as mqcc
mqc = None
from MyJsonToMqtt import MyJsonToMqtt as mjtmc
print("DOne")

'''
def mqCB(a1=0,a2=0,a3=0,a4=0):
    global c
    print("a:{}\nb:{}\nc:{}\nd:{}\n-----------".format(a1,a2,a3,a4))
    if( a1 == b"esp01/led/in" ):
        if a2 == b"1":
            mqPub("esp01/led","0", True)
        elif a2 == b"0":
            mqPub("esp01/led","1",True)
    elif a1 == b'esp01/cmd' :
        doCommands(a2)


      
def uParse( buf ):
    if len( buf ) > 5:        
        global mqStack
        if buf[-1] == "\r" or buf[-1] == "\n":
            buf = buf[:-1]
        if buf[-1] == "\r" or buf[-1] == "\n":
            buf = buf[:-1]
        
        if isinstance(buf, (bytes)):
            print("EE - xxx",buf)
            return False
        for l in buf.split("\r\n"):
            uParseLine( l )
    
    return True
        
def uParseLine( line ):
    global doSUartToMqtt
    if len(line)>1:
        if line[0] == '{' and line[-1] == '}':
            try:
                j = json.loads(line.replace("'",'"'))
                #print("jOK")
                if doSUartToMqtt:
                    mqBroadJson(j)
                #print("json YES stackSize:",len(mqStack))
                
            except:
                print("json NO :(",line)
                try:
                    mqAts("esp01/uart/parseE","err41:{}".format(uart))
                except:
                    pass
        else:
            #print("uartNaN:",l)
            abbbe = 0


'''








  
            
   

def getMs():
    return time.ticks_ms()%15000
             

def ticchk(sMs, target,every):
    if sMs > target:
        return True
    elif sMs < target and ( target-every ) > sMs :
        return True
    
    return False
    
    
def d():
    return True

def mqHandler(a1=0,a2=0,a3=0,a4=0):
    if d():print("mqHandler a:{}\nb:{}\nc:{}\nd:{}".format(a1,a2,a3,a4))
    
    msg = a2.decode()
    if d():print("    msg:",msg)
    if a1 == b'esp01/cmd':
        global mqc
        if d():print("    got command:")
        if msg == "ping":
            mqc.pub("esp01/res","pong")
        elif msg == "looperPrint:Off":
            global looperPrint
            looperPrint = False
        elif msg == "looperPrint:On":
            global looperPrint
            looperPrint = True
        elif len(msg)>8 and msg[:8] == "looperE:":
            global sMloopE
            try:
                sMloopE = int(msg[8:])
                print("set looper to ",sMloopE)
            except:
                mqc.pub("esp01/res","EE - need to be ms in int()")
        elif len(msg)>4 and msg[:4] == "echo":
            mqc.pub("esp01/res",msg[5:])
    
    
print("------- init big objects")
print("MyWifi ...")
mWifi = MyWifi('DIRECT-v7-SecureTether-PPA-LX3','zLzoqbNU')
time.sleep(.5)

print("MySUart ...")
suart = MySUart()
time.sleep(.5)

print("MyMqttClient ...")
mqc = mqcc("esp01","192.168.49.220",12883, callback=mqHandler,
    subList = [
        "esp01/ap",
        "esp01/others"
        ])
time.sleep(.5)

print("MyJsonToMqtt ...")
mjtm = mjtmc( mqttPubCallback = mqc )
print("------- init big objects DONE")


sMs = 0
sMi = 0
sMloopE = 5000
sMloopNext = 0

sMsuartE = 1
sMsuartNext = 0

sMmqcE = 1500
sMmqcNext = 0

uc = 0

looperPrint = True

print("Main loop ...")
while True:
    sMs = getMs()
    sMi+=1
    
    
    if ticchk(sMs,sMmqcNext,sMmqcE):
        mqc.chk_msg()
        sMmqcNext = getMs()+sMmqcE
    
    if ticchk(sMs,sMloopNext,sMloopE):
        mWifi.chkStatus()
        if looperPrint:print("wifi is ok:[{}]    online:[{}]    ip:[{}]".format(
            mWifi.isOk,
            mWifi.isConnected,
            mWifi.myIp,
            ))
        #print("suart buf:[{}]".format(uc))
        
        lps = (sMi/float(float(sMloopE)/1000.0))
        if looperPrint: print("looper i/s:[",lps,"/1s.",
              "]    msTick:[",sMs, 
              "]    mem:[",gc.mem_alloc(),
              "]    su.buf:[",len(suart.buf),
              "]")
        mqc.pub( "esp01/looper/lps", lps )
        mqc.pub( "esp01/cpu/mem/", gc.mem_alloc() )
        mqc.pub( "esp01/wifi/ip", mWifi.myIp )
        mqc.pub( "esp01/suart/bufSize", len(suart.buf) )
        mqc.pub( "esp01/suart/nEr", suart.nEr )
        mqc.pub( "esp01/mqc/nConnects", mqc.nConnects )
        mqc.pub( "esp01/mqc/nPub", mqc.nPub )
        mqc.pub( "esp01/mjtm/nEr" ,mjtm.nParseEr)
        mqc.pub( "esp01/mjtm/nNaN" ,mjtm.nParseNaN)
        mqc.pub( "esp01/mjtm/nPub" ,mjtm.nPub)
        
        
        
        
        
        if mWifi.isOk:
            if mqc.isConnect == False:
                mqc.connect()
                
            if mqc.isConnect == True and mqc.isOk == False:
                mqc.ping()
        
        if looperPrint:print("mqc is ok:[{}] online:[{}]".format(
            mqc.isOk, mqc.isConnect
            ))
        else:
            print(".")
        
        
        sMi = 0       
        sMloopNext = getMs()+sMloopE
    
    
    if 1:#ticchk(sMs, sMsuartNext,sMsuartE):
        uc = suart.readToBuf(sMi)
        if uc > 0:
            mjtm.parse(suart.buf)
            suart.buf = []
        #sMsuartNext = getMs()+sMsuartE
    
print("it's It! DONE")
