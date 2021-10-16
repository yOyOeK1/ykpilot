import time
from machine import Pin
import uasyncio as uaio

class MyAp:
    isAuto = False
    
    pNoLeft = 5
    pLeft = None
    pNoRight = 4
    pRight = None
    pNoCloutch = 0
    pCloutch = None
    
    apTargetDirection = None
    
    def __init__(self):
        print("MyAp.init")
        self.pLeft = Pin( self.pNoLeft, Pin.OUT)
        self.pinOff( self.pLeft )
        self.pRight = Pin( self.pNoRight, Pin.OUT)
        self.pinOff( self.pRight )
        self.pCloutch = Pin( self.pNoCloutch, Pin.OUT)
        self.pinOff( self.pCloutch )
        
        self.apTargetDirection = -11
        print("MyAp.init    DONE")
        
    def setNewDirection(self,direction):
        self.apTargetDirection = direction
    
    def pinOn(self, p):
        p.off()
    def pinOff(self,p):
        p.on()
    
    def pinOffAll(self):
        self.pinOff( self.pLeft )
        self.pinOff( self.pRight )
        self.pinOff( self.pCloutch )
    
    
    async def runItAsync(self):
        while True:
            await uaio.sleep_ms(500)
            self.iter( self.apTargetDirection )
            self.apTargetDirection = -11
    
    # 0 - is iter no direction / auto mode ON
    # 1 - left / auto mode On
    # 2 - rigth / auto mode On
    # others - stand by / auto mode Off
    def iter(self, direction = -1):
        if direction in [0,1,2]:
            self.pinOff( self.pLeft )
            self.pinOff( self.pRight )
            self.pinOn( self.pCloutch )
            self.isAuto = True
            
        else:
            self.isAuto = False
            self.pinOffAll()
        
        if direction == 1:
            self.pinOn( self.pLeft )
        elif direction == 2:
            self.pinOn( self.pRight )
                      
            
            
        
        