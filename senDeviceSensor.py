from TimeHelper import TimeHelper
from plyer import light
from plyer import battery
from plyer import brightness
import traceback
from senProto import senProto
#import psutil


class deviceSensors(senProto):
    def __init__(self,gui):
        super(deviceSensors, self).__init__()
        self.gui = gui
        self.th = TimeHelper()
        self.title = 'device'
        self.type = self.title
        
        self.upTimeStart = self.th.getTimestamp()
        
        self.battery = {
            "ok": None,
            "charging": None,
            "percent": None
            }
        self.light = {
            "ok": None,
            "val": None
            }
        self.backlight = {
            "ok": None,
            'org': None,
            'current': None
            }
        self.uptime = 0.0
        self.uptimeNice = ""
        
        self.iterCount = 0
        self.updateEvery = 5
        
    def updateUptime(self):
        ts = self.th.getTimestamp()
        self.uptime = ts - self.upTimeStart
        self.uptimeNice = self.th.getNiceHowMuchTimeItsTaking(self.uptime)
        
    def getValuesOptions(self):
        return {'dict':[
            'lightLumens', 
            'batteryCharging', 
            'batteryPercentage', 
            'bgLight',
            'app uptime sec.',
            'app uptime nice',
            'cpu percent',
            'mem total',
            'mem percent use',
            'cpu avg 1',
            'cpu avg 2',
            'cpu avg 3'
            ]}
        
    def getTitle(self):
        return self.title
    
        
    def initSensors(self):
        try:
            light.enable()
            self.light = {
                'ok' : True,
                'val': light.illumination 
                }
            print("light Yes!")
        except Exception:
            print( traceback.format_exc() )
            print("light NO")
            self.light['ok'] = False
            
            
        
        
        try:
            self.battery = {
                "ok": True,
                "charging": battery.status['isCharging'],
                "percent": battery.status['percentage']
                }
            print("battery Yes!")
        except Exception:
            print( traceback.format_exc() )
            print("battery NO")
            self.battery['ok'] = False
            
        try:
            brig = brightness.current_level()
            self.backlight = {
                "ok": True,
                "org" :brig,
                "current": brig
                }
            print("backlight Yes!")
        except Exception:
            print( traceback.format_exc() )
            print("backlight NO")
            self.backlight['ok'] = False
            
        #sys.exit(0)
        
    def iter(self):
        doGuiUpdate = True if self.gui.rl.current == "Sensors" else False
        
        self.updateUptime()
        tcb = {
            'app uptime sec.': self.uptime,
            'app uptime nice': self.uptimeNice
            }
        
        #tcb['cpu percent'] = int(psutil.cpu_percent())
        #memS = psutil.virtual_memory()
        #memSplit = str(memS).replace("(", " ").replace(")", " ").replace(",", "").split(" ")
        #tcb['mem total'] = int(memSplit[1][6:])
        #tcb['mem percent use'] = float(memSplit[3][8:])
        #loadA = list(psutil.getloadavg())
        #tcb['cpu avg 1'] = loadA[0]
        #tcb['cpu avg 2'] = loadA[1]
        #tcb['cpu avg 3'] = loadA[2]
        try:
            aoe =1
        except:
            print("EE - senDeviceSensor psutil ")
            
        
        if not self.iterCount % self.updateEvery:        
            if self.light['ok']:
                self.light['val'] = light.illumination
                tcb['lightLumens'] = self.light['val'] 
                
            if self.battery['ok']:
                self.battery['charging'] = battery.status['isCharging']
                tcb['batteryCharging'] = self.battery['charging']
                self.battery['percent'] = battery.status['percentage']
                tcb['batteryPercentage'] = battery.status['percentage']
                
                
            if self.backlight['ok']:
                brig = brightness.current_level()
                self.backlight['current'] = brig
                tcb['bgLight'] = brig
                
            #for o in self.callBacksForUpdate:
            #    o.update(self.title, tcb)
            self.broadcastCallBack(self.gui, self.title, tcb)
            
            for k in tcb.keys():
                v = tcb[k]
                self.broadcastByMqtt(
                    self.gui, 
                    "ykpilot/device/{}".format(k.replace(" ","_")), 
                    str(v)
                    )    
            
                
        self.iterCount+= 1
        
        
        # callbacks
        
        