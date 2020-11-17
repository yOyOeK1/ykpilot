from Widget_cn import Widget_cn

class Widget_cnDiff(Widget_cn):
    
    
    def setDiffs(self,
        callback0, valn0,
        callback1, valn1,
        angleNormalize = False        
        ):
        #    don't need to set up in setValues correct callbacks
        
        self.callback0 = callback0
        self.valn0 = valn0
        self.val0 = None
        self.callback1 = callback1
        self.valn1 = valn1
        self.angleNormalize = angleNormalize
        
        
    
    def update(self, fromWho, vals):
        if 0:
            print("update from widget_n[{}] from:{} callback:{} gotvals:{}".format(
                self.mtitle, fromWho, self.mcallback, vals
                ))
            
        if fromWho == 'comCal':
            vals = [vals]
            
        if fromWho == self.callback0:
            self.val0 = vals[self.valn0]
        elif fromWho == self.callback1 and self.val0 != None:
            self.val1 = vals[self.valn1]
            
            v = self.val0 - self.val1
            
            if self.angleNormalize:
                if v > 180.00:
                    v-= 360.00
                elif v < -180.00:
                    v+=360.00
            
            self.l.text = str( "%s%s"%( 
                round( v, self.mround ) if self.mround > 0 else int( v ), 
                self.munit 
                ) )
            self.l.refresh()
            self.recL.texture = self.l.texture
            #print("recl size",self.l.texture.size)
            self.recL.size = self.l.texture.size
                
                
            if 0:
                print("o ",self.mtitle,
                        "pos:",int(self.pos[0]),"x",int(self.pos[1]),
                        "size:",int(self.size[0]),"x",int(self.size[1]))
            
        if self.drawItC == 1:
            self.setPos(self.pos)
            self.drawItC+=1
    