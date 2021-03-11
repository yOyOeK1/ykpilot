import sys,random
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.lang.builder import Builder
from kivy.uix.label import Label

from kivy import metrics as kmetrics
from kivymd.uix.textfield import MDTextField
from kivy.clock import Clock


class ScreenSensors:
    
    def __init__(self):
        Clock.schedule_interval(self.updateIpsOnScreen, 2.)
    
    def setGui(self, gui):
        self.gui = gui
        self.initDone = False
        self.wObjs = {}
        self.initSensorsWidgets()
        
        
    def getRowForGui(self, name):
        rb = MDBoxLayout( orientation='horizontal' )
        vl = MDTextField()
        rb.add_widget(vl)
        #rb.add_widget( Label(text="   {}:".format(name) ) )
        #vl = Label(text="- - -")
        #rb.add_widget(vl)
        
        vl.hint_text = "{}:".format(name)
        vl.text = "- - -"
        vl.disabled = True
        
        return vl,rb
        
        
    def updateIpsOnScreen(self, *a):
        if self.gui.rl.current == 'Sensors':
            print("soo?",self.gui.ips)
            self.gui.rl.ids.l_phoLocIps.text = "{}".format(
                ", ".join(self.gui.ips)
                )
        
    def update(self, fromWho, vals):
        if self.gui.rl.current != "Sensors":
            return 0
        #print('update',fromWho,'->',vals)
        
        wObj = self.wObjs[fromWho]
        #print("wObj",wObj)
        objs = wObj['objs']
        for ii, o in enumerate(objs):
            #print("making ii",ii,' o',o)
            ok = list(o.keys())[0]
            #print("ok",ok)
            if wObj['vType'] == 'list':
                #print("list val",vals[ii])
                objs[ii][ok].text = str(vals[ii])
            if wObj['vType'] == 'dict':
                try:
                    #print("dict val",vals[ok])
                    objs[ii][ok].text = str(vals[ok])    
                except:
                    print("EE - 0032 val key",ok," not pressent :(")
                    objs[ii][ok].text = 'NaN'
                
    def initSensorsWidgets(self):
        if self.initDone == True:
            return 1
        
        bw = self.gui.rl.ids.l_sSen
        print("ssen - bw children",len(bw.children))
        
        for s in self.gui.sen.sensorsList:
            print("\-","(",s.type,")",s)
            
            sDesc = s.getValuesOptions()
            sDescType = list(sDesc.keys())[0]
            sVals = sDesc[sDescType]
            objs = []
            self.wObjs[s.type] = {
                'name':s.type,
                'vType':sDescType
                }
            
            print("buildind sensor view for ",s.type,
                  " [",sDescType,"]->",sDesc[sDescType]
                  )
            
            mb = MDBoxLayout(
                orientation='vertical',
                size_hint= (1.0,None)
                )
            mb.add_widget( Label(text=str(s.type)) )
            for ii,v in enumerate(sVals):
                vl,rb = self.getRowForGui(v)
                objName = v if sDescType == 'dict' else ii
                objs.append( { objName:vl } )
                mb.add_widget(rb)
                
            s.addCallBack(self,'Sensors', maxUpdateEvery=(random.randrange(1000,2000)/1000.0))
            
            self.wObjs[s.type]['objs'] = objs
            mb.size = [
                mb.size[0],
                (len(sVals)+1)*(self.gui.btH)
                ]
            
            bw.add_widget(mb)
            
           
           
        #print(self.wObjs)
        #sys.exit(0) 
        self.initDone = True