from TimeHelper import TimeHelper
from FileActions import FileActions
from DataSaveRestore import DataSR_restore, DataSR_save
from pygeodesy.ellipsoidalVincenty import LatLon
from senProto import senProto

class odometer(senProto):
    
    def __init__(self, gui, type_):
        super(odometer,self).__init__()
        self.th = TimeHelper()
        self.fa = FileActions()
        self.gui = gui
        self.type = type_
        self.title = self.type
        self.iter = 0
        
        self.data = {
            'total':0.0,
            'trip':0.0,
            'iters':0,
            'total iters': 0
            }
        
        self.dataFilePath = self.fa.join(
            self.gui.homeDirPath,
            "sensorOdometer.conf"
            )
        if self.fa.isFile(self.dataFilePath):
            self.data = DataSR_restore(self.dataFilePath)
            print("odometer have config !",self.data)
            print("zero trip, iter!")
            self.data['trip'] = 0.0
            self.data['iters'] = 0
        else:
            print("odometer first run ? no config file")
        
        
    def saveData(self):
        print("odometer save data")
        print("    res",DataSR_save(self.data, self.dataFilePath))
        
    def getTitle(self):
        return self.type
    
    def getValuesOptions(self):
        return { 'dict' : [
                    'total', 
                    'trip',
                    'iters',
                    'total iters'
                    ]
                }
        
    def getVals(self):
        return self.data
    
    def update(self,fromWho,val):
        #print("update from[",fromWho,"] ->",val)
        if fromWho == 'gps':
            if self.iter == 0:
                self.lastT = self.th.getTimestamp(microsec=True)
                self.lastVal = val
                self.lastLL = LatLon(val['lat'],val['lon'])
            else:
                t = self.th.getTimestamp(microsec=True) 
                ll = LatLon(val['lat'],val['lon'])
                dis =  ll.distanceTo(self.lastLL)
                tSince = (self.lastT-t)/1000000.0
                dis = (( dis/1000.00 )/tSince)
                if dis < 0.0:
                    dis = -dis 
                self.data['total']+= dis
                self.data['trip']+= dis
                self.data['iters'] = self.iter
                self.data['total iters']+=1
                
                self.lastT = t
                self.lastVal = val
                self.lastLL = ll
                
                #if self.gui.isReady:
                #    # callbacks
                #    for o in self.callBacksForUpdate:
                #        o.update(self.type, self.data) 
                self.broadcastCallBack(self.gui, self.type, self.data)
        
            self.iter+=1
    
        