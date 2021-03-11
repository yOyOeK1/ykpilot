from TimeHelper import TimeHelper
from senProto import senProto


class senSeatalk(senProto):
    
    def __init__(self,gui,type_):
        super(senSeatalk,self).__init__()
        self.gui = gui
        self.type_ = type_
        self.type = self.type_
        self.title = type_
        self.th = TimeHelper()
        self.lastIter = 0
        self.valReturnDesc = { 'dict' : [] }
        self.vals = {}
        
        self.stHis = []
        self.stHistoryLength = 100
    
    def getTitle(self):
        return self.title
    
    def getValuesOptions(self):
        return self.valReturnDesc
    
    def update(self, val):
        #print("sen.",self.type_,".update val",val)
        
        self.stHis.append(val)
        if len(self.stHis) > self.stHistoryLength:
            self.stHis.pop(0)
            
        keys = list(val.keys())
        for k in keys:
            self.vals[k] = val[k]
            try:
                abccc = self.valReturnDesc['dict'].index(k)
            except:
                self.valReturnDesc['dict'].append(k)
            
        print("senSeatalk vals",self.vals)
        
        #for o in self.callBacksForUpdate:
        #    o.update(self.type_, self.vals)
        self.broadcastCallBack(self.gui, self.type, self.vals)
           
        
        