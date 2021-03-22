import sys
from TimeHelper import *
from _functools import partial
from kivy.clock import Clock


class senProto:
    
    def __init__(self):
        self.th = TimeHelper()
        self.callBackForUpdate = []
        self.callOnScreen = []
        self.callLastTime = []
        self.callEvery = []
        
        
    def lookForScreen(self,obj):
        print("lookForScreen",obj)
        try:
            p = obj.parent
            if p:
                self.lookForScreen(p)
        except:
            pass
        
    def addCallBack(self, obj, onScreen='*', maxUpdateEvery=0):
        print("addCallBack to [",self.title,"] obj ",obj)
        self.callBackForUpdate.append( obj )
        self.callOnScreen.append(onScreen) 
        self.callLastTime.append(-1)
        self.callEvery.append(maxUpdateEvery*1000000)
        
    def removeCallBack(self, obj):
        for i,o in enumerate(self.callBackForUpdate):
            if o == obj:
                self.callBackForUpdate.pop(i)
                self.callOnScreen.pop(i)
                self.callLastTime.pop(i)
                self.callEvery.pop(i)
                
    
    def broadcastByTCPNmea(self, gui, msg):
        if gui.config['nmeBNmea']:
            gui.sf.sendToAll(msg)
    
    def broadcastByTCPJson(self, gui, msg):
        if gui.config['nmeBSensors']:
            gui.sf.sendToAll(msg)
            
    def broadcastCallBack(self, gui, fromWho, vals):
        #return None
        #print("--- call backs---[",self.type,"]-------")
        #for ii,c in enumerate(self.callOnScreen):
        #    print(ii," on screen",c,"->",self.callBackForUpdate[ii])
        
        
        if gui.isReady:
            t = self.th.getTimestamp(True)
            
            cs = gui.rl.current
            if cs[:7] == 'Widgets':
                cs = 'Widgets'
            for ii,s in enumerate(self.callOnScreen):
                if s == '*' or cs in s:
                    if self.callEvery[ii] == 0 or (t-self.callLastTime[ii])>=self.callEvery[ii]:
                        #print("send... ",self.type," to ",self.callBackForUpdate[ii])
                        self.callBackForUpdate[ii].update(fromWho,vals)
                        #Clock.schedule_once( lambda x : self.callBackForUpdate[ii].update(fromWho, vals), 0.01 )
                        self.callLastTime[ii] = t
                    
                        
                else:
                    pass
                    #print("skip (not correct screen)",self.type," to ",self.callBackForUpdate[ii])
                