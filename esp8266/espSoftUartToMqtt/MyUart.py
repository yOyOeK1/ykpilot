from machine import UART,Pin
import time
import uos
#import esp
import uasyncio as uaio
import gc

class MyUart:
    
    uart = None
    nEr = 0
    nOk = 0
    nChkOk = 0
    nChkEr = 0
    buf = []
    rxActive = False
    linesIn = []
    mode = ""
    
    def __init__(self, baudrate_=9600, mode = ''):
        print("MyUart.__init__")
        print("    do uart 0")
        
        if mode == 'dummy':
            self.mode = mode
        else:
            #esp.osdebug(None)
            uos.dupterm(None,1)
            gc.collect()
            led = Pin(2, Pin.OUT)
            
            self.uart = UART(0)
            self.uart.init(baudrate_, bits=8, parity=None, stop=1)
                
        print("    do init...")
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
            print("EE - uart 551")
    
    
    
    def testRead(self, cb = None):
        time.sleep(.5)
        print("testRead reaToBuff....")
        while True:
            self.readToBuf( cb )
            
    async def readLineAsync(self):
        line = ""
        
        if self.mode == 'dummy':
            while True:
                await uaio.sleep_ms(50)
        
        else:
        
            while True:
                await uaio.sleep_ms(2)
                while self.uart.any():
                    try:
                        line = str(self.uart.readline(), 'ascii')
                        if line!="":
                            self.linesIn.append(line)
                            self.nOk+=1
                    except:
                        self.nEr+=1
                
    #depricated
    def readToBuf(self, callBackOnLine = None):        
        pass
                  
