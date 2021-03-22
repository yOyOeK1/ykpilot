from pygeodesy.sphericalTrigonometry import LatLon, intersection
import aislib
import os
import kivy
from DataSaveRestore import DataSR_save, DataSR_restore
from FileActions import FileActions
from kivymd.uix.list import MDList, TwoLineListItem, ThreeLineListItem
from kivy.uix.scrollview import ScrollView
from kivy.lang.builder import Builder
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton,\
    MDRectangleFlatIconButton, MDIconButton
from kivy.properties import StringProperty
from kivy.clock import Clock
from _functools import partial
from plyer import camera
from kivymd.uix.boxlayout import MDBoxLayout
from gui import DLabel
from pygeodesy.utily import m2NM
from pygeodesy.dms import compassPoint


#from jnius import autoclass, cast
#from os.path import exists
#from android import activity, mActivity

'''
Intent = autoclass('android.content.Intent')
MediaStore = autoclass('android.provider.MediaStore')
Uri = autoclass('android.net.Uri')
Environment = autoclass('android.os.Environment')
'''

class trianPiont:
    def __init__(self, lat, lon, bearing, entryDate):
        self.LatLon = LatLon(lat,lon)
        self.bearing = float(bearing)
        self.entryDate = entryDate
        
    def getDict(self):
        print("trianPiont.getDict")
        return {
            'lat':self.LatLon.lat,
            'lon':self.LatLon.lon,
            'bearing':self.bearing,
            'entryDate':self.entryDate
            }

class trianItem:
    
    def __init__(self, name, points=[], status_='?', triaPont_ = None):
        self.name = name
        self.points = points
    
        self.trianPoint = None
        self.status = status_

        if len(self.points) == 2 and status_ == '?':
            self.solwLocation()
        else:
            self.status = status_
            if triaPont_:
                self.trianPoint = triaPont_
            else:
                if len(self.points) == 2:
                    self.solwLocation()
                
            
    def solwLocation(self):
        p0 = self.points[0]
        p1 = self.points[1]
        
        self.trianPoint = intersection(
            p0.LatLon, p0.bearing,
            p1.LatLon, p1.bearing,
            )
        
        self.status = 'DONE'
        print("intersection point [",self.name,"]",self.trianPoint)
        print("lat",self.trianPoint.lat,' lon',self.trianPoint.lon)

    def getDict(self):
        points = []
        for p in self.points:
            points.append(p.getDict())
        
        print("points",points)
        #print("trianPoint lat",self.trianPoint.lat,' lon',self.trianPoint.lon)
        
        tri = 'NaN'
        if self.trianPoint:
            tri = [self.trianPoint.lat,self.trianPoint.lon]
        
        return {
            'name':self.name,
            'status': self.status,
            'points': points,
            'tri': tri,
            }

class TrianAddDialog(ScrollView):
    def setGui(self,gui, runDialog):
        self.gui = gui
        self.runDialog = runDialog
    
    
class TrianRunAddDialog:
    def __init__(self,gui, trian, content, action):
        self.gui = gui
        self.trian = trian
        self.fa = trian.fa
        self.cleanDialogScreen()
        d = self.gui.rl.ids.bl_triDialog
        self.cont = content()
        if action == 'add':
            self.cont.ids.l_triTitle.text="Adding new triangulation point:"
        elif action == 'edit':
            self.cont.ids.l_triTitle.text="Triangulation point data:"
        d.add_widget(self.cont)
        self.cont.setGui(gui,self)
        self.phonoIndex = 0
        self.camOSD = DLabel(text="hdg: lat: lon:")
        
        if action == 'add':
            self.cont.ids.tf_triAddName.text = trian.getNextName()
            bl = MDBoxLayout(
                orientation = 'horizontal',
                size_hint= [1.0,None],
                size= [self.gui.windowSize[0], self.gui.btH*1.5],
                spacing = "10dp"
                )
            bl.add_widget(MDIconButton(
                #text= "Cancel",
                icon="cancel",
                on_release= self.on_triaAddCancel
                ))
            
            bl.add_widget(MDIconButton(
                #text= "Add",
                icon="content-save-edit",
                on_release= self.on_triaAddOk
                ))     
            self.cont.ids.l_triAddDialog.add_widget(bl)
            self.cont.ids.l_triAddDialog.add_widget(MDBoxLayout(
                size_hint= [1.0,None],
                size= [self.gui.windowSize[0], self.gui.btH*1.5],
                ))
            
        elif action == 'edit':
            d = self.cont.ids
            t = self.trian.triaItems[self.trian.editItem]
            d.tf_triAddName.text = str(t.name)
            if len(t.points) > 0:
                d.tf_triAddP0Bearing.text = str(t.points[0].bearing)
                d.tf_triAddP0Lat.text = str(t.points[0].LatLon.lat)
                d.tf_triAddP0Lon.text = str(t.points[0].LatLon.lon)
            if len(t.points) == 2:
                d.tf_triAddP1Bearing.text = str(t.points[1].bearing)
                d.tf_triAddP1Lat.text = str(t.points[1].LatLon.lat)
                d.tf_triAddP1Lon.text = str(t.points[1].LatLon.lon)
            
            bl = MDBoxLayout(
                orientation = 'horizontal',
                size_hint= [1.0,None],
                size= [self.gui.windowSize[0], self.gui.btH*1.5],
                spacing = "10dp"
                )
            bl.add_widget(MDIconButton(
                #text= "Delete",
                icon="delete",
                on_release= self.on_triaDelete
                ))
            bl.add_widget(MDIconButton(
                #text= "Cancel",
                icon="cancel",
                on_release= self.on_triaAddCancel
                ))
            
            bl.add_widget(MDIconButton(
                #text= "Save",
                icon="content-save-edit",
                on_release= self.on_triaSave
                ))     
            self.cont.ids.l_triAddDialog.add_widget(bl)
            self.cont.ids.l_triAddDialog.add_widget(MDBoxLayout(
                size_hint= [1.0,None],
                size= [self.gui.windowSize[0], self.gui.btH*1.5],
                ))
                
        
        self.gui.rl.current = 'TriangulateDialogs'
        print("make switch screen DONE")
     
     
    def on_useCamera(self, pointNo):
        print("on_useCamera",pointNo)
        self.gui.on_makeToast("building cammera view ....")
        Clock.schedule_once( partial(self.on_useCameraStep2,pointNo), 0.01)
        
    def on_useCameraStep2(self,pointNo,*a):
        print("on_useCameraStep2 No",pointNo)
        self.dialogPiontEdit = pointNo
        self.gui.stp.takePhoto(
            self.on_useCameraDone,
            self.camOSD
            )
        self.OSDClock = Clock.schedule_interval( self.OSDUpdate, 0.5 )

    def on_useCameraDone(self,status, fileName):
        print("on_useCameraDone",status)
        
        Clock.unschedule(self.OSDClock)
        
        if status == 'DONE':
            print("PICTURE OK !")
        else:
            return 0
        
        d = self.cont.ids
        a = self.dialogPiontEdit
        if a == 0:
            d.tf_triAddP0Bearing.text = str(self.trian.hdg)
            d.tf_triAddP0Lat.text = str(self.trian.lat)
            d.tf_triAddP0Lon.text = str(self.trian.lon)
        elif a == 1:
            d.tf_triAddP1Bearing.text = str(self.trian.hdg)
            d.tf_triAddP1Lat.text = str(self.trian.lat)
            d.tf_triAddP1Lon.text = str(self.trian.lon)
            
    def OSDUpdate(self,a=0,b=0):
        print("OSDUpdate")
        self.camOSD.text = 'hdg: {}    lat:{} lon:{}'.format(
            round(self.trian.hdg,1),
            round(self.trian.lat,7),
            round(self.trian.lon,7)
            )

        
    def cleanDialogScreen(self):
        d = self.gui.rl.ids.bl_triDialog
        d.clear_widgets()
    
    def on_triaDelete(self,a=0,b=0):
        print("on_triaDelete")
        self.trian.listClear()
        self.trian.triaItems.pop(self.trian.editItem)
        self.trian.saveTriaItems()
        self.trian.listBuild()
        self.gui.rl.current = 'Triangulate'
        
    
    def on_triaSave(self,a=0,b=0):
        print("on_triaSave")
        d = self.colectDataFromForm()
        self.trian.listClear()
        item = self.trian.addTriPoint(d,True)
        self.trian.triaItems[self.trian.editItem] = item
        self.trian.saveTriaItems()
        self.trian.listBuild()
        self.gui.rl.current = 'Triangulate'
        
    
    def on_triaAddCancel(self,a=0,b=0):
        self.gui.rl.current = 'Triangulate'
        
    def on_triaAddOk(self,a=0,b=0):
        print("on_triaAddOk")
        d = self.colectDataFromForm()
        self.trian.addTriPoint(d)
        self.trian.saveTriaItems()
        self.trian.listClear()
        self.trian.listBuild()
        self.gui.rl.current = 'Triangulate'
        
        
    def colectDataFromForm(self):
        i = self.cont.ids
        
        d = {
            'name': i.tf_triAddName.text,
            'status': '?',
            'points': []
            }
        
        if i.tf_triAddP0Lat.text:
            d['points'].append({
                'lat':i.tf_triAddP0Lat.text,
                'lon':i.tf_triAddP0Lon.text,
                'bearing':i.tf_triAddP0Bearing.text,
                'entryDate': 0
                })
        if i.tf_triAddP1Lat.text:
            d['points'].append({
                'lat':i.tf_triAddP1Lat.text,
                'lon':i.tf_triAddP1Lon.text,
                'bearing':i.tf_triAddP1Bearing.text,
                'entryDate': 0
                })
        return d

class Triangulacja:
    
    def __init__(self, gui):
        self.gui = gui
        self.fa = FileActions()
        self.triaItems = []
        self.fileStoragePath = self.fa.join(self.gui.homeDirPath, 'triangulation.data')#self.fa.join(self.gui.homeDirPath, 'triangulation.data')
        Builder.load_file('layoutTrianAddDialog.kv')
        self.loadTriaItems()
        self.listBuild()
        self.aisBroadcasting = False
        self.hdg = 0.0
        self.lat = 0.0
        self.lon = 0.0
    
    def isReady(self):
        o = self.gui.rl.ids.tri_addBt
        o.data = {
            'flag-triangle': 'New',
            'cube-send': 'AIS points'
            }
        o.callback = self.on_select
        self.gui.sen.comCal.addCallBack(self)
        self.gui.sen.gpsD.addCallBack(self)
        Clock.schedule_interval(self.updateDoneItemsInfo,2.12)
    
    
    def listClear(self):
        self.gui.rl.ids.bl_triList.clear_widgets()
      
    def listBuild(self):
        l = self.gui.rl.ids.bl_triList
        self.wItems = []
        for ni,i in enumerate(self.triaItems):
            st = ""
            if i.status == 'DONE':
                st = "lat: {} lon: {}".format(i.trianPoint.lat, i.trianPoint.lon)
            ii = ThreeLineListItem(
                text = "name:{} points:{} status:{}".format(i.name, len(i.points),i.status),
                secondary_text = st
                )
            self.wItems.append(ii)
            ii.on_release = partial(self.on_releaseItemTouch,ii,ni,i.name)
            
            l.add_widget(ii)
    
    def update(self, fromWho, vals):
        #print("update",fromWho, ' vals',vals)
        if fromWho == 'comCal':
            self.hdg = vals[0]
        if fromWho == 'gps':
            self.lat = vals['lat']
            self.lon = vals['lon']
        
    def updateDoneItemsInfo(self,a=0,b=0):
        if self.gui.rl.current != 'Triangulate':
            return None
        if self.lat and self.lon:
            p = LatLon(self.lat,self.lon)
            for ni,i in enumerate(self.triaItems):
                if i.status == 'DONE':
                    disMit = m2NM(p.distanceTo(i.trianPoint))
                    bear = p.bearingTo(i.trianPoint)
                    self.wItems[ni].tertiary_text = 'distance: {}[nm] at: {}` ({})'.format(
                        round(disMit,2), 
                        round(bear,1), 
                        compassPoint(bear,3)
                        )
                else:
                    self.wItems[ni].tertiary_text = ''
                    
    
    def on_releaseItemTouch(self,item, triaNo, triaName):
        print("on_releaseItemTouch",triaNo," name",triaName)
        self.on_startEditDialog(triaNo)
    
            
    def on_select(self,a=0,b=0):
        print("on_select",a.icon," b",b)
        self.gui.rl.ids.tri_addBt.close_stack()
        if a.icon == 'flag-triangle':
            self.gui.on_makeToast("building form ...")
            Clock.schedule_once(self.on_startAddDialog,0.01)
        elif a.icon == 'cube-send':
            self.aisBroadcastStart()
        
        
    def aisBroadcastStart(self):
        if self.aisBroadcasting:
            self.aisBroadcasting = False
            Clock.unschedule( self.aisBroadcasClock )
            self.gui.on_makeToast("stop ais points broadcast")
            
        else:
            self.aisBroadcasting = True
            self.aisBroadcasClock = Clock.schedule_interval( self.aisBroadcastPoints, 2.01 )
            self.gui.on_makeToast("start ais points broadcas")
            
    def aisBroadcastPoints(self,a=0,b=0):
        if len(self.triaItems) > 0:
            for ti,t in enumerate(self.triaItems):
                if t.status == 'DONE':
                    msg = self.getAisStr(ti, t.trianPoint)
                    self.gui.sf.sendToAll(msg)
                    print("broadcast ",msg)
                else:
                    print("skipp",t.name)
        
    def on_startEditDialog(self,trianNo):
        print("on_startEditDialog")
        self.editItem = trianNo
        self.addDialog = TrianRunAddDialog( 
            self.gui,
            self,
            TrianAddDialog,
            'edit' 
            )
        
    def on_startAddDialog(self,*a):
        print("on_startAddDialog")
        self.addDialog = TrianRunAddDialog( 
            self.gui,
            self,
            TrianAddDialog,
            'add' 
            )
        
    def getNextName(self):
        return 'point NO.{}'.format(len(self.triaItems)+1)
        
    
    def loadTriaItems(self):
        print("loadTriaItems")
        r = DataSR_restore(self.fileStoragePath)
        print("r",r)
        if r == None:
            return 0
        for t in r:
            print("restoring", t['name'],' status',t['status'],' points',len(t['points']))
            self.addTriPoint(t)
            
        
    def addTriPoint(self,t, returnIt = False):
        print("addTriPoint",t)
        if len(t['points']) > 0:
            p = t['points'][0]
            p0 = trianPiont(p['lat'], p['lon'],p['bearing'],p['entryDate'])
        
        if len(t['points']) == 2:
            p = t['points'][1]
            p1 = trianPiont(p['lat'], p['lon'],p['bearing'],p['entryDate'])
        
        points = []
        if len(t['points']) > 0:
            points = []
        
        if len(t['points']) > 0:
            points.append(p0)
        if len(t['points']) == 2:
            points.append(p1)
            
        if t['status'] == 'DONE':
            x = trianItem(
                t['name'], 
                points, 
                'DONE', 
                LatLon(str(t['tri'][0]),str(t['tri'][1]))
                )
        else:
            x = trianItem(t['name'], points)
        
        
        if returnIt:
            return x
        else:
            self.triaItems.append(x)
    
    
    def saveTriaItems(self):
        print("saveTriaItems",len(self.triaItems))
        ts = []
        for t in self.triaItems:
            ts.append(t.getDict())
        
        print("status of saving",DataSR_save(ts, self.fileStoragePath) )
        
    
        
    def getAisStr(self,mssi_, LatLon):
        # status 
        # 0 - undarway
        # 1 - anchore
        # 2 - not under command
        # 3 - restricted movability
        # 4 - contrained
        # 5 - moored
        # 6 - aground
        # 7 - engaged in finish
        # 8 - under way sailing
        # 9 - high speed craft
        # 10 - wing in ground effect
        # 11 - power driven vessel towing 
        # 12 - power driven vessel pushing
        # 13 - reserved 13
        # 15 - undefined
        
        a = aislib.AISPositionReportMessage(
            mmsi = mssi_,
            pa = 1,
            lon = int((LatLon.lon)*60*10000),
            lat = int((LatLon.lat)*60*10000),
            status = 15,
            ts = 30,
            raim = 0,
            comm_state = 0       
            )
        ais = aislib.AIS(a)
        #print("ais",ais)
        p = ais.build_payload(False)
        #print("payload",p)
        return p
        
    
    
if __name__ == "__main__":
    tri = Triangulacja(None)
    
    print("run as single module :P")
    p0 = trianPiont("09° 36.6029' N","079° 35.6117' W",77.0,0)
    p1 = trianPiont("09° 36.3585' N","079° 35.3761' W",21.0, 0)
    x = trianItem(1, [p0,p1])
    
    tri.triaItems.append( x )
    tri.saveTriaItems()
    
    aisPayload = tri.getAisStr(x.name,x.trianPoint)
    cmd = '''echo -en \'{}\' | nc -l -w 2 localhost 11225 '''.format(aisPayload)
    
    
    
    
    print("exec...")
    os.system(cmd)
    print("DONE")
    
    
  
        