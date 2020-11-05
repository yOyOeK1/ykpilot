

class ScreenNMEAMultiplexer:
    
    def setGui(self, gui):
        self.gui = gui
        
        self.setUpGuiToValues()
    
    def setUpGuiToValues(self):
        ip = self.gui.rl.ids.l_nmeMulIp
        ip.text = "Multiplexer ip: {}:{}".format(
            self.gui.senderIp, self.gui.senderPort
            )
        
        