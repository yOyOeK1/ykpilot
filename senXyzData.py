
from kivy.vector import Vector
from TimeHelper import TimeHelper
from FileActions import FileActions
from DataSaveRestore import DataSR_restore
from fftAnalisy import fftPlotData
import numpy as np
import math
from senTransform import transform90axis
from MyCalculate import SPoint
from imuVr import imuVr

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
        
        if self.type == "comCal":
            self.ccAngStart = None
            self.ccAng = []
            self.ccAngHis = 100
            self.ivr = imuVr(self)

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
                
                if self.gui.rl.current == "Model Screen":
                    self.gui.rl.ids.lModSimGyroHeelHz.text = str(round(listConfig['heelHz'],2))
                    self.gui.rl.ids.lModSimGyroPitchHz.text = str(round(listConfig['pitchHz'],2))
            except:
                pass


        else:
            print(" no config fille")
    
    def getTitle(self):
        return self.type
    
    def getValuesOptions(self):
        if self.type in [ 'gyro', 'gyroFlipt', 'accel', 'gravity', 'accelFlipt', 'spacorientation' ]:
            return { 'list' :
                ['x', 'y', 'z']
                }
        elif self.type in [ 'comCalAccelGyro']:
            return { 'list':
                ['hdg',  'avgHdg']
                }
        elif self.type in [ 'comCal' ]:
            return { 'list':
                [
                    'hdg',  'avgHdg',
                    'force on x', 'force on y', 'force on z', 'force total',
                    'angle strat x', 'angle start y', 'angle start z', 'start force',
                    'angle x', 'angle y', 'angle z', 'force now'
                 ]
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
        
            if self.gui.rl.current == "Sensors":
                self.gui.rl.ids.senLUpAxis.text = self.gui.sen.upAxisNames[self.gui.sen.upAxis ]
            
        if self.type == "gyroFlipt":
            if len(self.history)> 25:
                if self.gui.rl.current == "Model Screen":
                    updateGuiGF = True
                else:
                    updateGuiGF = False                
                sufix = sum(self.axis['y'][-10:-1])/9.0
                aavg = sum(self.axis['y'][-24:])/len(self.axis['y'][-24:])

                sufix = sum(self.axis['x'][-10:-1])/9.0
                aavg = sum(self.axis['x'][-24:])/len(self.axis['x'][-24:])
                sufix = sum(self.axis['z'][-10:-1])/9.0
                
                if updateGuiGF:
                    if sufix > aavg:
                        self.gui.rl.ids.lModSimGyroHeel.text = "S"
                    else:
                        self.gui.rl.ids.lModSimGyroHeel.text = "P"
                
                    if sufix > aavg:
                        self.gui.rl.ids.lModSimGyroPitch.text = "A"
                    else:
                        self.gui.rl.ids.lModSimGyroPitch.text = "B"
                    
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
            
            
            p = SPoint(val)
            ccAng = self.ivr.getAnglesAndLength(p)
            self.ccAng.append(ccAng)
            if len(self.ccAng)>self.ccAngHis:
                self.ccAng.pop(0)
                
            if self.ccAngStart == None:
                self.ccAngStart = ccAng
                
            
            
            
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
            
            cas  = self.ccAngStart
            ca = self.ccAng[-1]
            
            valToPropagate = [
                self.hdg,self.avgHdg,
                val[0],val[1],val[2],"lengthTODO",
                cas[0],cas[1],cas[2],cas[3],
                ca[0], ca[1], ca[2], ca[3]
                ]
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
            #print("jMsg:",jMsg)
            self.gui.sf.sendToAll( jMsg )
            
            
            
        self.lastTimeIter = timeNowInMillis

