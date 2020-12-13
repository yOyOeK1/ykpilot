from TimeHelper import TimeHelper


class senDTH:
    
    def __init__(self,gui,type_):
        self.gui = gui
        self.type_ = type_
        self.title = type_
        self.callBacksForUpdate = []
        self.th = TimeHelper()
        self.lastIter = 0
        self.history = []
        self.maxHistory = 50
    
    def getTitle(self):
        return self.title
    
    def getValuesOptions(self):
        tr = { 'dict' : [
                'humidity','C','F'
                ]
            }
        return tr
    
    def addCallBack(self, obj):
        print("addCallBack to [",self.title,"] obj ",obj)
        self.callBacksForUpdate.append( obj ) 
    
    def removeCallBack(self, obj):
        for i,o in enumerate(self.callBacksForUpdate):
            if o == obj:
                self.callBacksForUpdate.pop(i)
                return True
    
    def update(self, val):
        print("sen.",self.type_,".update val",val)
        
        self.history.append(val)
        if len(self.history)>self.maxHistory:
            self.history.pop(0)
        
        for o in self.callBacksForUpdate:
            o.update(self.type_, val)
    
    
    