
from myFastPlot import *
import sys,random
from TimeHelper import *


class PCPlotSinAnalitics:
    def __init__(self, gui, sensor):
        print("PCPlotSinAnalitics")
        self.gui = gui
        self.sensor = sensor
        self.th = TimeHelper()
        
        self.maxOnPlot = 30*20
        
        self.dataX = []
        self.dataY = []
        
        for d in range(20):
            self.dataX.append(d)
            self.dataY.append(random.randrange(0,20))
            
            
        self.plt = myFastPlot([
            self.data0
            ],200)
        self.plt.run()
        #sys.exit(9)
        
    def update(self, fromWho, vals):
        #print("ucbComCal", fromWho,' -> ',vals)
        if fromWho == 'comCal':
            self.updateComCal(fromWho,vals)
    
    def data0(self):
        self.dataY[-1] = random.randrange(0,20)
        return self.dataX, self.dataY
    
    
    def updateComCal(self,fromWho,vals):
        if fromWho == 'comCal':
            self.HDGt.append( self.th.getTimestamp())
            self.HDGd.append(vals[0])
    
    def dHDG(self):
        return self.HDGt, self.HDGd
    
    def dSimHDG(self):
        return self.simHDG[0][-self.maxOnPlot:],self.simHDG[1][-self.maxOnPlot:]
    
    def dSimHDGTarget(self):
        return self.simHDGTarget[0][-self.maxOnPlot:],self.simHDGTarget[1][-self.maxOnPlot:]
    
    def dSimPID(self):
        return self.simPID[0][-self.maxOnPlot:],self.simPID[1][-self.maxOnPlot:]
    
    def dSimRud(self):
        return self.simRud[0][-self.maxOnPlot:],self.simRud[1][-self.maxOnPlot:]
    
    def dSimError(self):
        return self.simError[0][-self.maxOnPlot:],self.simError[1][-self.maxOnPlot:]
    
    
    