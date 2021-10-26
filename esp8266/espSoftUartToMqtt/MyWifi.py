import network

class MyWifi:
    nic = None
    isOk = False
    isConnected = False
    ifConfig = None
    myIp = ""
    asAp = False
    
    def __init__(self, essid_, passwd_,asAccessPoint = False):
        print("MyWifi.init")
        
        if asAccessPoint == True:
            print("    as access point")
            self.nic = network.WLAN( network.AP_IF)
            self.nic.config( essid=essid_, password=passwd_ )
            self.nic.active(True)
            self.isOk = True
            self.isConnected = True
            self.asAp = True
        else:
            self.nic = network.WLAN( network.STA_IF)
            self.nic.active(True)
            self.nic.connect(essid_,passwd_) 
        
        
    def is_connected(self):
        return self.nic.isconnected()
    
    def if_config(self):
        return self.nic.ifconfig()
        
    def chkStatus(self):
        if self.asAp:
            if self.nic.isconnected():
                self.isOk = True
                self.isConnected = True
            else:
                self.isOk = False
                self.isConnected = False
        
        else:
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
