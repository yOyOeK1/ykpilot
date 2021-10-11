
print("MyMqttClient loading ...")
from umqttSimple2 import *
import uasyncio as uaio
print("    DONE")

class MyMqttClient:
    
    client = None
    isOk = False
    isConnect = False
    deb = False
    nConnects = 0
    nPub = 0
    pubBuf = []
    
    def __init__(self, client_id_,ip_,port_,callback=None,
                 subList = []
                 ):
        print("MyMqttClient.__init__")
        
        self.client =  MQTTClient(client_id_, ip_, port_)
        if callback == None:
            self.client.set_callback( self.callbackDumm )
        else:
            self.client.set_callback( callback )
        
        self.subList = subList        
        self.nConnects = 0
        self.nPub = 0
        self.pubBuf = []
            
        print("MyMqttClient.__init__ DONE")
        
        
    def callbackDumm(self,a1=0,a2=0,a3=0,a4=0):
        print("callBacDum a:{}\nb:{}\nc:{}\nd:{}".format(a1,a2,a3,a4))
        
    def connect(self):
        print("mqc.connect ...")
        res = None
        try:
            print("    connect ...")
            res = self.client.connect()
            print("    sub")
            self.client.subscribe("esp01/cmd")
            print("    try to subscribe to othere topics:",len(self.subList))
            for t in self.subList:
                print("    subscribe to:",t)
                self.client.subscribe(t)
            print("    ")
        except:
            print("    crash 52")
        print("    res:",res)
        if res == 0:    
            self.isConnect = True
            self.nConnects+=1
        else:
            self.isConnect = False
        print("    end",self.isConnect)
        
        
    async def chk_msg(self):
        if self.deb:print("mqc.chk_msg")
        pTime = 12
        if self.isOk:
            res = -999
            try:
                res = self.client.check_msg()
            except:
                print(" crash 51")
                
            if self.deb:print("    res:",res)
            if res == -999:
                self.isConnect = False
                self.isOk = False
            
            lb = len(self.pubBuf)-1
            while lb>=0:
                b = self.pubBuf[lb]
                await uaio.sleep_ms(pTime)
                self.client.publish(
                    b[0],
                    "{}".format(b[1]),
                    b[2]
                    )
                await uaio.sleep_ms(pTime)
                self.nPub+=1
                self.pubBuf.pop(lb)
                lb-=1
    
    async def runChkLoopAsync(self):
        res = 0
        lb = 0
        b = 0
        while True:     
            await uaio.sleep_ms(2)       
            if self.isOk:
                res = -999
                try:
                    res = self.client.check_msg()
                except:
                    print(" crash 51")
                    
                if self.deb:print("    res:",res)
                if res == -999:
                    self.isConnect = False
                    self.isOk = False
                
                lb = len(self.pubBuf)-1
                while lb>=0:
                    b = self.pubBuf[0]
                    await uaio.sleep_ms(2)
                    self.client.publish(
                        b[0],
                        "{}".format(b[1]),
                        b[2]
                        )
                    await uaio.sleep_ms(2)
                    self.nPub+=1
                    self.pubBuf.pop(0)
                    lb-=1
                
                
            await uaio.sleep_ms(100)
    
            
    def pub(self, topic, msg, retain_ = False):
        self.pubBuf.append([topic,msg,retain_])
            
    def pubReal(self,topic,msg,retain_=False):
        return 0
        if self.deb:print("mqc.pub")
        if self.isOk:
            res = -111
            try:
                res = self.client.publish(topic,str(msg),retain=retain_)
                self.nPub+=1
            except:
                print("    crash 53")
            if self.deb:print("    res:",res)
            if res != None:
                self.isOk = False
            
    def ping(self):
        if self.deb:print("mqc.ping")
        if self.isConnect:
            res = -111
            try:
                res = self.client.ping()
            except:
                print(" crash 54")
                
            if self.deb:print("    res:",res)
            if res == None:
                self.isOk = True
            else:
                self.isOk = False
                self.isConnect = False
        else:    
            self.isOk = False
        
        
        