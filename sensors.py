
import kivy
import math
import ast
import json
import traceback
from kivy.clock import Clock, mainthread
from kivy.vector import Vector
from kivy.uix.spinner import Spinner
from kivy.properties import NumericProperty,ObjectProperty,StringProperty
from plyer import gps,gravity,accelerometer,compass
from plyer import gyroscope,spatialorientation

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
from senECPU import senECPU
from senSeatalk import senSeatalk
from senOdometer import odometer
from senMicData import micData
from senDeviceSensor import deviceSensors
from senGpsData import gpsData
from senXyzData import xyzData
from senDTH import senDTH
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.button import MDFlatButton




        
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
        
        '''
        menu_items = []
        for i in range(10):
            menu_items.append({'text':"abc%s"%i,'on_release':self.on_PlaFromFileMD})
        
        self.sPlaFroFilMD = MDDropdownMenu(
            items=menu_items,
            width_mult=4,
            )
        #bl.add_widget(self.sPlaFroFilMD)
        btt = MDFlatButton(
            text="press",
            on_release=self.on_PlaFromFileMDOpen
            )
        bl.add_widget(btt)
        self.sPlaFroFilMD.callback=self.on_PlaFromFileMD
        self.sPlaFroFilMD.caller = btt
        '''
        
        print("new Spinner with updated list DONE")
        #self.wHeelBoat = waveCicleHolder(gui,'boat_heel')
        
        
        self.calibrateStep = 0
        self.recordToFile = "ready"
        self.toFileList = []
        #self.mic.runIt()
        
        
    '''    
    def on_PlaFromFileMDOpen(self,a=0,b=0):
        self.sPlaFroFilMD.open()
    def on_PlaFromFileMD(self,a=0):
        print("on_PlaFromFileMD",a) 
    '''    
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
        
        self.gravity = xyzData(gui, "gravity" )
        self.sensorsList.append( self.gravity )
        
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
    
        self.nodeMcu = senECPU(gui, 'nodeMcu')
        self.sensorsList.append(self.nodeMcu)
        
        self.arduinoUno = senECPU(gui, 'arduinoUno')
        self.sensorsList.append(self.arduinoUno)
        
        self.seatalk = senSeatalk(gui,'seatalk')
        self.sensorsList.append(self.seatalk)
        
        self.senDTH = senDTH(gui, 'senDTH')
        self.sensorsList.append(self.senDTH)
    
    
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
                
            print("trying ... gravity ...")    
            try:
                gravity.enable()
                print("    gravity OK")
            except:
                print("no gravity")
                
                
                
            print("trying ... gyroscope ...")
            try:
                gyroscope.enable()
                print("    gyroscope OK")
            except:
                print("no gyroscope")
        
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
                try:
                    self.gui.sen.gravity.setVal( e['gravity'] )
                except:
                    print("EE - replay from file gravity missing..")
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
        debPrints = True
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
            gravityVal = gravity.gravity
            if debPrints: print("gravityVal ",gravityVal)
            if not gravityVal == (None,None,None):
                self.gravity.setVal(list(gravityVal))
        except Exception:
            if debPrints: print("gravity nooo :(")    
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
                "gravity": self.gravity.getVals(),
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
        
        