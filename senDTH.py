from TimeHelper import TimeHelper
from senProto import senProto


class senDTH(senProto):
    
    def __init__(self,gui,type_):
        super(senDTH,self).__init__()
        self.gui = gui
        self.type_ = type_
        self.type = self.type_
        self.title = type_
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
    
    def update(self, val):
        print("sen.",self.type_,".update val",val)
        
        self.history.append(val)
        if len(self.history)>self.maxHistory:
            self.history.pop(0)
        
        #for o in self.callBacksForUpdate:
        #    o.update(self.type_, val)
        self.broadcastCallBack(self.gui, self.type, vals)
    
    
    