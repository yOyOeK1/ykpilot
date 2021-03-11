from TimeHelper import TimeHelper
from plyer import light
from plyer import battery
from plyer import brightness
import traceback
from senProto import senProto


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
            'app uptime nice']}
        
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
                
        self.iterCount+= 1
        
        
        # callbacks
        
        