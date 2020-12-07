from TimeHelper import TimeHelper
from senMsgTypeDetector import senMsgTypeDetector



class senECPU(senMsgTypeDetector):
    
    def __init__(self,gui,type_):
        self.gui = gui
        self.type_ = type_
        self.title = type_
        self.callBacksForUpdate = []
        self.th = TimeHelper()
        self.lastIter = 0
        self.buf = []
        self.history = 200
    
    def getTitle(self):
        return self.title
    
    def getValuesOptions(self):
        tr = { 'dict' : [
                'uart'
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
        #print("sen.",self.type_,".update val",val)
        self.buf.append(val)
        if len(self.buf)> self.history:
            self.buf.pop(0)
        
        cmds = self.msgDetParse(val)
        val = { 'uart': val }
        
        for o in self.callBacksForUpdate:
            o.update(self.type_, val)
    
    
    