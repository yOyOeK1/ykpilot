from senProto import senProto



class senSeatalkParser(senProto):
    
    def toTwo(self, a):
        #if len(a) == 0:
        #    return '00'
        #elif len(a) == 1:
        #    return "0%s"%a
        #else:
        #    return a
        return "{:0>2}".format(a)
    
    def stMakeWork(self, a, b ):
        #b = self.toTwo(b)
        #return float.fromhex("%s%s"%(a,b))
        return float.fromhex( "{:0>2}{:0>2}".format(a,b) )
    
    def seatalkParse(self,j,aa=1,ba=1):
        #print("seatalkParse[",j,"]")
        
        st = j.split(',')[:-1]
        #print("st[{}]".format(st))
        
        #depth sounder msg st40
        if len(st) == 5 and st[0] == '4':
            print("autohelm st40 depth sounder msg...")
            val = self.stMakeWork(st[3], st[2])
            ta = {'depth':(val*0.03048)}
            self.gui.sen.seatalk.update(ta)
            
            msg = ("$YKDBT,{feet},f,{meters},M,{meters},F".format(
                feet = round((val*0.1),1),
                meters = round((val*0.03048),1)
                ))
            #self.gui.sf.sendToAll(msg)
            self.broadcastByTCPNmea(self.gui, msg)
            self.gui.sen.mqc.pub("v/seatalk/depth")
            return True
        
        #depth sounder msg st60
        elif len(st) == 5 and st[0] == '0' and st[1] == '2':
            print("raymarine st60 depth sounder msg...")
            val = self.stMakeWork(st[4], st[3])
            ta = {'depth':(val*0.03048)}
            self.gui.sen.seatalk.update(ta)
            
            msg = ("$YKDBT,{feet},f,{meters},M,{meters},F".format(
                feet = round((val*0.1),1),
                meters = round((val*0.03048),1)
                ))
            #self.gui.sf.sendToAll(msg)
            self.broadcastByTCPNmea(self.gui, msg)
            self.gui.sen.mqc.pub("v/seatalk/depth")
            
            
            return True
        
        
        return None
        
        