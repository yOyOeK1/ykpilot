from TimeHelper import TimeHelper
from senProto import senProto


class senMqttTopic(senProto):
    
    def __init__(self,gui,type_):
        super(senMqttTopic,self).__init__()
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
                'v',
                'tUpdate'
                ]
            }
        return tr
    
    def update(self, val):
        try:
            val = val.decode()
        except:
            #print("sen.",self.type_,".update val[",val,"]",
            #    "val type",type(val))
            #print("EE - senMqttToic.update val",val)
            
            if val == "True":
                val = 1
            elif val == "False":
                val = 0
            
            
            '''try:
                val = float(val)
                print("II - try as float? out",val)
            except:
                print("II - as a string then")
            '''
        val = {
            'v':val,
            'tUpdate':self.th.getTimestamp(True)
            }
        self.history.append(val)
        if len(self.history)>self.maxHistory:
            self.history.pop(0)
        
        self.broadcastCallBack(self.gui, self.type, val)
    
    