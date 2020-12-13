
import json
from senSeatalkParser import senSeatalkParser


class senMsgTypeDetector(senSeatalkParser):
    
    def msgDetParse(self, buf):
        #print("msgDetParse",buf)
        bs = buf.count('{')
        be = buf.count("}")
        if bs != be:
            print("EE - msgTypeDetector no equal count of brackets :(")
            return None
        
        jStr = buf[6:]
        j = None
        try:
            j = json.loads(jStr.replace("'",'"'))
            #print("got json !")
        except:
            print("EE - msgTypeDetector error in str to json convert :(")
            return None
        
        if j != None:
            keys = list(j.keys())
            #print("keys",keys)
            if len(keys) == 1:
                if keys[0] == 'seatalk':
                    #print("got seatalk ....")
                    return self.seatalkParse(j[keys[0]])
                if keys[0] == 'dht':
                    return self.gui.sen.senDTH.update(j[keys[0]])
        
