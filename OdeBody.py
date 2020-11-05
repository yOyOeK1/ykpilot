
import ode
import sys

class OdeBody:
    def __init__(self):
        print("odeBody")
        
        self.makeWorld()
        '''
            0 - Center
            1 - B
            2 - S
            3 - Transom
            4 - P
            5 - mast
            '''
        self.bPos = [
            [0,0,0],
            [0,0,-4],
            [2,0,0],
            [0,0,4],
            [-2,0,0],
            [0,-4,0]
            ]
        self.bList = []
        
        for b in self.bPos:
            self.bList.append( self.makeBody(b,1.0) )
            
        self.fList = []
        for b in range(5):
            self.fList.append( 
                self.makeFJ(self.bList[0],self.bList[b+1]) 
                )
        
        for f in self.fList:
            f.setFixed()
        
    
    def makeTik(self,fps):
        #print("body rotation",self.bList[0].getRotation())
        self.odeWorld.step(fps)
       
    def setForce(self,table, offsets):
        ox = offsets[0]
        oy = offsets[1]
        for i,p in enumerate(self.bPos):
            key = "%s_%s"%( p[0]+ox, p[2]+oy )
            yWaterLine = table[key]            
            
            bPos = self.bList[i].getPosition()
            #print("bPos",bPos)
            #sys.exit()
            by = bPos[1]-2.0
            #print("by",by,"yForBoat",yForBoat,"force",self.odeBoat.getForce())
            if yWaterLine>by:
                fy = (-2.5*(by-yWaterLine))
                if fy > 26.0:
                    fy =26.0
                if i == 0:
                    print("+",(fy))
                
                self.bList[i].setForce( ( 0.0, fy, 0.0 ) )
            else:
                if i == 0:
                    print("-",(0.0))
                self.bList[i].setForce( ( 0.0, 0.0, 0.0 ) )
            
        
        
    def makeFJ(self,o0, o1):
        print("makeFJ")
        odeJR = ode.FixedJoint(self.odeWorld)
        odeJR.setFeedback(True)
        odeJR.attach(o0, o1)
        return odeJR
    
    def makeBody(self,pos,mass=1.0):
        print("makeBody")
        odeBody = ode.Body(self.odeWorld)
        mas = ode.Mass()
        mas.setBox(1,1,1,1)
        mas.mass = mass
        odeBody.setMass(mas)
        odeBody.setPosition( pos )
        
        return odeBody
    
    def makeWorld(self):
        print("makeWorld")
        self.odeWorld = ode.World()
        self.odeWorld.setGravity( (0,-9.81,0) )
        