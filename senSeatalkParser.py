


class senSeatalkParser:
    
    
    def stMakeWork(self, a, b ):
        if len(b) == 1:
            b = "0%s"%b
        return float.fromhex("%s%s"%(a,b))
    
    def seatalkParse(self,j):
        #print("seatalkParse[",j,"]")
        
        st = j.split(',')[:-1]
        
        
        if len(st) == 5 and st[0] == '4':
            print("autohelm st40 depth sounder msg...")
            val = self.stMakeWork(st[3], st[2])
            ta = {'depth':(val*0.03048)}
            self.gui.sen.seatalk.update(ta)
            return True
        
        return None
        
        