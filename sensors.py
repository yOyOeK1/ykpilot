
import kivy
import math
import ast
import traceback
from kivy.clock import Clock, mainthread
from kivy.vector import Vector
from kivy.uix.spinner import Spinner
from kivy.properties import NumericProperty,ObjectProperty,StringProperty
from plyer import gps, accelerometer,compass,gyroscope,spatialorientation
from plyer import light
from plyer import battery
from plyer import brightness
from TimeHelper import *
from FileActions import *
from pygeodesy import dms
from pygeodesy.ellipsoidalVincenty import LatLon
from QueryPopup import QueryPopup
from fftAnalisy import fftPlotData
import numpy as np
import _thread
import sys
from DataSaveRestore import DataSR_save, DataSR_restore
from waveCicleHolder import waveCicleHolder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout


def transform90axis( upAxis, vals ):
    # x - on side
    # y - upright
    # z - flat
    #[ -x, -y, z]
    if upAxis == 'x':
        return [-vals[1],-vals[2],vals[0]]
    elif upAxis == 'y':
        return [vals[0],-vals[2],vals[1]]
    elif upAxis == 'z': 
        return [vals[0],vals[1],vals[2]]

class deviceSensors:
    def __init__(self,gui):
        self.gui = gui
        self.th = TimeHelper()
        self.title = 'device'
        self.callBacksForUpdate = []
        
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
    
    def addCallBack(self, obj):
        print("addCallBack to [",self.title,"] obj ",obj)
        self.callBacksForUpdate.append( obj ) 
        
    def removeCallBack(self, obj):
        for i,o in enumerate(self.callBacksForUpdate):
            if o == obj:
                self.callBacksForUpdate.pop(i)
                return True
        
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
            self.backlight = {
                "ok": True,
                "org" :brightness.current_level(),
                "current": brightness.current_level()
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
                if doGuiUpdate: self.gui.rl.ids.lSenLum.text = str(self.light['val'])
                
            if self.battery['ok']:
                self.battery['charging'] = battery.status['isCharging']
                tcb['batteryCharging'] = self.battery['charging']
                self.battery['percent'] = battery.status['percentage']
                tcb['batteryPercentage'] = battery.status['percentage']
                
                if doGuiUpdate: self.gui.rl.ids.lSenBatCha.text = str(self.battery['charging'])
                if doGuiUpdate: self.gui.rl.ids.lSenBatPer.text = str(self.battery['percent'])
                
            if self.backlight['ok']:
                self.backlight['current'] = brightness.current_level()
                tcb['bgLight'] = brightness.current_level()
                if doGuiUpdate: self.gui.rl.ids.lSenBacOrg.text = str(self.backlight['org'])
                if doGuiUpdate: self.gui.rl.ids.lSenBacCur.text = str(self.backlight['current'])
            
            for o in self.callBacksForUpdate:
                o.update(self.title, tcb)
                
        self.iterCount+= 1
        
        
        # callbacks
        
        
            

class micData:
    def __init__(self,gui):
        self.gui = gui
        self.th = TimeHelper()
        self.work = False
        
    def on_record(self,o):
        print("o.active",o.active)
        if self.work:
            self.work = False
        else:
            self.work = True
            _thread.start_new(self.runIt,())
        
        
    def runIt(self):
        import pyaudio
        import struct
        import matplotlib.pyplot as plt
        import numpy as np
        import time
        
        pyaudioDisplay = True
        
        
        mic = pyaudio.PyAudio()
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        CHUNK = 64*4
        stream = mic.open(
            format=FORMAT, 
            channels=CHANNELS, 
            rate=RATE, 
            input=True, 
            frames_per_buffer=CHUNK)
        
        reciter = 1
        dataHistory = []
        dataMem = 10
        lastTime = self.th.getTimestamp()
        recIterLast = 0
        im = np.zeros( (512,512,3), dtype=np.uint8)
        imY = 0
        imX = 0
        while self.work:
            reciter+= 1
            
            
            
            dataHistory.append( stream.read(CHUNK) )
            if len(dataHistory) > dataMem:
                dataHistory.pop(0)
            
            #print(".")
            if pyaudioDisplay and len(dataHistory)>5:
                dataHistory[-1] = np.frombuffer( dataHistory[-1], np.int16)
                
                if len(dataHistory)>3:                
                    fftPlotData(self.gui.pMic2, np.array([ *dataHistory[-1], *dataHistory[-2], *dataHistory[-3] ]))
                    #fftPlotData(self.gui.pMic1, np.array([ *dataHistory[-1], *dataHistory[-2]] ))
                    fftPlotData(self.gui.pMic, dataHistory[-1])
                #self.gui.pMic
                
            else:
                time.sleep(0.1)

            
            t = self.th.getTimestamp()
            if (t-lastTime)>1:
                print("iters in sec ",(reciter-recIterLast)," y ",imY)
                recIterLast = reciter
                lastTime = t
                
                if imY > 20:
                    imY = 0
                    print('save img')
                    from PIL import Image
                    new_img = Image.fromarray(im)
                    new_img.save("fox.png")
                
            if True:
                res = fftPlotData(None, dataHistory[-1])
                a = []
                b = []
                try:
                    for i in res:
                        a.append(i[0])
                        b.append(i[1])
                    
                    m = max(b)
                    i = b.index(m)
                    
                    if b[10] >0.5:
                        im[imY][imX][0] = 250
                        im[imY][imX][1] = 250
                        im[imY][imX][2] = 250
                except:
                    pass
                
                imX+= 1
                if imX > 274*2:
                    imX = 0
                    imY+= 1
            
            
class gpsData:
    status = "---"
    androidServiceStatus = False
    lat = 0.0
    lon = 0.0
    avgSog = 0.0
    avgCog = 0.0
    maxSog = 0.0
    gpsSog = 0.0
    gpsCog = 0.0
    cog = 0
    sog = 0
    accur = -1
    updateTime = -1
    iter = 0
    avgReadings = 0.95
    avgPos = [None,None]
    oldData = {}
    callBacksForUpdate = []
    llOld = [None, None]
    
    def __init__(self,gui,debGuiObjts={}):
        self.gui = gui
        self.guiObjs = debGuiObjts
        self.th = TimeHelper()
        self.title = "gps"
    
    def getTitle(self):
        return self.title
    
    def getValuesOptions(self):
        tr = { 'dict' : [
                'lat','lon','speed','bearing','accuracy',
                'avgSog','avgCog'
                ]
            }
        return tr
    
    def getVals(self):
        return [ self.lat, self.lon, self.cog, self.sog ]
    
    def addCallBack(self, obj):
        print("addCallBack to [",self.title,"] obj ",obj)
        self.callBacksForUpdate.append( obj ) 
    
    def removeCallBack(self, obj):
        for i,o in enumerate(self.callBacksForUpdate):
            if o == obj:
                self.callBacksForUpdate.pop(i)
                return True
    
    def update(self, val):
        self.iter+= 1
        if self.avgPos[0] == None:
            self.avgPos = [ val['lat'],val['lon'] ]
            self.lat = val['lat']
            self.lon = val['lon']
        
        self.avgPos[0] = (self.avgPos[0]*self.avgReadings)+(val['lat']*(1.0-self.avgReadings))
        self.avgPos[1] = (self.avgPos[1]*self.avgReadings)+(val['lon']*(1.0-self.avgReadings))
        
        doIt = True
        
        tSinceLast = (self.th.getTimestamp(True)-self.updateTime)/1000000.0
        
        if tSinceLast < 0.5:
            doIt = False
        else:
            #print("-----------------")
            #print("time since last",tSinceLast)
            
            pavg = LatLon( self.avgPos[0], self.avgPos[1] )
            pNew = LatLon( val['lat'], val['lon'])
            dis = pavg.distanceTo(pNew)
            spe = (( dis/1000.00 )/tSinceLast)*60.0*60.0
            self.sog = (spe*0.539957) # to nm
            self.cog = pavg.bearingTo(pNew)
            #print("distance is ",dis)
            if spe > 100.00:
                doIt = False
                print( "gps data Dump to fast ! ",
                    "Speed is ",spe," km/h"
                    )
        if doIt:
            self.lat = val['lat']
            self.lon = val['lon']        
            self.gpssog = val['speed']
            if self.maxSog < self.sog:
                self.maxSog = self.sog
            self.avgSog = (self.avgSog*self.avgReadings)+(self.sog*(1.0-self.avgReadings))
            val['avgSog'] = self.avgSog
            
            
            self.gpscog = val['bearing']
            self.avgCog = (self.avgCog*self.avgReadings)+(self.gpssog*(1.0-self.avgReadings))
            val['avgCog'] = self.avgCog
            
            self.accur = val['accuracy']        
            
            self.updateTime = self.th.getTimestamp(True)
            
            # nmea
            latRaw = dms.latDMS( self.lat,form=dms.F_DM,prec=6).replace('°','').replace('′','')
            latDM = latRaw[:-1]
            latNS = latRaw[-1]
            lonRaw = dms.lonDMS( self.lon,form=dms.F_DM,prec=6).replace('°','').replace('′','')
            lonDM = lonRaw[:-1]
            lonEW = lonRaw[-1]
            msg = ("$YKRMC,,A,%s,%s,%s,%s,%s,%s,,,,A"%(latDM,latNS,lonDM,lonEW,round(self.sog,2),round(self.cog,2)))
            self.gui.sf.sendToAll(msg)
            
            
            if self.gui.rl.current == "Sensors": 
                self.guiObjs['lat'].text = "%s"%self.lat
                self.guiObjs['lon'].text = "%s"%self.lon
                self.guiObjs['accur'].text = "%s"%round(self.accur,0)
                self.guiObjs['cog'].text = "%s / %s"%(round(self.gpscog,1), round(self.cog,1))
                self.guiObjs['sog'].text = "%s / %s"%(round(self.gpssog,2), round(self.sog,2))
            
            if self.gui.rl.current == "Race":
                self.guiObjs['lSRacSog'].text = "%s" % round(self.sog,1)
                self.guiObjs['lSRacSogMax'].text = "max: %s" % round(self.maxSog,2)
                self.guiObjs['lSRacSogAvg'].text = "avg: %s" % round(self.avgSog,2)
            
            if self.gui.isReady:
                # callbacks
                for o in self.callBacksForUpdate:
                    o.update('gps', val)
                
                # json
                jMsg = str({
                    "type": "gps",
                    "data": val
                    })
                self.gui.sf.sendToAll( jMsg )
        
        
class xyzData:
    historyMem = 1010
    
    uSEvery = 5.0
    
    guiUpdateEvery = 1.0
    
    guiArrowsAccel = False
    guiGraphAngle = False
    guiGraphCompas = False
    guiGraphDbHeelPitch = False
    guiGraphGyro = False
    guiGraphHeelPitch = False
    
    
    def __init__(self, gui, type_, debGuiObjcts=[]):
        self.th = TimeHelper()
        self.fa = FileActions()
        self.callBacksForUpdate = []
        self.gui = gui
        self.type = type_
        self.title = self.type
        self.iter = 0
        self.avgFraction = 0.92
        self.guiObjs = debGuiObjcts
        self.history = []
        self.lastVal = None
        self.propagateVal = True
        self.axis = {
            'x':[],
            'y':[],
            'z':[]
            }
        
        self.uSTLast = self.th.getTimestamp(True)
        self.uSCount = 0
        self.guiUTLast = self.uSTLast
        
        
        self.lastTimeIter = 0
        
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.xOff = 0.0
        self.yOff = 0.0
        self.zOff = 0.0
        self.updateTime = -1
        #for heel slope detection
        self.hsbOld = 0.0
        self.avgHdg = 0.0

        if True:
            listConfig = DataSR_restore(
                self.fa.join( self.gui.homeDirPath,"ykpilot_calibration.conf" )
                )
            try: 
                key = "%s.offset"%self.type
                print("    key: ",key," -> ",listConfig[key])
                self.setOffset(listConfig[key])
                print("    from config file")
            except:
                print("    no config for %s"%key)

            try:
                self.gui.rl.ids.lModSimGyroHeelHz.text = str(round(listConfig['heelHz'],2))
                self.gui.rl.ids.lModSimGyroPitchHz.text = str(round(listConfig['pitchHz'],2))
            except:
                pass


        else:
            print(" no config fille")
    
    def getTitle(self):
        return self.type
    
    def getValuesOptions(self):
        if self.type in [ 'gyro', 'gyroFlipt', 'accel', 'accelFlipt', 'spacorientation' ]:
            return { 'list' :
                ['x', 'y', 'z']
                }
        elif self.type in [ 'comCal', 'comCalAccelGyro']:
            return { 'list':
                ['hdg',  'avgHdg']
                }
        elif self.type == 'orientation':
            return { 'list':
                ['x','y','z','pitch','heel']
                }
        else:
            print("EE - sensor not define !!!")
            
        return None
    
    
    def addCallBack(self, obj):
        print("addCallBack to [",self.title,"] obj ",obj)
        self.callBacksForUpdate.append( obj ) 
    
    def removeCallBack(self, obj):
        for i,o in enumerate(self.callBacksForUpdate):
            if o == obj:
                self.callBacksForUpdate.pop(i)
                return True
        
    def getVals(self):
        return [ self.x, self.y, self.z ]
    
    def setOffset(self,offsets):
        self.xOff, self.yOff, self.zOff = offsets
    
    def setVal(self, val):
        #print("%s got setValue"%self.type)
        timeNowInMillis = self.th.getTimestamp(True)
        
        
        self.uSCount+= 1
        if (timeNowInMillis - self.uSTLast ) > (self.uSEvery*1000000):
            self.uSTLast = timeNowInMillis
            print("UPS    [",self.type,'] ',round(self.uSCount/(self.uSEvery),1))
            self.uSCount = 0
        
        
        self.iter+=1
        if self.type == "orientation" and len(self.axis['y']) > 50:

            if self.guiGraphDbHeelPitch:
                da = []
                vL = None
                for i,v in enumerate(self.axis['y'][-400:]):
                    if vL == None:
                        vL = v
                    vL = vL*0.95 + v*0.05
                    da.append( v )
                fftPlotData(self.gui.pFFTHeel, np.array(da))
                
                da = []
                vL = None
                for i,v in enumerate(self.axis['x'][-400:]):
                    if vL == None:
                        vL = v
                    vL = vL*0.95 + v*0.05
                    da.append( v )
                fftPlotData(self.gui.pFFTPitch, np.array(da))
                
                da = []
                vL = None
                for i,v in enumerate(self.gui.sen.accel.axis['z'][-400:]):
                    if vL == None:
                        vL = v
                    vL = vL*0.95 + v*0.05
                    da.append( v )
                fftPlotData(self.gui.pFFTUD, np.array(da))
                
        
        
        val[0]-= self.xOff
        val[1]-= self.yOff
        val[2]-= self.zOff
        
        if self.type == "spacorientation":            
            # x - on side
            # y - upright
            # z - flat
            # orientation x - Heel    y - Pitch
            
            if self.gui.sen.upAxis == "z":
                self.gui.sen.orientation.setVal([self.z, self.y, self.x])
            elif self.gui.sen.upAxis == "x":
                self.gui.sen.orientation.setVal([-self.y, 90.00+self.z, self.x])            
            elif self.gui.sen.upAxis == "y":
                accel = self.gui.sen.accel.getVals()
                a = [accel[0], accel[1], accel[2]]
                h = math.degrees( math.atan2( a[1], a[0] )-math.pi*0.5 )
                p = math.degrees( math.pi*0.5-math.atan2( a[1], a[2] ) )
                self.gui.sen.orientation.setVal([h, p, 0.0])
                
            
        
        #val[0] = self.x*0.3 + val[0]*0.6
        #val[1] = self.y*0.3 + val[1]*0.6
        #val[2] = self.z*0.3 + val[2]*0.6
        
        
        if self.type == "gyro":
            v = transform90axis(self.gui.sen.upAxis, val)
            v[2] = -v[2]
            self.gui.sen.gyroFlipt.setVal(v)
            
        
        self.x = float(val[0])
        self.y = float(val[1])
        self.z = float(val[2])
        
        self.history.append([self.x,self.y,self.z])
        self.axis['x'].append( self.x )
        self.axis['y'].append( self.y )
        self.axis['z'].append( self.z )
        if len(self.history)>self.historyMem:
            self.history.pop(0)
            self.axis['x'].pop(0)
            self.axis['y'].pop(0)
            self.axis['z'].pop(0)


        if self.type == "accel":
            if self.x >= self.y and self.x >= self.z:
                self.gui.sen.upAxis = "x"
            elif self.z >= self.x and self.z >= self.y:
                self.gui.sen.upAxis = "z"
            else:
                self.gui.sen.upAxis = "y"
        
            self.gui.rl.ids.senLUpAxis.text = self.gui.sen.upAxisNames[self.gui.sen.upAxis ]
            
        if self.type == "gyroFlipt":
            if len(self.history)> 25:
                
                sufix = sum(self.axis['y'][-10:-1])/9.0
                aavg = sum(self.axis['y'][-24:])/len(self.axis['y'][-24:])
                if sufix > aavg:
                    self.gui.rl.ids.lModSimGyroHeel.text = "S"
                else:
                    self.gui.rl.ids.lModSimGyroHeel.text = "P"
                
                sufix = sum(self.axis['x'][-10:-1])/9.0
                aavg = sum(self.axis['x'][-24:])/len(self.axis['x'][-24:])
                if sufix > aavg:
                    self.gui.rl.ids.lModSimGyroPitch.text = "A"
                else:
                    self.gui.rl.ids.lModSimGyroPitch.text = "B"
                    
                sufix = sum(self.axis['z'][-10:-1])/9.0
                if sufix > 0.0:
                    self.gui.rl.ids.lModSimGyroYaw.text = "S"
                else:
                    self.gui.rl.ids.lModSimGyroYaw.text = "P"
                
                if self.guiGraphGyro:
                    self.gui.pgx.points = self.gui.sen.sinHistoryArrayToGraph(
                        self.axis['x'][-90:], 30
                        )
                    self.gui.pgy.points = self.gui.sen.sinHistoryArrayToGraph(
                        self.axis['y'][-90:], 30
                        )
                    self.gui.pgz.points = self.gui.sen.sinHistoryArrayToGraph(
                        self.axis['z'][-90:], 90
                        )
                    
            t = self.lastTimeIter-timeNowInMillis
            m = math.degrees(self.axis['z'][-1])
            mov = m*(t/1000000.0)
            try:
                hdg = self.gui.sen.comCal.hdg%360.00
                if hdg > 180.00:
                    hdg = hdg - 360.0
                z = self.gui.sen.comCalAccelGyro.z
                
                if (hdg - z) < -180.0:
                    hdg+=360.00
                elif (hdg - z) > 180.0:
                    hdg-=360.00
                vts = (z-mov)*0.95+(hdg*0.05)
                #print("accelGyro ",round(mov,2)," vts ",round(vts,2)," hdg ",round(hdg,2))
                self.gui.sen.comCalAccelGyro.setVal([
                    0.0,0.0,
                    vts
                    ])
                #print("gyro to hdg ",self.axis['z'][-1],"time",t,"mov",mov)
            except:
                print("corecting hdg by gyro error")    
                #print( "- %s %s %s \n"%(self.axis['x'][-1], self.axis['y'][-1], self.axis['z'][-1] ))
                
            #self.gui.sen.wHeelBoat.update(self.axis['y'][-1])
                
        # gui update
        updateGui = False
        if (timeNowInMillis - self.guiUTLast ) > (self.guiUpdateEvery*1000000):
            updateGui = True
            self.guiUTLast = timeNowInMillis
            
        
        if updateGui and len(self.guiObjs) == 3 and self.gui.rl.current == "Sensors":
            for i,o in enumerate(self.guiObjs):
                o.text = "%s"%round(val[i],5)
        
        if self.type == "accel":
            if self.guiArrowsAccel:
                howFarBackAccel = 30
                x_ = self.gui.sen.sinWaveAnalitic(self.axis['x'][-howFarBackAccel:])
                y_ = self.gui.sen.sinWaveAnalitic(self.axis['y'][-howFarBackAccel:])
                z_ = self.gui.sen.sinWaveAnalitic(self.axis['z'][-howFarBackAccel:])
                self.gui.senBoat.setArrowsAccel([ x_, y_, z_])

        if self.type == "orientation":
            pitch = round( self.y, 3 )
            heel = round(self.x, 3)
            self.history[-1] = [pitch,heel,0]
            self.axis['x'][-1] = pitch
            self.axis['y'][-1] = heel
            if updateGui:
                self.gui.rl.ids.senLPitch.text = str( pitch )
                self.gui.rl.ids.senLHeel.text = str( heel )
            try:
                self.gui.senBoat.setHeel(self.x)
                self.gui.senBoat.setPitch(self.y)
            except:
                pass
            
            #graph
            if self.guiGraphHeelPitch:
                self.gui.pPitch.points = self.gui.sen.sinHistoryArrayToGraph(
                    self.axis['x'][-90:], 30 
                    )
                self.gui.pHeel.points = self.gui.sen.sinHistoryArrayToGraph(
                    self.axis['y'][-90:],30
                    )

            #print(fgh)
            
            if len(self.history)> 25:
                if updateGui:
                    if sum(self.axis['x'][-10:-1])/9.0 > sum(self.axis['x'])/len(self.axis['x']):
                        self.gui.rl.ids.lModSimHeelSlope.text = "S"
                    else:
                        self.gui.rl.ids.lModSimHeelSlope.text = "P"
            

        self.updateTime = timeNowInMillis
                        
                             
        if self.type == "comCal":
            v = transform90axis(self.gui.sen.upAxis, val)
            self.hdg = Vector(v[0], v[1]).angle((0,1))
            if self.hdg < 0.0:
                self.hdg = 180.0 + (180.0 + self.hdg)

            self.axis['x'][-1] = self.hdg
            
            #self.gui.senBoat.setRoseta( self.hdg )
            #print("TOFIX52352")
            
            
            if updateGui:
                self.gui.rl.ids.senLComDir.text = str(round(self.hdg,1))
            
            if self.guiGraphCompas:
                self.gui.pc.points = self.gui.sen.sinHistoryArrayToGraph(
                    self.axis['x'][-90:])

            self.avgHdg = (self.avgHdg*self.avgFraction)+(self.hdg*(1.0-self.avgFraction))
            
            
        # nmea    
        if self.type == "orientation":
            pitch = round( self.y, 2 )
            heel = round( self.x, 2 )
            nmea = "$YKXDR,A,%s,,PTCH,A,%s,,ROLL,"%(-pitch, heel)
            self.gui.sf.sendToAll( nmea )
            
        elif self.type == "comCalAccelGyro":
            nmea = "$YKHDG,%s,W,0,E" % round(self.z,1)
            self.gui.sf.sendToAll(nmea)
            
        elif self.type == 'comCal':
            ms = self.updateTime        
            if ( self.gui.sen.comCalAccelGyro.lastTimeIter + 5000000.0 ) < ms:
                nmea = "$YKHDG,%s,W,0,E" % round(self.hdg,1)
                self.gui.sf.sendToAll(nmea)
            
        
        
        if self.type == 'comCal':
            valToPropagate = [self.hdg,self.avgHdg]
        elif self.type == 'orientation':
            valToPropagate = [val[0],val[1],val[2],pitch,heel]
        else:
            valToPropagate = val
        
        
        if self.lastVal == None or self.lastVal != valToPropagate:
            self.propagateVal = True
            #print("+")
        else:
            self.propagateVal = False
            #print(".")
        
        
        if self.propagateVal:
            # callbacks
            for o in self.callBacksForUpdate:
                o.update(self.type, valToPropagate)
            
            self.lastVal = valToPropagate
            
            # json            
            jMsg = str({
                "type": self.type,
                "data": val
                })
            self.gui.sf.sendToAll( jMsg )
            
            
            
        self.lastTimeIter = timeNowInMillis

class odometer:
    
    def __init__(self, gui, type_):
        self.th = TimeHelper()
        self.fa = FileActions()
        self.callBacksForUpdate = []
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
        
    def addCallBack(self, obj):
        print("addCallBack to [",self.title,"] obj ",obj)
        self.callBacksForUpdate.append( obj ) 
    
    def removeCallBack(self, obj):
        for i,o in enumerate(self.callBacksForUpdate):
            if o == obj:
                self.callBacksForUpdate.pop(i)
                return True
        
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
                
                if self.gui.isReady:
                    # callbacks
                    for o in self.callBacksForUpdate:
                        o.update(self.type, self.data) 
                
        
            self.iter+=1
    
        
        
class sensors:
    
    ready = False
    running = False
    platform = ''
    context = None
    sensorsCount = 3
    # x - on side
    # y - upright
    # z - flat
    upAxisNames = {
        'x' : 'on side',
        'y' : 'portret',
        'z' : 'flat'
        }
    upAxis = "z"
    
    def __init__(self,gui):
        self.gui = gui
        self.boat = {}

        self.permissonsStatus = False
        self.sensorsList = []

        self.th = TimeHelper()
        self.fa = FileActions()
        
        self.playingFromFile = False
        self.FromFile = ""
        self.FromFileData = {}
        self.replayFps = 60
        
        self.sPlaFroFil = Spinner(
            values = [],#list(self.filesToPlay),
            text = "play from file:",
            size_hint = (None,None),
            size = (self.gui.btH*4,self.gui.btH)        
            )
        self.sPlaFroFil.bind(text=self.on_PlaFroFile)
        bl = self.gui.rl.ids.bl_sensorsPlaFroFil
        bl.add_widget(self.sPlaFroFil)
        
        print("new Spinner with updated list DONE")
        #self.wHeelBoat = waveCicleHolder(gui,'boat_heel')
        
        
        self.calibrateStep = 0
        self.recordToFile = "ready"
        self.toFileList = []
        
        #self.mic.runIt()
    def makeSensors(self):
        gui = self.gui
        self.mic = micData(gui)
        
        self.device = deviceSensors(gui)
        self.sensorsList.append( self.device )
        
        
        self.gpsD = gpsData(gui, {
            'lat': self.gui.rl.ids.senLGpsLat,
            'lon': self.gui.rl.ids.senLGpsLon,
            'sog': self.gui.rl.ids.senLGpsSog,
            'lSRacSog': self.gui.rl.ids.lSRacSog,
            'lSRacSogMax': self.gui.rl.ids.lSRacSogMax,
            'lSRacSogAvg': self.gui.rl.ids.lSRacSogAvg,
            'cog': self.gui.rl.ids.senLGpsCog,
            'accur': self.gui.rl.ids.senLGpsAcc
            })
        self.sensorsList.append( self.gpsD )
        
        self.odometer = odometer( gui, 'odometer')
        self.sensorsList.append( self.odometer )
        self.gpsD.addCallBack(self.odometer)
        
        self.gyro = xyzData(gui, "gyro", [
            self.gui.rl.ids.senLGyrX,
            self.gui.rl.ids.senLGyrY,
            self.gui.rl.ids.senLGyrZ
            ])
        self.sensorsList.append( self.gyro )
        
        self.gyroFlipt = xyzData(gui, "gyroFlipt",[
            self.gui.rl.ids.senLGyrCalX,
            self.gui.rl.ids.senLGyrCalY,
            self.gui.rl.ids.senLGyrCalZ
            ])
        self.sensorsList.append( self.gyroFlipt )
        
        self.accel = xyzData(gui, "accel", [
            self.gui.rl.ids.senLAccX,
            self.gui.rl.ids.senLAccY,
            self.gui.rl.ids.senLAccZ
            ])
        self.sensorsList.append( self.accel )
        
        self.spacialOrientation = xyzData(gui, "spacorientation", [
            self.gui.rl.ids.senLSpaOriX,
            self.gui.rl.ids.senLSpaOriY,
            self.gui.rl.ids.senLSpaOriZ
            ])
        self.sensorsList.append( self.spacialOrientation )
        
        self.accelFlipt = xyzData(gui, "accelFlipt")
        self.sensorsList.append( self.accelFlipt )
        
        self.orientation = xyzData(gui, "orientation")
        self.sensorsList.append( self.orientation )
        
        self.comCal = xyzData(gui, "comCal", [
            self.gui.rl.ids.senLComCalX,
            self.gui.rl.ids.senLComCalY,
            self.gui.rl.ids.senLComCalZ
            ])
        self.sensorsList.append( self.comCal )
        
        self.comCalAccelGyro = xyzData(gui, "comCalAccelGyro")
        self.sensorsList.append( self.comCalAccelGyro )
    
    
    def askForPermissions(self):
        if kivy.platform == 'android':
            #self.request_android_permissions2()
            print("trying ... gps ...")
            try:
                gps.configure( 
                    on_location=self.on_gps_location,
                    on_status=self.on_gps_status
                    )
                self.request_android_permissions1()
                print("    gps OK")
            except:
                print("no gps :(")
                
                
            print("trying ... accelerometers ...")
            try:
                accelerometer.enable()
                print("    accelerometers OK")
            except:
                print("no accelerometers")
                
            print("trying ... spacial orientation ...")
            try:
                spatialorientation.enable_listener()
                print("    spacial orientation OK")
            except:
                print("no spacial orientation")
                
            print("trying ... gyroscope ...")
            try:
                gyroscope.enable()
                print("    gyroscope OK")
            except:
                print("no accelerometers")
        
            print("trying ... compass calibrated...")
            try:
                compass.enable()
                print("    compass calibrated OK")
            except:
                print("no compass calibrated")
                
        
        
    
    def sinHistoryArrayToGraph(self, a=[],avgSize=90):
        if len(a)>0:
            points = []
            pOld = 0.0
            try:
                m = min (a[-avgSize:])
                pdif = 1.0/(max(a[-avgSize:])-m)
                for i,y in enumerate(a):
                    pOld = (y + pOld )/2.0
                    points.append([i,(pOld-m)*pdif])
                return points
            except:
                return [[0,0]]
        else:
            return [[0,0]]
    
    def sinWaveAnalitic(self,buf,samplingSize_=30):
        blen = len(buf)
        bavg = sum(buf)/blen
        bmin = min(buf)
        bmax = max(buf)
        
        bufforMinimumAnalitic = 30
        samplingSize = samplingSize_
        
        upSlopesC = 0
        downSlopesC = 0
        slop = 0
        
        if blen > bufforMinimumAnalitic:
            lastSlopeDir = 0
            for i in range(30,blen,1):
                sufix = sum(buf[ i-samplingSize:i ])/(samplingSize-1)
                slop = 0
                if sufix > bavg:
                    slop = 1
                else:
                    slop = -1
                    
                if lastSlopeDir != slop:
                    
                    if slop > 0:
                        upSlopesC+=1
                    else:
                        downSlopesC+=1
                    
                    lastSlopeDir = slop
        
        return {
            'last': buf[-1],
            'filtert': (sum(buf[-4:])/3.0),
            'ups': upSlopesC,
            'downs': downSlopesC,
            'len': blen,
            'avg': bavg,
            'min': bmin,
            'max': bmax,
            'current': slop
            }
            
    
    def calibrateIter(self):
        print("calibrate iter [%s]"%self.calibrateStep)
        step = self.calibrateStep
        calLastFor = self.th.getTimestamp() - self.calibationTimeStart
        
        if calLastFor > (60*5): # 5 min
            self.calibrateStep = 0
            self.queryMessage.dismiss()
        
        if step == 1:
            bufLen = len(self.calBuf)
            self.calCompas.append(self.comCal.hdg)
            comRes = self.sinWaveAnalitic(self.calCompas)
            print("    calibrate gyro [ ups %s downs %s ]" % ( comRes['ups'], comRes['downs'] ) )
            gf = self.gyroFlipt.getVals()
            self.calBuf['x'].append(gf[0])
            self.calBuf['y'].append(gf[1])
            self.calBuf['z'].append(gf[2])
            self.calHeel.append(self.orientation.x)
            self.calPitch.append(self.orientation.y)
            
            print("z axis:")
            print( self.sinWaveAnalitic(self.calBuf['z']) )
            print("compas axis:")
            print( comRes )

            whatInOn = str("calibrating in progress ... [%s/2][%s/2] %s"%(comRes['ups'],comRes['downs'],round(self.comCal.hdg,1)))
            
            self.queryMessage.ids.bt_cancel.text = str(
                self.th.getNiceHowMuchTimeItsTaking( calLastFor ) 
                )
            
            #self.gui.rl.ids.bModSimCal.text = whatInOn
            self.queryMessage.title = whatInOn
            
            waitUpTo = 2
            if comRes['ups'] == waitUpTo and comRes['downs'] == waitUpTo:
                step = 2
            
        if step == 2:
            avgx = sum(self.calBuf['x'])/len(self.calBuf['x'])
            avgy = sum(self.calBuf['y'])/len(self.calBuf['y'])
            avgz = sum(self.calBuf['z'])/len(self.calBuf['z'])
            
            tSpand = float(self.th.getTimestamp() - self.calTStart)
            heelHz = (self.sinWaveAnalitic(self.calBuf['x'],4)['downs']/tSpand)
            pitchHz = (self.sinWaveAnalitic(self.calBuf['y'],4)['downs']/tSpand)
            self.gui.rl.ids.lModSimGyroHeelHz.text = str(round(heelHz,2))
            self.gui.rl.ids.lModSimGyroPitchHz.text = str(round(pitchHz,2))
            
            print("    avg ",avgx,avgy, avgz)
            self.gyroFlipt.setOffset([avgx,avgy,avgz])
            
            self.orientation.setOffset([
                sum(self.calHeel)/len(self.calHeel),
                sum(self.calPitch)/len(self.calPitch),
                0.0
                ])
            
            self.calBuf = {'x':[], 'y':[],'z':[]}
            self.calCompas = []
            self.calibrateStep = 0 
            self.gui.rl.ids.bModSimCal.text = str("Calibrated at %s"%self.th.getNiceDateFromTimestamp())
            self.queryMessage.dismiss()
        
            dataToFila = {
                "gyroFlipt.offset": [avgx,avgy,avgz],
                "orientation.offset": [
                    sum(self.calHeel)/len(self.calHeel),
                    sum(self.calPitch)/len(self.calPitch),
                    0.0
                    ],
                "heelHz": heelHz,
                "pitchHz": pitchHz
                }
            
            DataSR_save(
                dataToFila, 
                self.fa.join(self.gui.homeDirPath,"ykpilot_calibration.conf")
                )
            print("config file on drive. ykpilot_calibration.conf")
            
        
    def calibrate(self):
        print("calibrate")
        self.calTStart = self.th.getTimestamp()
        self.calCompas = []
        self.calHeel = []
        self.calPitch = []
        self.calBuf = {'x':[], 'y':[],'z':[]}
        self.calibrateStep = 1
        
        self.orientation.setOffset([0.0,0.0,0.0])
        self.gyroFlipt.setOffset([0.0,0.0,0.0])
        
        self.calibationTimeStart = self.th.getTimestamp()
        self.queryMessage = QueryPopup()
        self.queryMessage.setAction(
            "Calibrating ...", 
            "In the process of calibarion gyro, heel, pitch sensor...", 
            self.on_calibation_cancel, "Cancel calibration now!", 
            None, None
            )
        self.queryMessage.run()
    
    def on_calibation_cancel(self):
        print("on_calibation_cancel")
        self.calibrateStep = 0
        
    
    def buidPlayer(self, toReturn ):
        print("buidPlayer ---------------------------------------------------")
        
        print("update list of files...")
        self.filesToPlay = self.fa.getFileList( 
            self.gui.workingFolderAdress,
            filter=".rec" 
            )
        print("-> list is ",self.filesToPlay)
        self.sPlaFroFil.values = list(self.filesToPlay)
        print("    done")
        
        bl = BoxLayout(
            orientation="vertical",
            )
        bl.add_widget(toReturn)
        self.playerBL = BoxLayout(
            orientation = "horizontal",
            size_hint = (self.gui.btH, None),
            height = self.gui.btH
            ) 
        self.playerBt = Button(
            text=">",
            size_hint = (None, None),
            size = (self.gui.btH, self.gui.btH),
            on_release=self.on_PlayFromFile_play
            )
        self.playerBL.add_widget(self.playerBt)
        self.playerSeek = Slider(
            min = 0.0,
            max = 1.0,
            value = 0.0,
            size_hint = ( None, None),
            size = (self.gui.btH*2, self.gui.btH)
            )
        self.gui.rl.bind(size=self.playerUpdateSize)
        self.playerBL.add_widget(self.playerSeek)
        self.playerTimer = Label(
            text="00:00:00",
            size_hint = (None, None),
            size = (self.gui.btH*4.1, self.gui.btH)
            )
        self.playerBL.add_widget(self.playerTimer)
        bl.add_widget(self.playerBL)
        
        #self.playerBL.height = 0.0
        #self.playerBL.visible = False
        self.playerHide()
        
        if self.gui.platform == 'pc':
            self.on_PlaFroFile(None, "ykpilot_record_2020_05_16_17_30_58.rec")
        
        return bl
        
        
    
    def playerShow(self):
        self.gui.hide_widget( self.playerBL, False )
            
    def playerHide(self):
        self.gui.hide_widget( self.playerBL )
        
        
    def playerUpdateSize(self, *args):
        self.playerSeek.width = self.gui.rl.width - (self.gui.btH*4.2)
        #self.playerTimer.pos = self.playerSeek.pos
        
    def on_PlaFroFile(self,obj,text):
        print("on_PlaFroFile [",text,"]")
        self.playerShow()
        file = "%s%s" % (
            self.gui.workingFolderAdress,
            text
            )
        print("loading file [",file,"]")
        self.FromFileData = DataSR_restore(file)
        print("    element in file",len(self.FromFileData))
        d = self.FromFileData
        tStart = d[0]['timeStamp']
        tEnd = d[-1]['timeStamp']
        self.playerTimer.text = self.th.getNiceHowMuchTimeItsTaking( tEnd-tStart )
        self.playerSeek.max = tEnd-tStart
        self.playerSeek.value = 0.0
        self.replayTStart = tStart
        self.replayTCurrent = 0.0
        self.replayTLast = 0.0
        

    
    def on_PlayFromFile_play(self,obj):
        print("on_PlayFromFile_play")
        if self.playingFromFile == False:
            print("pause")
            self.playingFromFile = True
            self.playerBt.text = "||"
            self.playerIterClock = Clock.schedule_interval(self.playerIter, 1.0/float(self.replayFps))
        else:
            print("play")
            self.playingFromFile = False
            self.playerBt.text = ">"
            Clock.unschedule( self.playerIterClock )
            
    
    def playerIter(self, a):
        try:
            aobeo = self.replayTCurrent
        except:
            print("EE - player Iter but no file to play :(")
            print("I will try to stop playng ?...")
            self.on_PlayFromFile_play(None)
            return 0
        
        self.replayTCurrent+= 1.0/float(self.replayFps)
        self.playerSeek.value = self.replayTCurrent
        
        #print("player", self.replayTCurrent)
        for e in self.FromFileData:
            tStart = self.replayTStart+self.replayTLast
            tEnd = self.replayTStart+self.replayTCurrent
            if e['timeStamp'] > tStart and e['timeStamp'] <= tEnd:
                #print("gps", e['gps'][0:2])
                
                try:
                    self.gui.sen.gpsD.update({
                        'lat': e['gps'][0],
                        'lon': e['gps'][1],
                        'bearing': e['gps'][2],
                        'speed': e['gps'][3],
                        'accuracy': 0.0                    
                        })
                except:
                    pass
                
                self.gui.sen.gyro.setVal( e['gyro'] )
                self.gui.sen.accel.setVal( e['accel'] )
                self.gui.sen.comCal.setVal( e['comCal'] )
                self.gui.sen.spacialOrientation.setVal( e['space'] )
                
        self.replayTLast = self.replayTCurrent    
        
        if self.replayTLast > (tEnd):
            self.on_PlayFromFile_play(None)    
    
    def on_recordToFile(self):
        #print("on_recordToFile ",self.recordToFile)
        if self.recordToFile == "active":
            self.recordToFile = "ready"
            if len(self.toFileList)>0:
                fileName = "%srecord_%s.rec"% (
                    self.gui.workingFolderAdress,
                    self.th.getNiceFileNameFromTimestamp() 
                    )
                DataSR_save(self.toFileList, fileName)
                print("writing lines (%s) to file %s"%(len(self.toFileList),fileName))
                self.toFileList = []
            self.gui.rl.ids.b_sensorsRecToFil.text = "Record to file"    
        else:
            self.recordToFile = "active"
            self.gui.rl.ids.b_sensorsRecToFil.text = "recording ..."    

    @mainthread
    def on_gps_location(self, **kwargs):
        #print("gps raw(%s)"%(kwargs))
        try:
            self.gpsD.update(kwargs)
        except:
            pass
    
    @mainthread
    def on_gps_status(self, stype, status):
        #print("gps status",status)
        try:
            if status == 'gps: available':
                self.gpsD.status = 'ready'
            else:
                self.gpsD.status = 'busy'
            print("gps status stype(%s) status(%s)"%(stype,status))
        except:
            pass
        
        
    def request_android_permissions1(self):
        print("request permissions ")
        from android.permissions import request_permissions, Permission

        def callback( permissions, results):
            if all([res for res in results]):
                print("permissions OK!")
                self.permissonsStatus = True
            else:
                print("permissions no bueno :(")
                print("TODO - if permission are not fine do something!")
                print("results",results)
                self.permissonsStatus = False
                
        request_permissions([Permission.ACCESS_COARSE_LOCATION,
                             Permission.ACCESS_FINE_LOCATION,
                             #Permission.WRITE_SETTINGS,
                             Permission.READ_EXTERNAL_STORAGE,
                             Permission.WRITE_EXTERNAL_STORAGE,
                             Permission.WAKE_LOCK        
                             ], callback)
    
    
    
    def gps_start(self, mt, md):
        print("gps_start")
        if self.gpsD.androidServiceStatus:
            print("skipp ! it's running allrady")
        else:
            self.gpsD.androidServiceStatus = True
            gps.start(mt,md)
        
    def gps_stop(self):
        print("gps_stop")
        if self.gpsD.androidServiceStatus:
            self.gpsD.androidServiceStatus = False
            gps.stop()
        else:
            print("skipp ! it's not running")
    
    def update(self,fromWho, vals):
        #print("sensors.update fromWho[{}]".format(fromWho))
        self.boat = {
            'cogError': 0.0,
            'hdg': self.comCal.hdg,
            'cog': self.gpsD.cog,
            'sog': self.gpsD.sog,
            'lat': self.gpsD.lat,
            'lon': self.gpsD.lon,
            'gRot': self.gyroFlipt.axis['z'][-1] if len(self.gyroFlipt.axis['z'])>0 else 0.0
            }
    
    def interval(self,u):
        debPrints = False
        if debPrints: print("sensors.interval...")
        
        self.device.iter()
        
        
        try:
            accelVal = accelerometer.acceleration[:3]
            if debPrints: print("accelVal %s    %s    %s"%(accelVal[0],accelVal[1],accelVal[2]))
            if not accelVal == (None,None,None):
                self.accel.setVal(list(accelVal))
        except Exception:
            if debPrints: print("accelerometer nooo :(")    
            if debPrints: print( traceback.format_exc() )
        
        try:
            space = spatialorientation.orientation
            for i in range(0,3,1):
                space[i] = math.degrees(space[i])
            if debPrints: print("spatialorientation %s    %s    %s"%(space[0],space[1],space[2]))
            if not space == (None,None,None):
                self.spacialOrientation.setVal(list(space))
        except Exception:
            if debPrints: print("spatialorientation nooo :(")    
            if debPrints: print( traceback.format_exc() )
        
        try:
            gyroVal = gyroscope.rotation
            if debPrints: print("gyroVal")
            #print(gyroVal)
            if gyroVal[:3] != (None, None, None):
                self.gyro.setVal(list(gyroVal[:3]))
        except Exception:
            if debPrints: print("gyroscope nooo :(")
            if debPrints: print( traceback.format_exc() )
            
            
        try:
            compVal = compass.orientation
            if debPrints: print("compVal")
            #print(compVal)
            if compVal[:3] != (None, None, None):
                self.comCal.setVal(list(compVal[:3]))
        except Exception:
            if debPrints: print("compass calibrated nooo :(")
            if debPrints: print( traceback.format_exc() )
        
        if self.calibrateStep != 0:
            self.calibrateIter()

        if self.recordToFile == "active":
            line = {
                "gps": self.gpsD.getVals(),
                "timeStamp": self.th.getTimestamp(True),
                "accel": self.accel.getVals(),
                "gyro": self.gyro.getVals(),
                "comCal": self.comCal.getVals(),
                "space": self.spacialOrientation.getVals()
                }
            self.toFileList.append(line)

    def run(self):
        #pass
        #self.mic.runIt()
        self.device.initSensors()
        iterTime = (1.0/15.0) if self.gui.platform == 'android' else 1.0
        self.intervalEvent = Clock.schedule_interval( self.interval, iterTime )
        
        