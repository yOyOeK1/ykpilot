import time




time.sleep(2)
print("3")
time.sleep(1)
print("2")
time.sleep(1)
print("1")
time.sleep(1)
print("gogogo")




print("loading libs...")
mqc = None
from MySUart import MySUart
if 0:
    if 1:
        print("    testing...")
        def cb( m ):
            print("cb(",len(m),"):",m)
        print("MySUart ...")
        suart = MySUart()
        suart.testRead()
       
from MyMqttClient import MyMqttClient as mqcc
from MyWifi import MyWifi
from MyJsonToMqtt import MyJsonToMqtt as mjtmc
import json
print("DOne")

# pLed = Pin(2,Pin.OUT); pin 2
        
        
pNo = 0
def p(msg):
    global mqc,pNo
    mqc.pub("esp01/pOut","{}:{}".format(pNo,msg))
    pNo+=1
    #print("P()",msg)

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
#mWifi = MyWifi('AlcatelPOP3','srytyfrytybangbang')
time.sleep(.5)

print("MySUart ...")
#suart = MySUart2()
suart = MySUart()
time.sleep(.5)

print("MyMqttClient ...")
mqc = mqcc("esp01","192.168.49.220",12883, callback=mqHandler,
#mqc = mqcc("esp01","192.168.43.99",12883, callback=mqHandler,
    subList = [
        "esp01/ap",
        "esp01/others"
        ])
time.sleep(.5)

print("MyJsonToMqtt ...")
mjtm = mjtmc( mqttPubCallback = mqc )
print("------- init big objects DONE")

def dbmq(msg):
    debugPrintOnUartToMqttPubTopic(msg)
    
def debugPrintOnUartToMqttPubTopic(msg):
    mqc.pub("esp01/debug","{}".format(msg))
    
suart.difWritePipe = debugPrintOnUartToMqttPubTopic

uartMsgAvg = 0.00
mjtmAvg = 0.00
rppAvg = 0.00


sMs = 0
sMi = 1
sMloopE = 5000
sMloopNext = 0

sMsuartE = 100
sMsuartNext = 0

sMmqcE = 500
sMmqcNext = 0
uartDumpToMq = 0
uc = 0

looperPrint = True
gIter = 0
lowestNext = -1

time.sleep(.1)
print("import uasyncio ...")
import uasyncio
async def suardLooper(a=0,b=0):
    while True:
        suart.readToBuf()

print("starting uart  ...")

print("Main loop ...")

#while True:
#    r = suart.readToBuf(sMi)
    

async main():
while True:    
    sMs = getMs()
    sMi+=1
    lowestNext = sMs
    
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
        #gc.collect()
        mem = gc.mem_alloc()
        #suart.readToBuf()
        lps = (sMi/float(float(sMloopE)/1000.0))
        if looperPrint: print("looper i/s:[",lps,"/1s.",
              "]    msTick:[",sMs, 
              "]    mem:[",mem,
              "]")
        #p("looper i/s:[{}/1s.]    msTick:[{}]    mem:[{}]".format(
        #        lps, sMs,gc.mem_alloc())
        #      )
        if uartDumpToMq:
            print("    uartToMq ",uartDumpToMq)
            uartDumpToMq = 0
        if mqc.isOk:
            #suart.readToBuf()
            mqc.pub( "esp01/looper/lps", lps )
            mqc.pub( "esp01/cpu/mem/", mem )
            mqc.pub( "esp01/wifi/ip", mWifi.myIp )
            mqc.pub( "esp01/suart/nOk", suart.nOk )
            mqc.pub( "esp01/suart/nEr", suart.nEr )
            mqc.pub( "esp01/suart/nChkOk", suart.nChkOk )
            mqc.pub( "esp01/suart/nChkEr", suart.nChkEr )
            #suart.readToBuf()
            mqc.pub( "esp01/mqc/nConnects", mqc.nConnects )
            mqc.pub( "esp01/mqc/nPub", mqc.nPub )
            mqc.pub( "esp01/mjtm/nEr" ,mjtm.nParseEr)
            mqc.pub( "esp01/mjtm/nNaN" ,mjtm.nParseNaN)
            mqc.pub( "esp01/mjtm/nPub" ,mjtm.nPub)
            mqc.pub( "esp01/iter" ,gIter)
            mqc.pub( "esp01/uartRead/msAvg", uartMsgAvg )
            mqc.pub( "esp01/mjtm/msAvg", mjtmAvg )
            mqc.pub( "esp01/rpp/msAvg", rppAvg )
            
        gIter+= 1
        #suart.readToBuf()
        
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

    
    
    if ticchk(sMs, sMsuartNext,sMsuartE):
        #suart.writePing()
        
        
        #suart.uart.write("$led:1\r\n");
        while suart.linesIn :
            chktMsg = suart.chkSumChk(suart.linesIn[0])
            #suart.readToBuf()
            if mqc.isOk:
                mjtm.parseLine(
                    chktMsg
                    )
                #suart.readToBuf()
            suart.linesIn.pop(0)
            uartDumpToMq+=1
        sMsuartNext = getMs()+sMsuartE

    
    
    if 0: 
        if 0:       
            suart.readToBuf()
        elif 0:
            mjtm.parseLine( suart.readToBuf(sMi) )
        else:  
            tS = getMs()          
            ures = None
            ures = suart.readToBuf(sMi)
            tUg = getMs()
            if ures != None:
                #mjtm.parseLine( ures )
                tMq = getMs()
                #p(">uart({}):{}".format(len(ures),ures))
                #p(">uart({}) out in ({})ms uart time ({})ms pub time ({})ms".format(len(ures),
                #   (tMq-tS), (tUg-tS), (tMq-tUg) ))
                uartMsgAvg = ((uartMsgAvg*10.00)+ (tUg-tS) )/11.0
                mjtmAvg = ((mjtmAvg*10.00)+ (tMq-tUg) )/11.0
                rppAvg = ((rppAvg*10.00)+ (tMq-tS) )/11.0
                #mqc.pub( "esp01/uart/readTimes/msAvr", uartMsgAvg )
                #mqc.pub( "esp01/mjtm/msAvr", mjtmAvg )
                #mqc.pub( "esp01/rpp/msAvr", rppAvg )
                
                
print("it's It! DONE")
