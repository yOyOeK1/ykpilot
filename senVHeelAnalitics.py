from TimeHelper import TimeHelper
from FileActions import FileActions
from DataSaveRestore import DataSR_restore, DataSR_save
from senProto import senProto
import numpy as np
from PCPlot import PCPlot
from myFastPlot import myFastPlot
from kivy.clock import Clock

class senVHeelAnalitics(senProto):
    
    def __init__(self, gui, type_):
        super(senVHeelAnalitics,self).__init__()
        self.th = TimeHelper()
        self.fa = FileActions()
        self.gui = gui
        self.type = type_
        self.title = self.type
        self.iter = 0
        
        self.historyMem = 60*1000000 #millisec
        
        self.smoothBy = (1/7.0)*10000000
        
        self.d = []
        self.ds = []
        self.t = []
        self.anglef = []
        self.tLast = None
        
        self.data = {
            'total min':None,
            'total max':None,
            'total avg':None,
            'current min':None,
            'current max':None,
            'current avg':None,
            'angle':None,
            'angle F': None,
            'phase':None,
            'hz':None,
            'phase in sec':None,
            'count':None,
            }
        
        #Clock.schedule_once(self.on_plt, 2)
        
    def on_plt(self,a=0):
        self.pltBuff = myFastPlot(
            [
                self.p_rawHeel,
                self.p_angle,
                self.p_cavg,
                self.p_angleF,
                
             ],
            inBuffer = True)
        self.pltBuff.runBuffMode(self.gui.rl.ids.l_pltSpot)
        
        
    def p_rawHeel(self):
        return self.t,self.d
    
    def p_angle(self):
        return self.t,self.ds
    
    def p_cavg(self):
        try:
            x = [self.t[0],self.t[-1]]
            y = [self.data['current avg'],self.data['current avg']]
            return x,y
        except:
            return [0],[0]
        
    def p_angleF(self):
        return self.t,self.anglef
            
      
    def getTitle(self):
        return self.type
    
    def getValuesOptions(self):
        return { 'dict' : [
                    'total min',
                    'total max',
                    'total avg',
                    'current min',
                    'current max',
                    'current diff',
                    'current avg',
                    'angle',
                    'angle F',
                    'phase',
                    'hz',
                    'phase in sec',
                    'count'
                    ]
                }
        
    def getVals(self):
        return self.data
    
    def update(self,fromWho,val):
        #print("update senVHeelAnalitics from[",fromWho,"] ->",val)        
        self.iter+=1
        
        t = self.th.getTimestamp(True)
        
        self.d.append(val[4])
        self.t.append(t)
        
        s = len(self.d)-1
        ssum = 0.0
        scount = 0
        tUp = t-self.smoothBy
        while s >=0 :
            if self.t[s] >= tUp:
                scount+=1
                ssum+= self.d[s]
                
            s-=1
        if scount > 0:
            sangle = round(ssum/scount,1)
            self.data['angle'] = sangle
            self.ds.append(sangle)
        else: 
            self.ds.append(self.ds[-1])
            
            
        if len(self.ds)>5:
            angleF = ((np.sum(self.ds[-4:])/4.0)-self.ds[-1])/((t-self.tLast)/1000000.)
            angleF = (np.sum(self.ds[-4:])+angleF)/5.0
            
            self.data['angle F'] = angleF
            print("angle f",angleF,
                  ' angle dif ',(self.ds[-2]-self.ds[-1]),
                  ' time',((t-self.tLast)/1000000.),
                  ' angless ',self.ds[-4:])
            
            
            
            self.anglef.append(angleF)
        else:
            self.anglef.append(0.0)
            
            
        cmin = np.min(self.d)
        cmax = np.max(self.d)
        cavg = np.sum(self.d)/len(self.d)
        cdiff = cmax-cmin
        
        self.data['current min'] = cmin
        self.data['current max'] = cmax
        self.data['current avg'] = cavg
        self.data['current diff'] = cdiff
        
    
    
        if self.t[0] < (t-self.historyMem):
            self.d.pop(0)
            self.ds.pop(0)
            self.t.pop(0)
            self.anglef.pop(0)
            #print("pop",len(self.t))
        self.broadcastCallBack(self.gui, self.type, self.data)
        
        self.tLast = t
        