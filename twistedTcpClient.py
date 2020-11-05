

from __future__ import print_function

from twisted.internet import reactor, protocol
import time
import _thread
from TimeHelper import *
from kivy.clock import Clock

class ttc_Client(protocol.Protocol):
    
    th = TimeHelper()
    
    def updatePongTime(self):
        self.factory.lastPong = self.th.getTimestamp(microsec=True)
    
    def connectionMade(self):
        print("connected !")
        self.transport.write(b"hello from ykpilot! app")
        self.factory.client = self
        self.updatePongTime()
        
    def dataReceived(self, data):
        msg = "%s"%str(data)[2:-1]
        print("Server said: [{}] - > [{}]".format( str(data),msg ))
        
        self.updatePongTime()
        
        if msg == 'O':
            ms = self.th.getTimestamp(microsec=True)
            self.lastPong = ms
        
        elif msg == 'exit()':
            self.transport.loseConnection()
    
    def connectionLost(self, reason):
        print("connection lost")
        
    def sendMsg(self,msg):
        self.transport.write(msg.encode('utf-8'))
        

class ttc_Factory(protocol.ClientFactory):
    protocol = ttc_Client
    
    
    def watchDogIter(self,a):
        ms = self.th.getTimestamp(microsec=True)
        dif = (ms-self.lastPong)/1000000.0
        #print("last ping {:.3f}sec.".format( dif  ))
        if dif > 1.0 and self.client:
            self.client.transport.write(b"O")
        
        if dif > 3.0:
            #print("not connected ?")
            if self.client:
                self.lastPong = ms
                self.client.connectionLost("yyy time out")
            self.setConnectionStatus('off')
        else:
            self.setConnectionStatus('on')
        
    
    
    def setGui(self, gui):
        print("Factory setGui")
        self.th = TimeHelper()
        
        self.gui = gui
        self.client = None
        self.lastPong = 0
        
        self.watchDogTimeOut = Clock.schedule_interval(self.watchDogIter, 1.0)
        
        
        
    def setConnectionStatus(self, status):
        self.gui.wifiTcpStatus = self.gui.wifiTcpStatusOpts[status]
        
    def clientConnectionFailed(self, connector, reason):
        print("Connection failed - goodbye!")
        self.mreconnect()
        
    def clientConnectionLost(self, connector, reason):
        print("Connection lost - goodbye!")
        self.mreconnect()
     
    def mreconnect(self):
        if True:
            print("will reconnect ...")
            time.sleep(1)
            print("connecting ...")
            self.mconnect()
        else:
            reactor.stop()
    
    def mconnect(self):
        reactor.connectTCP("192.168.4.1", 19999, self)
       
    def getClient(self):
        return self.client

class ttc():
    def __init__(self, gui):
        self.workStatus = False
        self.gui = gui
        self.factory = ttc_Factory()
        self.factory.setGui( self.gui )
        
        
    def work(self):
        print("ttc.work!")
        self.workStatus = True
        self.connect()
        
    def send(self, msg):
        print("ttc.send [{}]".format(msg))
        c = self.factory.getClient()
        if c != None:
            c.sendMsg(msg)
        else:
            print("no client")
    
    def stop(self):
        print("ttc.stop !")
        self.workStatus = False

    def connect(self):
        print("ttc.connect!")
        reactor.connectTCP("192.168.4.1", 19999, self.factory )



    