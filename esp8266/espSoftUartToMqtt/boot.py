import time




time.sleep(2)
print("3")
time.sleep(1)
print("2")
time.sleep(1)
print("1")
time.sleep(1)
print("gogogo")


from machine import Pin
'''
p = Pin(14, Pin.IN)
pUp = 0
pDown = 0
while True:
    if p.value():
        if pDown > 0:
            print("D:",pDown)
            pDown = 0
        pUp+=1
    else:
        if pUp > 0:
            print("U:",pUp)
            pUp = 0
        pDown+=1
'''     
    


print("loading libs...")
import uasyncio as uaio

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

from MyChkSums import *       
from MyMqttClient import MyMqttClient as mqcc
from MyWifi import MyWifi
from MyJsonToMqtt import MyJsonToMqtt as mjtmc
from MyAp import MyAp
import json
print("DOne")

pLed = Pin(2,Pin.OUT)
def ledOn():
    global pLed
    pLed.on()
def ledOff():
    global pLed
    pLed.off()
    
        
        
pNo = 0
def p(msg):
    global mqc,pNo
    mqc.pub("esp01/pOut","{}:{}".format(pNo,msg))
    pNo+=1
    #print("P()",msg)







    
def d():
    return False

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
    
    if a1 == b'esp01/ap':
        #if d():print("    esp01 ap:[",msg,"]")
        global ap
        ap.setNewDirection( int(msg) )
            
    
    if a1 == b'esp01/cmd':
        if d():print("    esp01 got command:[",msg,"]")
        if msg == "ping":
            global mqc
            mqc.pub("esp01/res","pong")
            return True
        
        elif msg == "led:Off":
            ledOn()
            return True
        
        elif msg == "led:On":
            ledOff()
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
mjtm = mjtmc( 
    mqttPubCallback = mqc, 
    othersCommandParserHandler = simpleHandler
    )
time.sleep(.5)

print("MyAp - autopilot module .....")
ap = MyAp( )
time.sleep(.5)

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

sMsuartE = 100

sMmqcE = 500

uartDumpToMq = 0
uc = 0

looperPrint = False
gIter = 0
lowestNext = -1

time.sleep(.1)




looperIter = 0
async def looperAsync():
    global looperIter,mqc,mWifi,suart,mjtm,uartDumpToMq,sMloopE,gIter,uartInDecNEr
    
    await uaio.sleep_ms(100)
    mem = 0
    pTime = 100
    
    while True:
        print("/-- Looper")
        looperIter+=1

        mem = gc.mem_alloc()
        await uaio.sleep_ms(pTime)
        
        if looperPrint: 
            print("looper i:[",looperIter,
              "]    msTick:[",sMs, 
              "]    mem:[",mem,
              "]")
            await uaio.sleep_ms(pTime)
        
        mWifi.chkStatus()
        await uaio.sleep_ms(pTime)
        if looperPrint:
            print("wifi is ok:[{}]    online:[{}]    ip:[{}]".format(
            mWifi.isOk,
            mWifi.isConnected,
            mWifi.myIp,
            ))
            await uaio.sleep_ms(pTime)
        
        if uartDumpToMq:
            #print("uartToMq c:[",uartDumpToMq,"]")
            mqc.pub( "esp01/uartToMqtt/n", uartDumpToMq )
            await uaio.sleep_ms(pTime)
         
        if mqc.isOk:
            mqc.pub( "esp01/looper/iter", looperIter )
            mqc.pub( "esp01/cpu/mem/", mem )
            await uaio.sleep_ms(pTime)
            mqc.pub( "esp01/wifi/ip", mWifi.myIp )
            await uaio.sleep_ms(pTime)
            mqc.pub( "esp01/suart/linesIn",len(suart.linesIn))
            await uaio.sleep_ms(pTime)
            mqc.pub( "esp01/suart/nOk", suart.nOk )
            await uaio.sleep_ms(pTime)
            mqc.pub( "esp01/suart/nEr", suart.nEr )
            mqc.pub( "esp01/suart/nChkOk", suart.nChkOk )
            await uaio.sleep_ms(pTime)
            mqc.pub( "esp01/suart/uartToDecEr", uartInDecNEr )
            mqc.pub( "esp01/suart/bust", suart.bust )
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
            mqc.pub( "esp01/uartRead/msAvg", uartMsgAvg )
            mqc.pub( "esp01/mjtm/msAvg", mjtmAvg )
            mqc.pub( "esp01/rpp/msAvg", rppAvg )
            await uaio.sleep_ms(pTime)
            
        gIter+= 1
        #suart.readToBuf()
        
        if mWifi.isOk:
            if mqc.isConnect == False:
                mqc.connect()
            await uaio.sleep_ms(pTime)
            if mqc.isConnect == True and mqc.isOk == False:
                mqc.ping()
            await uaio.sleep_ms(pTime)
        
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
            msg = None
            try:
                msg = suart.linesIn[0].decode('ascii')
            except:
                await uaio.sleep_ms(pTime)
                uartInDecNEr+=1
                print("Edec55")
                
            #mqc.pub("esp01/ulutma", msg, False)
                
                
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

async def TaskBalancer():
    global uartInDecNEr,suart
    print("TaskBalancer")
    while True:
        
        if uartInDecNEr > 3 and suart.bust < 2000 :
            suart.bust = int(float(suart.bust)*1.1)
            await uaio.sleep_ms(1)
            print("TasBal uDecEr",uartInDecNEr," + suart.bust:",suart.bust)
            await uaio.sleep_ms(1)
            
        elif uartInDecNEr == 0 and suart.bust > 12:
            suart.bust = int(float(suart.bust)*0.95)
            await uaio.sleep_ms(1)
            print("TasBal uDecEr",uartInDecNEr," - suart.bust:",suart.bust)
            await uaio.sleep_ms(1)
            
        uartInDecNEr = 0
                            
        
        await uaio.sleep_ms(20_002)

print("Main loop ...")

#while True:
#    r = suart.readToBuf(sMi)
    

async def main():
    tLooper = uaio.create_task( looperAsync() )
    tMqcChkMsg = uaio.create_task( mqc.runChkLoopAsync() )
    tSUartRead = uaio.create_task( suart.readLineAsync() )
    tUartLinesInToMqtt = uaio.create_task( uartLinesInToMqttAsync() )
    tAp = uaio.create_task( ap.runItAsync() )
    #tTaskBalancer = uaio.create_task( TaskBalancer() )
    
    
    while True:
        
        while len(suart.linesIn)>30:
            suart.linesIn.pop(0)
            
        while len(suart.linesIn)>30:
            suart.linesIn.pop(0) 
            
        
        await uaio.sleep_ms(5_000)


uaio.run(main())

'''
while True:    
    sMs = getMs()
    lowestNext = sMs
    
    
    
    
    if ticchk(sMs, sMsuartNext,sMsuartE):
        #suart.writePing()
        #suart.uart.write("$led:1\r\n");
        
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
                
'''
print("it's It! DONE")
