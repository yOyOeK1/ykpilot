import network

class MyWifi:
    nic = None
    isOk = False
    isConnected = False
    ifConfig = None
    myIp = ""
    
    def __init__(self, essid_, passwd_):
        print("MyWifi.init")
        
        
        self.nic = network.WLAN( network.STA_IF)
        self.nic.active(True)
        self.nic.connect(essid_,passwd_) 
        
        
    def is_connected(self):
        return self.nic.isconnected()
    
    def if_config(self):
        return self.nic.ifconfig()
        
    def chkStatus(self):
        #print("MyWifi.chkStatus")
        self.isConnected = self.is_connected()
        if self.isConnected == False:
            self.isOk = False
            self.myIp = ""
            return False
        self.ifConfig = self.if_config()
        if self.isConnected == True and len(self.ifConfig)==4 and self.ifConfig[0] != '0.0.0.0':
            self.isOk = True
            self.myIp = self.ifConfig[0]
        else:
            self.isOk = False

        return self.isOk
