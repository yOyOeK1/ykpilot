from machine import SoftUART, Pin
import time
import uasyncio as uaio
'''

from machine import SoftUART, Pin
u = SoftUART(Pin(14),Pin(12),baudrate=19200)

def crc(s):
    crc = 0
    for c in stream:
        for i in range(0, 8):
            b = (crc & 1) ^ ((( int(c) & (1 << i))) >> i)
            crc = (crc ^ (b * 0x118)) >> 1
    print(hex(crc))
    return crc
'''
class MySUart:
    
    #uart = None
    mStart = None
    nEr = 0
    nOk = 0
    rxActive = False
    nChkOk = 0
    nChkEr = 0
    buf = []
    noAction = 0
    linesIn = []
    bust = 14
    
    def __init__(self, PinTx=14, PinRx=12, baudrate_=9600, timeout_=10):
        print("MySUart.init")
        self.uart = SoftUART(
            Pin(PinTx), Pin(PinRx), 
            baudrate=baudrate_, 
            timeout=timeout_) 
        
        self.mStart = bytearray()
        self.nEr = 0
        self.rxActive = False
        
        self.lGotNo = False
        self.lGotChkSum = False
        self.lChkSumOk = False
        
        self.nChkOk = 0
        self.nChkEr = 0
        self.buf = []
        
    
    def writeOk(self):
        self.writeLine("Ok")
    def writeRe(self):
        self.writeLine("Re")
    def writePing(self):
        self.writeLine("$ping")
        
    def writeLine(self,msg):
        self.uart.write("{}*{}\n".format(
            msg, self.getChkSum(msg)
            ))
    
        
    
    
    
    
    
    
    def testRead(self, cb = None):
        print("testRead reaToBuff....")
        while True:
            self.readToBuf(  )
      
    
    async def readLineAsync(self):
        ct = self.bust
        while True:
            #if self.readToBuf():
            #    await uaio.sleep_ms(1)
            ct = self.bust
            c = None
            while ct > 0:
                c = self.uart.readline()
                if c != None:
                    #try:
                        #if len(c)>128:
                    #print("long:",c)
                    self.linesIn.append(c[:-2])
                    self.nOk+=1
                    break
                        
                    #except:
                    #    print("E31x - ",c)
                    #    self.nEr+=1
                    #    break
                ct-=1
            
            
            await uaio.sleep_ms(50)
            
    
    def readToBuf(self):
        ct = 100
        c = None
        while ct > 0:
            c = self.uart.readline()
            if c != None:
                print("c",c)
                self.linesIn.append(c[:-2])
                self.nOk+=1
                break
            ct-=1
            
            
          
