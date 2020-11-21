from kivy.uix.spinner import Spinner
from kivy.metrics import cm
from kivy.uix.boxlayout import BoxLayout
from Widget_n import MSLabel
from kivy.uix.checkbox import CheckBox
from WidgetHelper import WidgetHelper
from QueryPopup import QueryPopup
import sys


class WidgetValFunctionHandler(WidgetHelper):
    
    def __init__(self):
        self.setUp = False
        
    
    def getParametersInDict(self):
        return {
            'fun': self.fun,
            'callback0': self.callback0,
            'valn0': self.valn0,
            'callback1': self.callback1,
            'valn1': self.valn1,
            'angleNarmalize': self.angleNormalize
            }
    
    def setParametersFromDict(self, dic):
        self.setParameters(
            dic['fun'], 
            dic['callback0'], 
            dic['valn0'], 
            dic['callback1'], 
            dic['valn1'], 
            dic['angleNormalize']
            )
    
    def setParameters(self, fun = 'direct',
        callback0='', valn0='',
        callback1='', valn1='',
        angleNormalize = False        
        ):
        #    don't need to set up in setValues correct callbacks
        
        self.fun = fun
        self.callback0 = callback0.replace('gpsD','gps')
        self.valn0 = valn0
        self.val0 = None
        self.callback1 = callback1.replace('gpsD','gps')
        self.valn1 = valn1
        self.val1 = None
        self.angleNormalize = angleNormalize
        
        self.setUp = True
    
    def makeSourceSettingsPart(self, bl, sensorsList, wConf=None):
        self.sensorsList = sensorsList
        self.selChanType0 = None
        self.selChanType1 = None
        
        vSens0 = []
        for s in self.sensorsList:
            #print("s",s)
            vSens0.append(s.title)
        selSource0 = Spinner(
            text="select source 1",
            values = vSens0,
            size_hint_y = None,
            height = cm(1),
            )
        selSource0.bind(text=self.on_sourceSelected0)
        self.selSource0 = selSource0
        
        selChannel0 = Spinner(
            text="select channel",
            values = [],
            size_hint_y = None,
            height = cm(1)
            )
        selChannel0.bind(text=self.on_channelSelected0)
        self.selChannel0 = selChannel0
        
        
        self.funOpts = [
                'direct value',
                'difference from two sources',
                'sum of two sources',
                'multiply',
                'divade first by second'
                ]
        self.funReal = [
            'direct',
            'diff',
            'sum',
            'multiply',
            'divade'
            ]
        selFunction = Spinner(
            text="direct value",
            values = self.funOpts,
            size_hint_y = None,
            height = cm(1)
            )
        self.selFunction = selFunction
        
        
        vSens1 = vSens0
        for s in self.sensorsList:
            #print("s",s)
            vSens1.append(s.title)
        selSource1 = Spinner(
            text="select source 2",
            values = vSens1,
            size_hint_y = None,
            height = cm(1),
            )
        selSource1.bind(text=self.on_sourceSelected1)
        self.selSource1 = selSource1
        
        selChannel1 = Spinner(
            text="select channel 2", 
            values = [],
            size_hint_y = None,
            height = cm(1)
            )
        selChannel1.bind(text=self.on_channelSelected1)
        self.selChannel1 = selChannel1
        
        bh = self.getDialogRow()
        bl.add_widget(bh)
        bh.add_widget(MSLabel(text="source 1:"))
        bh.add_widget( selSource0 )
        
        bh = self.getDialogRow()
        bl.add_widget(bh)
        bh.add_widget(MSLabel(text="channel 1:"))
        bh.add_widget( selChannel0 )
        
        bh = self.getDialogRow()
        bl.add_widget(bh)
        bh.add_widget(MSLabel(text="function:"))
        bh.add_widget( selFunction )
        
        bh = self.getDialogRow()
        bl.add_widget(bh)
        bh.add_widget(MSLabel(text="source 2:"))
        bh.add_widget( selSource1 )
        
        bh = self.getDialogRow()
        bl.add_widget(bh)
        bh.add_widget(MSLabel(text="channel 2:"))
        bh.add_widget( selChannel1 )
        
        bh = self.getDialogRow()
        bl.add_widget(bh)
        bh.add_widget(MSLabel(text="normalize angle:"))
        self.chkAngleNorm = CheckBox()
        bh.add_widget(self.chkAngleNorm)
        
        if wConf != None:
            if wConf['valHandler']['callback0']:
                self.selSource0.text = str(wConf['valHandler']['callback0'])
            if wConf['valHandler']['valn0'] != '':
                self.selChannel0.text = self.getChannelStrSelection( self.selChannel0.values, wConf['valHandler']['valn0']  )
            
            if wConf['valHandler']['callback1']:
                self.selSource1.text = str(wConf['valHandler']['callback1'])
            if wConf['valHandler']['valn1']!='':
                self.selChannel1.text = self.getChannelStrSelection( self.selChannel1.values, wConf['valHandler']['valn1']  )
            
            self.selFunction.text = str(self.funOpts[self.funReal.index( wConf['valHandler']['fun'] ) ] )
            self.chkAngleNorm.active = True if wConf['valHandler']['angleNormalize']==1 else False

        return bl
    
    def getChannelStrSelection(self, values, val):
        valInt = False
        try:
            i = int(val)
            valInt = True
        except:
            pass
        
        if valInt:
            return values[i]
        else:
            return val 
        
    def on_sourceSelected0(self,a='',b=''):
        self.on_sourceSelected(0)
    
    def on_sourceSelected1(self,a='',b=''):
        self.on_sourceSelected(1)    
            
    def on_sourceSelected(self,a='',b=''):
        print("on_sourceSelected",a)
        print("it's for ",a)
        
        vChann = []
        if a == 0:
            src = self.selSource0.text
        elif a == 1:
            src = self.selSource1.text
            
        for s in self.sensorsList:
            sTitle = s.title.replace('gpsD','gps')
            src = src.replace('gpsD','gps')
            print("s.title123:",s.title,"    src",src)
            if sTitle == src:
                svo = s.getValuesOptions()
                print("got options",svo)
                svt = list(svo.keys())[0]
                print("options type",svt)
                if a == 0:
                    self.selChanType0 = svt
                elif a == 1:
                    self.selChanType1 = svt
                    
                if svt == 'list':
                    for o in svo[svt]:
                        vChann.append(o)
                elif svt == 'dict':
                    for o in svo['dict']:
                        vChann.append(o)
                
                if a == 0:
                    self.selChannel0.text = "select channel %s"%(a+1)
                    self.selChannel0.values = vChann
                    print("    ->",self.selChannel0.values)
                elif a == 1:
                    self.selChannel1.text = "select channel %s"%(a+1)
                    self.selChannel1.values = vChann
                    print("    ->",self.selChannel1.values)
                return True
                
    def on_channelSelected0(self,a='',b=''):
        print("on_channelSelected0",a,"\n",b)
    def on_channelSelected1(self,a='',b=''):
        print("on_channelSelected1",a,"\n",b)
    
    
    def getSettingsFromWidgetsToDict(self):
        src0 = self.selSource0.text
        if self.selChanType0 == 'dict':
            chn0 = self.selChannel0.text
        else:
            try:
                print("self.selChannel0",self.selChannel0)
                print("self.selChannel0.values",self.selChannel0.values)
                print("self.selChannel0.text",self.selChannel0.text)
                chn0 = self.selChannel0.values.index(self.selChannel0.text)
            except:
                print("EE - no source selected !")
                return 0
        
        if self.selChanType1 != None:
            src1 = self.selSource1.text
            if self.selChanType1 == 'dict':
                chn1 = self.selChannel1.text
            else:
                chn1 = self.selChannel1.values.index(self.selChannel1.text)
        else:
            src1 = ""
            chn1 = ""
        
        
        fun = self.selFunction.text
        funReal = self.funReal[self.funOpts.index(fun)]
            
        if src0 == 'gps':
            src0 = "gpsD"
        if src1 == 'gps':
            src1 = "gpsD"
            
        
        if src0 == '' and src1 == '':
            print("EE - no src for WVFH")
            sys.exit()
        
        print("src0",src0)
        print("chn0",chn0)
        print("func",fun)
        print("funReal",funReal)
        print("src1",src1)
        print("chn1",chn1)
        
        callback = [src0]
        if src1 != '':
            callback.append(src1)
            
        angleNorm = 1 if self.chkAngleNorm.active else 0
        
        vHandler = {
            'fun': funReal,
            'callback': callback,
            'callback0': src0,
            'valn0' : chn0,
            'callback1': src1,
            'valn1' : chn1,
            'angleNormalize': angleNorm
            }
        print("wvfh returning:",vHandler)
        return vHandler
        
    
    
    def updateVal(self, fromWho, vals):
        if self.setUp == False:
            return None
        
        if 0:#self.fun == 'diff':
            print('''updateVal in WVFH[{}] 
    from:[{}] gotvals:[{}] fun:[{}] 
    c0[{}] vn0[{}] 
    c1[{}] vn1[{}]'''.format(
                "widgetValFunHand", fromWho, vals, self.fun,
                self.callback0, self.valn0, self.callback1, self.valn1
                ))
            
        
            
        if fromWho == self.callback0:
            self.val0 = vals[self.valn0]
            if self.fun == 'direct':
                return self.val0
        
        if self.callback1 != '':    
            #print('got callback1',self.callback1," recive ",fromWho)
            if fromWho == self.callback1 and self.val0 != None:
                self.val1 = vals[self.valn1]
                #print("precess")
                
                if self.fun == 'diff':
                    v = self.val0 - self.val1
                if self.fun == 'sum':
                    v = self.val0 + self.val1
                if self.fun == 'multiply':
                    v = self.val0 * self.val1
                if self.fun == 'divade':
                    v = self.val0 / self.val1
                
                #print("    got v",v)
                
                if self.angleNormalize == 1:
                    if v > 180.00:
                        v-= 360.00
                    elif v < -180.00:
                        v+=360.00
                
                #print('    after angleNorm',v)
                
                return v
            
            
        return None
    