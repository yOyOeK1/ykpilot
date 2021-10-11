from machine import UART
import time

class MyUart:
    
    uart = None
    nEr = 0
    nChkOk = 0
    nChkEr = 0
    buf = []
    rxActive = False
    
    def __init__(self, baudrate_=57600):
        print("MyUart.__init__")
        print("    do uart 0")
        self.uart = UART(0,baudrate_)
        print("    do init...")
        self.uart.init(baudrate_, bits=8, parity=None, stop=1)
        self.nEr = 0
        
        self.lGotNo = False
        self.lGotChkSum = False
        self.lChkSumOk = False
        
        self.nChkOk = 0
        self.nChkEr = 0
        self.buf = []
        self.rxActive = False
        self.difWritePipe = None
        print("MyUart.__init__ DONE")
    
    def writeOk(self):
        self.writeLine("Ok")
    def writeRe(self):
        self.writeLine("Re")
    def writePing(self):
        self.writeLine("$ping")
        
    def writeLine(self,msg):
        if self.rxActive == False:
            if self.difWritePipe == None:
                self.uart.write("{}*{}\n".format(
                    msg, self.getChkSum(msg)
                    ))
            else:
                self.difWritePipe(msg)
        else:
            print("EE - uart2 551")
    
        
    def getChkSum(self, msg):
        value = 0
        for c in msg:
            value ^= ord(c)
        return str(hex( value & 255 ))[2:]
    
    
    def chkSumChk(self, msg):
        di = msg.find(':')
        mi = msg.rfind('*')
        if di != -1 and mi != -1:
            self.lGotNo = False
            self.lGotChkSum = False
            
            self.lChkSumOk = True
            try:
                abcc = int(msg[:di])
                self.lGotNo = True                
            except:
                pass
            
            self.lGotChkSum = False
            if self.lGotNo:
                try:
                    chkSumStr = msg[mi+1:]
                    if len(chkSumStr)>0:
                        self.lGotChkSum = True
                    msgOnly = msg[di+1:mi]
                    chkSum =  self.getChkSum(msgOnly)
                    if chkSumStr == chkSum:
                        #print("chkTest",chkSumStr," <=> ",chkSum," OK")
                        self.lChkSumOk = True
                    else:
                        print("chkEr not same",msg)
                        return msg
                except:
                    pass
                
                if self.lChkSumOk:
                    self.nChkOk+=1
                    return msg[di+1:mi]
                elif self.lGotNo and self.lGotChkSum:
                    self.nChkEr+=1
                    
        
        return msg

    def doCChkSume(self,msg):    
        try:
            msg = msg.decode('ascii')
        except:
            print("EE decode 6455 ",msg)
            return msg
            
        #print("c msg",msg)
        return self.chkSumChk(msg)
    
    def testRead(self, cb = None):
        time.sleep(.5)
        print("testRead reaToBuff....")
        while True:
            self.readToBuf( cb )
            
    
    def readToBuf(self, callBackOnLine = None):
        while self.uart.any()>0:
            self.rxActive = True
            all = self.uart.read()
            
            if callBackOnLine == None:
                print("rtb:",all)
            else:
                lines = all.split(b'\r\n')
                #print("    lines c:",len(lines))
                
                if callBackOnLine != None:
                    for l in lines:
                        chk = self.doCChkSume( l ) 
                        callBackOnLine( chk )
                        
        self.rxActive = False
                  
