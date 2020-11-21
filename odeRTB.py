import ode
from ode import World, Body, Mass
from TimeHelper import TimeHelper

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
from direct import interval
#style.use('fivethirtyeight')
import _thread
import numpy as np

class odeRTB:
    def __init__(self,gui):
        self.gui = gui
        
        self.vDHistory = []
        self.bPHistory = []
         
        self.th = TimeHelper()
        
        self.w = World()
        self.w.setGravity( ( 0.0, 0.0, 0.0 ) )
        self.b = Body(self.w)
        self.b.setPosition((0.0, 0.0, 0.0))
         
        
        self.lt = self.th.getTimestamp(microsec=True)
        self.lastVal = None
        
    def plotAnimate(self, i):
        xs = []
        ys = []
        zs = []
        for v in self.bPHistory[:-10]:
            xs.append(v[0])
            ys.append(v[1])
            zs.append(v[2])
            
        if len(self.bPHistory)>500:
            self.bPHistory.pop(0)
            self.vDHistory.pop(0)
            
            
        self.ax1.clear()
        r = np.array(xs)
        s = np.array(ys)
        t = np.array(zs)
        self.ax1.scatter(r,s,zs, marker='o')
        
        
    def startPltShow(self, a=''):
       
        self.fig = plt.figure()
        self.ax1 = self.fig.add_subplot(111,
            projection='3d'
            )
       
        ani = animation.FuncAnimation(self.fig, self.plotAnimate, interval=500)
        plt.show()
        
    iter = 0
    def update(self, fromWho, val):
        #print("ode.updateIt",fromWho)
        self.iter+=1
        if fromWho == 'accel':
            
            if len(self.vDHistory) == 10:
                _thread.start_new(self.startPltShow,())
            t = self.th.getTimestamp(microsec=True)
            if self.lastVal == None:
                self.lastVal = val
            else:
                vD = []
                for k in range(len(val)):
                    vD.append(self.lastVal[k]-val[k])
                self.vDHistory.append(vD)
                #print(t-self.lt,"    mm/s^2:",vD)
                #if (self.iter%100)==0:
                #    self.b.setLinearVel((0.0,0.0,.0))
                #    print("0.0.0")
                bp = self.b.getPosition()
                self.bPHistory.append(bp)
                #print("b pos: {}    {}    {}".format(
                #    round(bp[0], 4),
                #    round(bp[1], 4),
                #    round(bp[2], 4)
                #    ))
                avgFrom = 100
                if len(self.vDHistory)%avgFrom == 0:
                    print("recall avg")
                    vcc = [0.0, 0.0, 0.0]
                    for ii in range(avgFrom-1):
                        vcc[0]+= self.vDHistory[ii][0]
                        vcc[1]+= self.vDHistory[ii][1]
                        vcc[2]+= self.vDHistory[ii][2]
                    vcc[0]/=float(avgFrom-1.0)
                    vcc[1]/=float(avgFrom-1.0)
                    vcc[2]/=float(avgFrom-1.0)
                    self.va = vcc
                    vc = val
                elif len(self.vDHistory) > avgFrom:
                    vc = [
                        val[0]-self.va[0],
                        val[1]-self.va[1],
                        val[2]-self.va[2]
                        ]
                    
                    #print("va:",self.va)
                    
                else:
                    vc = val
                
               # print("t",(t-self.lt)/1000000.0)
                
                #print("vdh",len(self.vDHistory)," -",vc)
                
                if len(self.vDHistory) > avgFrom+10:
                    self.w.setGravity((
                        vD[0],#vc[0],#vD[0],
                        vD[1],#vc[1],#vD[1],
                        vD[2]#vc[2]#vD[2]
                        ))
                
                #self.w.step( (t-self.lt)/1000000.0 )
                self.w.step(0.1)
                
                self.lastVal = val
                self.lt = t
            