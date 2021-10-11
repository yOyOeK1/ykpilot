from machine import Pin, SOFTUART
import time

class MySUart2:
    
    uart = None
    nEr = 0
    nChkOk = 0
    nChkEr = 0
    buf = []
    rxActive = False
    
    def __init__(self, PinTx=12, PinRx=14, baudrate_=57600):
        
        self.uart = SOFTUART(
            tx=PinTx,rx=PinRx, 
            baudrate=baudrate_) 
        
        self.nEr = 0
        
        self.lGotNo = False
        self.lGotChkSum = False
        self.lChkSumOk = False
        
        self.nChkOk = 0
        self.nChkEr = 0
        self.buf = []
        self.rxActive = False
    
    def writeOk(self):
        self.writeLine("Ok")
    def writeRe(self):
        self.writeLine("Re")
    def writePing(self):
        self.writeLine("$ping")
        
    def writeLine(self,msg):
        if self.rxActive == False:
            self.uart.write("{}*{}\n".format(
                msg, self.getChkSum(msg)
                ))
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
            
    
    auBuf = ""
    chNo = 0
    cFu = ""
    countChOnUart = 0
    def readToBuf(self, callBackOnLine = None):
        self.countChOnUart = self.uart.getcount()
        if self.countChOnUart == 0:
            return None
        else:
            #self.auBuf = ""
            #self.chNo = 0
            to = 100
            while to > 0:
                self.cFu = self.uart.get()
                if self.cFu == 0:
                    break
                else:
                    self.auBuf+= chr(self.cFu)
                    self.chNo+=1
                    to = 1000
                    if self.chNo>=512:
                        print("tl")
                        break
                
                if self.auBuf[-1] in ["\n", "\r"]:
                    if self.chNo == 1:
                        self.auBuf = []
                    elif self.chNo > 1:
                        self.auBuf = self.auBuf[:-1]
                        if len(self.auBuf) > 0 and self.auBuf[-1] in ["\n", "\r"]:
                            self.auBuf = self.auBuf[:-1]
                        
                        if len(self.auBuf) > 0:
                            print("go:{}".format(self.auBuf))
                    
                    break
                
                to-=1
            
            self.auBuf = ""
            self.chNo = 0
            #print("to")    
             
            '''       
            #print("[",self.auBuf,"]")
            self.auBuf = ""
            #if auBuf[-1] == "\n":
            #    auBuf = auBuf[:-1]
            #    #print("nm<au:",auBuf)
            #    print(("au>nm:%s"%auBuf))
            #    auBuf = ""
        
        
        
        
        while c :
            self.rxActive = True
            if len(c)>1:
                try:
                    callBackOnLine.parseLine(
                        self.chkSumChk( 
                            c[:-2].decode('ascii') 
                            )
                        )
                except:
                    print("EE 423432",c)
                    
            c = self.uart.readline()
                        
        self.rxActive = False
        '''       
