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
        }
    },
    'sys_interval': 10,
    'topic-check': {
        'enabled': False
    }
}    
        #print(self.config)
    
    
    async def runIt(self):
        print("hbmqttBroker.runIt()")
        
        print(self.config)
        self.broker = Broker(self.config,plugin_namespace='invalid.namespace')
        print("hbmqttBroker.runIt() 1")
        await self.broker.start()
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

