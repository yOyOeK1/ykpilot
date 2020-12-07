from TimeHelper import TimeHelper


class senSeatalk:
    
    def __init__(self,gui,type_):
        self.gui = gui
        self.type_ = type_
        self.title = type_
        self.callBacksForUpdate = []
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
    
    def addCallBack(self, obj):
        print("addCallBack to [",self.title,"] obj ",obj)
        self.callBacksForUpdate.append( obj ) 
    
    def removeCallBack(self, obj):
        for i,o in enumerate(self.callBacksForUpdate):
            if o == obj:
                self.callBacksForUpdate.pop(i)
                return True
    
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
        
        for o in self.callBacksForUpdate:
            o.update(self.type_, self.vals)
           
        
        