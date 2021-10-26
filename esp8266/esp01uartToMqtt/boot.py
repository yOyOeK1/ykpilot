from machine import Pin
import time


def mPrint(s):
    if(1):
        print(s)



time.sleep(3)
mPrint(2)
time.sleep(1)
mPrint(1)
time.sleep(1)
mPrint("go go go .....")



import webrepl
webrepl.start()

mPrint("import .....")
import uasyncio as uaio 

from MyChkSums import *
from MyMqttClient import MyMqttClient as mqcc
from MyJsonToMqtt import MyJsonToMqtt as mjtmc
from MyWifi import MyWifi
from MyUart import MyUart
mPrint("import DONE")


mqc = None


def d():
    return True

def simpleHandler(msg):
    return mqHandler(a1 = b'esp01/cmd', a2=msg)


def mqHandler(a1=0,a2=0,a3=0,a4=0):
    if d():print("mqHandler...")# a:{}\nb:{}\nc:{}\nd:{}".format(a1,a2,a3,a4))
    
    #print("ty",type(a2))
    if isinstance(a2,bytes):
        msg = a2.decode()
    else:
        msg = a2#.decode()
    
    #if d():print("    msg:[",msg,"]")
    
    '''
    if a1 == b'esp01/ap':
        #if d():print("    esp01 ap:[",msg,"]")
        global ap
        ap.setNewDirection( int(msg) )
    '''     
    
    if a1 == b'esp01/cmd':
        if d():print("    esp01 got command:[",msg,"]")
        if msg == "ping":
            global mqc
            mqc.pub("esp01/res","pong")
            return True
        
        elif msg == "looperPrint:Off":
            global looperPrint
            looperPrint = False
            return True
        
        elif msg == "looperPrint:On":
            global looperPrint
            looperPrint = True
            return True
        
        elif len(msg)>4 and msg[:4] == "echo":
            mqc.pub("esp01/res",msg[5:])
            return True
        
        elif len(msg)>5 and msg[:5] == "uart:":
            global suart
            suart.uart.write("{}\r\n".format(msg[5:]))
            print("uart.write({})".format(msg[5:]))
            return True
        
        elif len(msg)>8 and msg[:8] == "looperE:":
            global sMloopE,mqc
            try:
                sMloopE = int(msg[8:])
                print("set looper to ",sMloopE)
            except:
                mqc.pub("esp01/res","EE - need to be ms in int()")
            return True
        
        elif len(msg)>10 and msg[:10] == "suartBust:":
            global suart,mqc
            try:
                suart.bust = int(msg[10:])
                print("set suart.bust to ",suart.bust)
            except:
                mqc.pub("esp01/res","EE - need to be int()")
                
            return True
        
    return False




mPrint("init what need to be init ....")
apWifi = MyWifi(  essid_="MyPimPim", passwd_="ala ma kota", asAccessPoint=True  )
suart = MyUart()#mode='dummy')
mqc = mqcc("esp01ex","192.168.4.2",12883, callback=mqHandler)

def dummymqPut(t,m,r):
    global mqc
    mqc.pub(t,m,r)
    
mjtm = mjtmc( 
    mqttPubCallback = dummymqPut, 
    othersCommandParserHandler = simpleHandler
    )
mPrint("init done")

globalIter = 0

 


looperPrint = True
looperIter = 0
sMloopE = 5000
gIter = 0
uartDumpToMq = 0
async def looperAsync():
    global looperIter,mqc,apWifi,suart,mjtm,uartDumpToMq,sMloopE,gIter,uartInDecNEr,mqHandler
    
    await uaio.sleep_ms(100)
    mem = 0
    pTime = 100
    
    while True:
        print("/-- Looper")
        looperIter+=1

        mem = gc.mem_alloc()
        await uaio.sleep_ms(pTime)
        
        
        apWifi.chkStatus()
        await uaio.sleep_ms(pTime)
        if looperPrint:
            print("wifi is ok:[{}]    online:[{}]    ip:[{}]".format(
            apWifi.isOk,
            apWifi.isConnected,
            apWifi.myIp,
            ))
            await uaio.sleep_ms(pTime)
        
        if mqc.isOk:
            mqc.pub( "esp01/looper/iter", looperIter )
            mqc.pub( "esp01/cpu/mem/", mem )
            await uaio.sleep_ms(pTime)
            mqc.pub( "esp01/wifi/ip", apWifi.myIp )
            await uaio.sleep_ms(pTime)
            mqc.pub( "esp01/suart/linesIn",len(suart.linesIn))
            await uaio.sleep_ms(pTime)
            mqc.pub( "esp01/suart/nOk", suart.nOk )
            await uaio.sleep_ms(pTime)
            mqc.pub( "esp01/suart/nEr", suart.nEr )
            mqc.pub( "esp01/suart/nChkOk", suart.nChkOk )
            await uaio.sleep_ms(pTime)
            mqc.pub( "esp01/suart/uartToDecEr", uartInDecNEr )
            mqc.pub( "esp01/suart/nChkEr", suart.nChkEr )
            await uaio.sleep_ms(pTime)
            mqc.pub( "esp01/mqc/nConnects", mqc.nConnects )
            mqc.pub( "esp01/mqc/nPub", mqc.nPub )
            mqc.pub( "esp01/mjtm/nEr" ,mjtm.nParseEr)
            mqc.pub( "esp01/mjtm/nNaN" ,mjtm.nParseNaN)
            await uaio.sleep_ms(pTime)
            mqc.pub( "esp01/mjtm/nPub" ,mjtm.nPub)
            mqc.pub( "esp01/iter" ,gIter)
            await uaio.sleep_ms(pTime)
            
        gIter+= 1
        #suart.readToBuf()
        
        if looperPrint:
            print("mqc is ok:[{}] online:[{}]".format(
                mqc.isOk, mqc.isConnect
                ))
            
        else:
            print(".")
        
        
        print("\-- LOPE")
        await uaio.sleep_ms(sMloopE)
    


chkSumStat = False
chktMsg = ""
uartInDecNEr = 0
async def uartLinesInToMqttAsync():
    global suart,mqc,uartDumpToMq,chkSumStat,chktMsg,uartInDecNEr
    pTime = 2
    msg = None
    while True:
        
        while suart.linesIn :
            if len(suart.linesIn)>20:
                suart.linesIn.pop(0)
            
            await uaio.sleep_ms(pTime)
            msg = suart.linesIn[0]
            
            await uaio.sleep_ms(pTime)
            
            if msg != None:
                chkSumStat,chktMsg = chkSumChk(msg)
                await uaio.sleep_ms(pTime)
                
                if mqc.isOk:
                    await uaio.sleep_ms(pTime)
                    res = mjtm.parseLineAsync(
                        chktMsg
                        )
                    if res == 0:
                        uartInDecNEr+=1
                    uartDumpToMq+=1
                    await uaio.sleep_ms(pTime)
            suart.linesIn.pop(0)
            
        await uaio.sleep_ms(2)


print("Main loop ...")


tMqcChkMsg = None
async def main():
    global apWifi,tMqcChkMsg,suart,mqc
    
    tLooper = uaio.create_task( looperAsync() )
    #tMqcChkMsg = uaio.create_task( mqc.runChkLoopAsync() )
    tsUartRead = uaio.create_task( suart.readLineAsync() )
    tUartLinesInToMqtt = uaio.create_task( uartLinesInToMqttAsync() )
    #tTaskBalancer = uaio.create_task( TaskBalancer() )
    
    
    while True:
        
        if apWifi.isOk and tMqcChkMsg == None:
            tMqcChkMsg = uaio.create_task( mqc.runChkLoopAsync() )
        elif apWifi.isOk == False and tMqcChkMsg != None:
            tMqcChkMsg.cancel()
            await uaio.sleep_ms(100)
            tMqcChkMsg = None
            gc.collect()
            
            
        if apWifi.isOk:
            if mqc.isConnect == False:
                for ipBroker in range(2,6,1):
                    mqc.setWhatToDo("esp01ex","192.168.4.{}".format(ipBroker),12883, callback=mqHandler)
                    mqc.initClient()
                    mqc.connect()
                    await uaio.sleep_ms(50)
                    if mqc.isConnect:
                        break
                
            await uaio.sleep_ms(50)
            if mqc.isConnect == True:
                mqc.ping()
            await uaio.sleep_ms(50)
            
            
        while len(suart.linesIn)>30:
            suart.linesIn.pop(0)
            
        while len(suart.linesIn)>30:
            suart.linesIn.pop(0) 
            
        
        await uaio.sleep_ms(1_000)


uaio.run(main())






