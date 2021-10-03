from TimeHelper import TimeHelper
from plyer import light
from plyer import battery
from plyer import brightness
import traceback
from senProto import senProto
from hbMqttClient import hbMqttClient
import sys
from DataSaveRestore import DataSR_save, DataSR_restore
from _ast import Try


class senMqttClient(senProto,hbMqttClient):
    def __init__(self,gui):
        super(senMqttClient, self).__init__()
        hbMqttClient.__init__(self)
        self.gui = gui
        self.th = TimeHelper()
        self.title = 'mqtt client'
        self.type = self.title
        
        self.upTimeStart = self.th.getTimestamp()
        
        self.iterCount = 0
        self.online = False
        self.dictionary = {'dict':[]}
        self.values = {}
        
    def updateUptime(self):
        ts = self.th.getTimestamp()
        self.uptime = ts - self.upTimeStart
        self.uptimeNice = self.th.getNiceHowMuchTimeItsTaking(self.uptime)
        
    def getValuesOptions(self):
        return self.dictionary
    
    def configSave(self,gui):
        print("senMqttClient.configSave")
        va = {}
        for t in self.values.keys():
            print(t)
            va[t]= {
                'top': self.values[t]['top'],
                'tim': self.values[t]['tim'],
                'obj': ""
                }
            try:
                va[t]['msg'] = ""#self.values[t]['msg'].decode('UTF-8')
            except:
                print("EE - decoding no [{}]".format(self.values[t]['msg']))
                va[t]['msg'] = ""
        
        print("save config res", DataSR_save(
            va, 
            gui.fa.join( gui.homeDirPath,'ykpilotSenMqttClient.conf')
            )
        )
        
    def restoreFromFile(self,gui):
        print("senMqttClient.restoreFromFile")
        res = DataSR_restore(
            gui.fa.join( gui.homeDirPath,'ykpilotSenMqttClient.conf')
            )
        print("res:",res)
        if res == None:
            return 0
        print("------------")
        for t in res.keys():
            i = res[t]
            print("topic:",i['top']," >> ",i['msg'])
            gui.sen.hbmq.inBuf.append([i['top'],i['msg']])
        print("build used sensors ...")
        gui.sen.hbmq.hbmakeStacks(gui,True)
        gui.sen.hbmq.iter()
        print("--------------------")
        print("list of sensors",gui.sen.sensorsListStr)
        print("senMqttClient.restoreFromFile DONE")
        
        
    def getTitle(self):
        return self.title
    
        
    def initSensors(self):
        print("initSensors")
        #sys.exit(0)
        
    def iter(self):
        
        if 1:#self.hbClientStats()
            self.hbmakeStacks(self.gui)
        
        doGuiUpdate = True if self.gui.rl.current == "Sensors" else False
        
        self.iterCount+= 1
        
        # callbacks
        
        
        
        