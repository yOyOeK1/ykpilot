from helperUdp import helperUdp


class apWifiCommunication():
    
    def __init__(self):
        print("apWifiCommunication init!")
        
        
        
    def connect(self, ip, port):
        self.udp = helperUdp(ip,port)
        self.udp.setAsSender()
    
    def disconnect(self):
        pass
    
    def status(self):
        return 0
    
    def send(self, toSend):
        print("send: [",toSend,"]")
        self.udp.send(toSend)
        return "res"
    
    