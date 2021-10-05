from machine import SoftUART, Pin

class MySUart:
    
    uart = None
    buf = []
    mStart = None
    nEr = 0
    rxActive = False
    
    def __init__(self, PinTx=2, PinRx=4, baudrate_=115200, timeout_=0):
        
        self.uart = SoftUART(
            Pin(PinTx), Pin(PinRx), 
            baudrate=baudrate_, 
            timeout=timeout_) 
        
        self.mStart = bytearray()
        self.nEr = 0
        self.rxActive = False
    
    def writeOk(self):
        self.uart.write("Ok")
    def writeRe(self):
        self.uart.write("Re")
    def writePing(self):
        self.uart.write("$ping")
        
    
    def readToBuf(self, iterForLog = 0):
        self.rxActive = True
        c = self.uart.read(1)
        while c:
            #print("C",c)
            if c in [ b'\r', b'\n']:
                self.rxActive = False
                if 1:
                    a = None
                    try:
                        a = self.mStart.decode('ascii')
                    except:
                        self.nEr+= 1
                    
                    self.mStart = bytearray()
                        
                    if a != None:
                        return a 
                        self.buf.append( a )
                        if len(self.buf)>10:
                            self.buf.pop(0)
                            #print("MySUart.buf.pop")
                        #print(str(iterForLog),"@uart:",self.buf[-1][:5])
                        
                    
            else:
                self.mStart.append(c[0]) 
                
            if len(self.mStart)>512:
                self.mStart = bytearray()
                while self.uart.read(1):
                    aaabc = 0
                break
                
            c = self.uart.read(1)

        
        #print("buf",self.buf)
        self.rxActive = False
        return None

          
