import logging
import asyncio
import os
from hbmqtt.broker import Broker
import yaml

@asyncio.coroutine
def broker_coro():
    
    config = {
     'listeners': {
        'default': {
            'type': 'tcp',
            'bind': 'localhost:12883'    # 0.0.0.0:1883
        }
    },
    'sys_interval': 10,
    'topic-check': {
        'enabled': False
    }
}    
    print(config)
    broker = Broker(config,plugin_namespace='invalid.namespace')
    yield from broker.start()


if __name__ == '__main__':
    formatter = "[%(asctime)s] :: %(levelname)s :: %(name)s :: %(message)s"
    #logging.basicConfig(level=logging.INFO, format=formatter)
    asyncio.get_event_loop().run_until_complete(broker_coro())
    asyncio.get_event_loop().run_forever()
