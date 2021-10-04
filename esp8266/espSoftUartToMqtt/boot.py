
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
        if len(msg)>4 and msg[:4] == "echo":
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

print("Main loop ...")
while True:
    sMs = getMs()
    sMi+=1
    
    
    if ticchk(sMs,sMmqcNext,sMmqcE):
        mqc.chk_msg()
        sMmqcNext = getMs()+sMmqcE
    
    if ticchk(sMs,sMloopNext,sMloopE):
        mWifi.chkStatus()
        print("wifi is ok:[{}]    online:[{}]    ip:[{}]".format(
            mWifi.isOk,
            mWifi.isConnected,
            mWifi.myIp,
            ))
        #print("suart buf:[{}]".format(uc))
        
        
        
        print("looper i/s:[",(sMi/int(sMloopE/1000)),"/1s.",
              "]    msTick:[",sMs, 
              "]    mem:[",gc.mem_alloc(),
              "]    su.buf:[",len(suart.buf),
              "]")
        mqc.pub( "/esp01/looper/lps", (sMi/int(sMloopE/1000)) )
        mqc.pub( "/esp01/cpu/mem/", gc.mem_alloc() )
        mqc.pub( "/esp01/wifi/ip", mWifi.myIp )
        mqc.pub( "/esp01/suart/bufSize", len(suart.buf) )
        mqc.pub( "/esp01/suart/nEr", suart.nEr )
        mqc.pub( "/esp01/mqc/nConnects", mqc.nConnects )
        mqc.pub( "/esp01/mqc/nPub", mqc.nPub )
        mqc.pub( "/esp01/mjtm/nEr" ,mjtm.nParseEr)
        mqc.pub( "/esp01/mjtm/nNaN" ,mjtm.nParseNaN)
        mqc.pub( "/esp01/mjtm/nPub" ,mjtm.nPub)
        
        
        
        
        
        if mWifi.isOk:
            if mqc.isConnect == False:
                mqc.connect()
                
            if mqc.isConnect == True and mqc.isOk == False:
                mqc.ping()
        
        print("mqc is ok:[{}] online:[{}]".format(
            mqc.isOk, mqc.isConnect
            ))
        
        
        sMi = 0       
        sMloopNext = getMs()+sMloopE
    
    
    if 1:#ticchk(sMs, sMsuartNext,sMsuartE):
        uc = suart.readToBuf(sMi)
        if uc > 0:
            mjtm.parse(suart.buf)
            suart.buf = []
        #sMsuartNext = getMs()+sMsuartE
    
print("it's It! DONE")
    
'''    
if 0:
    if (mIter%10000) == 0:
        gc.collect()
        #try:
        #    s1.deinit()
        #except:
        #    print("E - no deint")
        #s1 = msUartInit()
        print("uIn:{} uEr:{} mqSS:{} mem:{} er:{}".format(
            uIn,uEr,len(mqStack), gc.mem_alloc(), mqEr
            ))
    
    if (mIter%100) == 0:
        if doSoftUart:
            uart = s1.readline()
            if uart != None:
                buf = None
                try:
                    buf = uart.decode('ascii')
                    uIn+=1
                except:
                    buf = uart
                    uEr+=1
                    print("ee",buf)
                
                if buf != None and uParse(buf) == True: 
                    #print("good")
                    abbbb = 0
                else:
                    mqAts("esp01/uart/parseE","err41:{}".format(uart))
                
                
    if doMqtt:
        if mqIsConnected:
            if (mIter%100) == 0:
                if mqChk( mqClient ) == False:
                    print("EE - mqChk error :(")
                
            
            if (mIter%100) == 0:
                mqStack,mqSsmax = mqChkStack( mqStack, mqSsmax )
    
    
    
    if (mIter%100000) == 0:
        mqAts("esp01/wifi/status","{}".format(nic.isconnected()))
        mqAts("esp01/wifi/ip","{}".format(getIp( nic )))
        mqAts("esp01/services/Mqtt","{}".format(("1" if doMqtt else "0")))
        mqAts("esp01/services/SoftUart","{}".format(("1" if doSoftUart else "0")))
        mqAts("esp01/services/SUartToMqtt","{}".format(("1" if doSUartToMqtt else "0")))
    
    if (mIter%10000) == 0:
        if mqPing( mqClient ) == False:
            if doMqtt:
                print("EE - ping error reconnect ?")
                mqClient = mqCon( mqCB )
            else:
                if mqIsConnected:
                    try:
                        print("try to stop mqtt client..")
                        c.disconnect()
                        mqIsConnected = False
                    except:
                        print("EE - can't stop client")
                else:
                    pass
                        
                    
                
        else:
            mqEr = 0
            #print("mqtt.pong")
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
    
    if doMqtt == False and doSoftUart == False and doSUartToMqtt == False:
        print("nothing to do !")
        r = input()
        print("got[{}]".format(r))
        doCommands(r)
        print(doMqtt,doSUartToMqtt,doSoftUart)
    
    
    mIter+=1
    #time.sleep(.5)
    
'''