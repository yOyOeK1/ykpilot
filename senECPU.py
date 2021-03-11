from TimeHelper import TimeHelper
from senMsgTypeDetector import senMsgTypeDetector
from senProto import senProto



class senECPU(senMsgTypeDetector,senProto):
    
    def __init__(self,gui,type_):
        super(senECPU,self).__init__()
        self.gui = gui
        self.type_ = type_
        self.type = self.type_
        self.title = type_
        self.th = TimeHelper()
        self.lastIter = 0
        self.maxHistory = 50
        self.history = []
    
    def getTitle(self):
        return self.title
    
    def getValuesOptions(self):
        tr = { 'dict' : [
                'uart'
                ]
            }
        return tr
    
    def update(self, val):
        #print("sen.",self.type_,".update val",val)
        self.history.append(val)
        if len(self.history)> self.maxHistory:
            self.history.pop(0)
        
        cmds = self.msgDetParse(val)
        val = { 'uart': val }
        
        #for o in self.callBacksForUpdate:
        #    o.update(self.type_, val)
        self.broadcastCallBack(self.gui, self.type, val)
    
    
    