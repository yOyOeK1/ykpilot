from TimeHelper import TimeHelper
from pygeodesy.ellipsoidalVincenty import LatLon
from pygeodesy import dms
from senProto import senProto

class gpsData(senProto):
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
    llOld = [None, None]
    
    def __init__(self,gui,debGuiObjts={},icon=None):
        
        super(gpsData, self).__init__()
        
        self.gui = gui
        self.guiObjs = debGuiObjts
        self.th = TimeHelper()
        self.title = "gps"
        self.type = self.title
        self.icon = icon
    
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
            #self.gui.sf.sendToAll(msg)
            self.broadcastByTCPNmea(self.gui, msg)
            
            self.broadcastByMqtt(self.gui, "sensors/gps/lat", latRaw)
            self.broadcastByMqtt(self.gui, "sensors/gps/lon", lonRaw)
            self.broadcastByMqtt(self.gui, "sensors/gps/cog", self.gpscog)
            self.broadcastByMqtt(self.gui, "sensors/gps/sog", self.gpssog)
            self.broadcastByMqtt(self.gui, "sensors/gps/accuracy", self.accur)
            
            
            if self.gui.rl.current == "Race":
                self.guiObjs['lSRacSog'].text = "%s" % round(self.sog,1)
                self.guiObjs['lSRacSogMax'].text = "max: %s" % round(self.maxSog,2)
                self.guiObjs['lSRacSogAvg'].text = "avg: %s" % round(self.avgSog,2)
            
            if self.gui.isReady:
                # callbacks
                #for o in self.callBacksForUpdate:
                #    o.update('gps', val)
                self.broadcastCallBack(self.gui, 'gps', val)
                
                # json
                jMsg = str({
                    "type": "gps",
                    "data": val
                    })
                #self.gui.sf.sendToAll( jMsg )
                self.broadcastByTCPJSon( self.gui, jMsg )


