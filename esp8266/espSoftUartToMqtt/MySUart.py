from machine import SoftUART, Pin

class MySUart:
    
    uart = None
    buf = []
    mStart = None
    nEr = 0
    
    def __init__(self, PinTx=2, PinRx=4, baudrate_=4800, timeout_=0):
        
        self.uart = SoftUART(
            Pin(PinTx), Pin(PinRx), 
            baudrate=baudrate_, 
            timeout=timeout_) 
        
        self.mStart = bytearray()
        self.nEr = 0
    
    def readToBuf(self, iterForLog = 0):
        c = self.uart.read(1)
        while c:
            if c in [ b'\r', b'\n']:
                if len(self.mStart)<3:
                    self.mStart = bytearray()
                else:
                    try:
                        self.buf.append( self.mStart.decode('ascii') )
                        #print(str(iterForLog),"@uart:",self.buf[-1][:5])
                    except:
                        #print("E - to ascii 532[",self.mStart,"]")
                        self.nEr+= 1
                    self.mStart = bytearray()
                    
            else:
                self.mStart.append(c[0]) 
                
            if len(self.mStart)>512:
                self.mStart = bytearray()
                break
                
            c = self.uart.read(1)

        
        #print("buf",self.buf)
        
        return len(self.buf)

          
