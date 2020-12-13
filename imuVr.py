from MyCalculate import MyCalculate, SPoint



class imuVr:
    
    def __init__(self,senXyzDataObj):
        self.senObj = senXyzDataObj
        self.mc = MyCalculate()
        pass
    
    def getAnglesAndLength(self, p):
        angles = self.mc.getVectorAngles(p)
        return [
            angles[0],
            angles[1],
            angles[2],
            "TODO"
            ]
        
        #x
        
        #y
        
        #z