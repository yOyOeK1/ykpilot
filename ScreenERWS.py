from FileActions import *
from TimeHelper import *
from helperTwistedTcp import *
import sys,os,platform
from kivy.core.image import Image
from MyCalculate import MyCalculate, SPoint
from pygeodesy.sphericalTrigonometry import LatLon
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from _functools import partial
from kivy.clock import Clock
from shapely.geometry.multipolygon import MultiPolygon
from shapely.geometry.point import Point
import numpy as np
from shapely.geometry.multipoint import MultiPoint
from DataSaveRestore import DataSR_save, DataSR_restore
from shapely.geometry import polygon
from shapely.geometry.polygon import Polygon


class ScreenERWS:
    
    wImgUrl = 'http://www.pancanal.com/eng/eie/radar/current_image.gif'
    wDirName = 'ykWeather'
    wIter = 5 # min
    wLegend = [
        [40,460],    #min
        [40,6],     #max
        ]
    wScale = {
        'xy0': [209,168],
        'll0': ["09° 21.5461' N", "079° 53.3004' W"],
        'xy1': [408,228],
        'll1': ["09° 33.3800' N", "078° 56.8303' W"],
        }
    wMy = ["09° 36.7351' N", "079° 35.1304' W"]
    wFrame = [ 48,1, #top left
        509,496 #bottom right
        ]
    
    def __init__(self,gui):
        self.gui = gui
        
        self.th = TimeHelper()
        self.fa = FileActions()
        self.mc = MyCalculate()
        
        if platform.release() == "4.15.0-126-generic":
            print("platform my laptop?")
            self.wPath = "/home/yoyo"
        else:
            self.wPath = "/storage/emulated/0"
        self.wPath = self.fa.join(self.wPath, self.wDirName)
        
        self.recomputeScaleInfo()
        
    
    def recomputeScaleInfo(self):
        print("recomputeScaleInfo")
        pixDist = self.mc.distance(
            SPoint( self.wScale['xy0'][0],self.wScale['xy0'][1] ),
            SPoint( self.wScale['xy1'][0],self.wScale['xy1'][1] )
            ) 
        self.wScale['xyDist'] = pixDist
        print("xyDist:",pixDist,'[pixels]')
        
        LL0 = LatLon( self.wScale['ll0'][0], self.wScale['ll0'][1] )
        LL1 = LatLon( self.wScale['ll1'][0], self.wScale['ll1'][1] )
        llDist = LL0.distanceTo(LL1)
        self.wScale['llDist'] = llDist
        print("llDist:",llDist,'[meters]')
        
        LLMy = LatLon( self.wMy[0], self.wMy[1] )
        self.xyMy = [
            self.mc.remap( self.wScale['xy0'][0], self.wScale['xy1'][0], LL0.lon, LL1.lon, LLMy.lon ),
            self.mc.remap( self.wScale['xy0'][1], self.wScale['xy1'][1], LL0.lat, LL1.lat,  LLMy.lat )
            ]
        print("xyMy",self.xyMy)
        
    
    def analiseImg(self, imgPath):
        print("analiseImg [%s]"%imgPath)
        img = Image.load(imgPath,keep_data=True)
        size = img.size
        self.wSize = size
        print("image size:",size)
        
        self.steps = self.analiseSteps(img)
        print("found legend steps",len(self.steps))
        
        cPath = "%s_casch_"%imgPath
        cCover = "%s_cover"%cPath
        cPolis = "%s_polis"%cPath
        cMeshs = "%s_meshs"%cPath
        if self.fa.isFile(cMeshs):
            print("pickle meshs :) ?")
            m = DataSR_restore(cMeshs)
            self.polis = {}
            print("got from cashe file steps",len(m))
            for si,k in enumerate(m.keys()):
                print("restoring step",k)
                print("meshes",len(m[k]))
                m0 = Polygon()
                meshs = m[k]
                for me in meshs:
                    print("points:",len(me))
                    #print("->",me)
                    m1 = Polygon(me).simplify(0.1,preserve_topology=True)
                    m0 = m0.union( m1 ).simplify(0.1,preserve_topology=True)
                self.polis[int(k)] = m0
                print("poli DONE area",self.polis[int(k)].area)
            
        else:
            self.cover,self.polis,self.meshs = self.analiseCover(img)
            DataSR_save(self.meshs, cMeshs)
        
        
    def analiseCover(self, img):
        cover = {}
        polis = {}
        meshs = {}
        for r in range(len(self.steps)):
            cover[ r ] = []
            polis[ r ] = None
            meshs[ str(r) ] = []
        
        for x in range(self.wFrame[0], self.wFrame[2],1):
            for y in range(self.wFrame[1], self.wFrame[3],1):
                c = img.read_pixel(x,y)
                try:
                    ci = self.steps.index(c)
                except:
                    ci = -1
                if ci >= 0:
                    #print("c",c,' ci',ci)
                    p = (x,y)
                    for cc in range(0,ci+1, 1):
                        cover[cc].append(p)
        
        for r in range(len(self.steps)):
            if r >= 0:
                print("cover at ",r,' pixels',len(cover[r]))
                polis[r] = MultiPoint(cover[r])
                polis[r] = polis[r].buffer(1.0).buffer(-3.0).buffer(2.0)
                polis[r] = polis[r].simplify(0.75,preserve_topology=True)
                print("is valid multipoly",polis[r].is_valid)
                print("area",polis[r].area)
                try:
                    print("geoms",len(polis[r].geoms))
                    haveGeoms = True
                except:
                    haveGeoms = False
                    print("no geoms but have exterior?")
                    print(len(polis[r].exterior.coords))
                    if len(polis[r].exterior.coords):
                        ta = []
                        for mp in list(polis[r].exterior.coords[:]):
                            ta.append( [int(mp[0]), int(mp[1])] )
                        meshs[str(r)].append( ta ) 
                
                if haveGeoms:
                    for g in polis[r].geoms:
                        ta = []
                        for mp in list(g.exterior.coords[:]):
                            ta.append( [int(mp[0]), int(mp[1])] )
                        meshs[str(r)].append( ta )
                    
                    
                #except:
                #    print("no geoms so one poly ?")
            
            
        return cover,polis,meshs
        
    def analiseSteps(self, img):
        #return legend from max rain to min colors
        s = []
        x = self.wLegend[0][0]
        cLast = None
        for y in range(self.wLegend[1][1],self.wLegend[0][1],1):
            c = img.read_pixel(x,y)
            #print("y:",y," - color",c)
            if cLast == None or cLast != c:
                cLast = c
                s.append(c)
        s.reverse() 
        return s


class ScreenERWSWid(Widget):
    pass

class ScreenERWSWidget:
    
    def build(self):
        bl = MDBoxLayout(orientation="vertical")
        
        i = ScreenERWSWid(
            size_hint = [None,None],
            size = [512,512] 
            )
        self.can = i.canvas
        bl.add_widget(i)
        
        
        return bl

    def drawSomeStuff(self, ana,a=0,b=0):
        self.ana = ana
        a = self.ana
        with self.can:
            Color(0,0,0)
            Rectangle( 
                size=[512,512],
                pos=[0,0] 
                )
            
            
            #legend
            y = 0
            for l in a.steps:
                Color(l[0],l[1],l[2])
                Rectangle( 
                    size=[10,10],
                    pos=[0,y] 
                    )
                y+=10
                
            #cloudCover
            for li, l in enumerate(a.steps):
                if li in [3,4,7,8]: 
                    Color(l[0],l[1],l[2])
                    
                    poli = a.polis[li]
                    for x in range(a.wFrame[0], a.wFrame[2],1):
                        for y in range(a.wFrame[1], a.wFrame[3],1):
                            if poli.contains(Point(x,y)):
                                Rectangle( 
                                    size=[1,1],
                                    pos=[x,a.wSize[1]-y] 
                                    )
            
            
class ScreenERWSAlone(ScreenERWSWidget,MDApp):
    pass

if __name__ == "__main__":
    print("stand alone")
    print("Early Rain Warning System")
    
    args = sys.argv[1:]
    argsCount = len( args )
    
    print("args: {0}".format(args))
    if len(args) == 1:
        file = args[0]
        doGui = False
    else:
        file = '/home/yoyo/ykWeather/wRadar_2020_08_16_08_59_44.gif'
        doGui = True
        
    print("file ",file)
    #sys.exit(9)
    
    if doGui:
        sa = ScreenERWSAlone()
    else:
        sa = 0
    
    s = ScreenERWS(sa)
    s.analiseImg(file)
    
    if doGui:
        Clock.schedule_once( partial(sa.drawSomeStuff,(s)), 1 )
        
        sa.run()
    