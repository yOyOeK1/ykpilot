import json

class MyJsonToMqtt:
    
    nParseEr = 0
    nParseNaN = 0
    nPub = 0
    
    def __init__(self,mqttPubCallback):
        print("MyJsonToMqtt.init")
        
        self.nParseEr = 0
        self.nParseNaN = 0
        self.nPub = 0
        self.mqc = mqttPubCallback
        
        print("MyJsonToMqtt.init DONE")
      
      
      
    def mqBroadJson(self, j, pref = ""):
        #print("broadcast",j," --> ",type(j))
        if isinstance(j, dict):
            for k in j.keys():
                #print("pref:",pref,"key:",k," -> ",str(j[k])[:10])
                self.mqBroadJson(j[k], "{}/{}".format(pref,k))
                
        else:
            #print("is it a leaf ? :))")
            #print("mq:",pref," (",j,")")
            self.mqc.pub("uart{}".format(pref), j, False)
            self.nPub+= 1
            #print("p ",pref," m",j)
        
        
    def parse(self, buf):
        d = False
        if d:print("mjtm.parse")
        for l in buf:
            ll = len(l)
            if ll>1 and l[0] == "{" and l[-1] == "}":
                    if d:print("    got json?")
                    try:
                        self.mqBroadJson(
                            json.loads( l.replace("'",'"') )
                            )
                    except:
                        self.nParseEr+= 1
            else:
                if d:print("    NaN",l)
                self.nParseNaN+=1
                
                
                
                