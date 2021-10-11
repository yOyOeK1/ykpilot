import logging
import asyncio
import sys
import os
from hbmqtt.broker import Broker
from hbmqtt.mqtt.constants import QOS_1
import yaml

class hbmqttBroker:
    
    def __init__(self, gui = None):
        self.gui = gui
        self.config = {
     'listeners': {
        'default': {
            'type': 'tcp',
            'bind': '0.0.0.0:12883'    # 0.0.0.0:1883
        },
        'my-ws-1':{
            'bind': '0.0.0.0:12808',
            'type': 'ws'
        },
        
    },
    'sys_interval': 10,
    'topic-check': {
        'enabled': False
    }
}    
        #print(self.config)
    
    
    async def runIt(self):
        print("hbmqttBroker.runIt()")
        print("congif is:")
        print(self.config)
        print("make the broker")
        self.broker = Broker(self.config,plugin_namespace='invalid.namespace')
        print("try to start it...")
        try:
            await self.broker.start()
        except:
            print("EE -- some error on broker start")
        print("hbmqttBroker.runIt is going good")
        while True:
            print("hbmqttBroker running ...")
            await asyncio.sleep(2)
        print("hbmqttBroker.runIt() DONE")
        
if __name__=="__main__":
    h = hbmqttBroker()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(h.runIt())
    #loop.run_until_complete(guiStarter())
    loop.close()

