import json
import uasyncio as uaio

class MyJsonToMqtt:
    
    nParseEr = 0
    nParseNaN = 0
    nOthersHandler= 0
    nPub = 0
    
    def __init__(self,mqttPubCallback, othersCommandParserHandler):
        print("MyJsonToMqtt.init")
        
        self.nParseEr = 0
        self.nParseNaN = 0
        self.nPub = 0
        self.mqc = mqttPubCallback
        self.otherHandler = othersCommandParserHandler
        
        print("MyJsonToMqtt.init DONE")
      
      
      
    def mqBroadJson(self, j, pref = "", level = 0):
        #print("broadcast",j," --> ",type(j))
        if isinstance(j, dict):
            for k in j.keys():
                #print("pref:",pref,"key:",k," -> ",str(j[k])[:10])
                if level < 6:
                    self.mqBroadJson(j[k], "{}/{}".format(pref,k))
                
        else:
            #print("is it a leaf ? :))")
            #print("mq:",pref," (",j,")")
            self.mqc.pub("uart/batMux{}".format(pref), j, False)
            self.nPub+= 1
            #print("p ",pref," m",j)
        
    def parseLineAsync(self, l):
        #pTime = 12
        #print("pla:",l)
        if l == None:
            return 0
        d = False
        ll = len(l)
        if ll>1 and l[0] == "{" and l[-1] == "}":
                if d:print("    got json?")
                js = None
                #await uaio.sleep_ms(pTime)
                try:
                    #js = json.loads( l.replace("'",'"') )
                    js = eval(l.replace("'",'"'))
                    if not isinstance(js, dict):
                        js = None
                except:
                    #print("E j43:",l)
                    #self.mqc.pub("esp01/mjtm/nNaNExa", l, False)
                    self.nParseEr+= 1
                #await uaio.sleep_ms(pTime) 
                if d:print("    js",js)  
                if js != None:
                    self.mqBroadJson(js)
                    return 1
                    #await uaio.sleep_ms(pTime)
                    
        elif l[0] == "$" and self.otherHandler(l[1:]):
            self.nOthersHandler+=1
        else:
            if d:print("    NaN",l)
            #self.mqc.pub("esp01/mjtm/nNaNExa", l, False)
            self.nParseNaN+=1
            
        return 0
        
    def parse(self, buf):
        d = False
        if d:print("mjtm.parse")
        for l in buf:
            self.parseLine(l)
                
                
                
                