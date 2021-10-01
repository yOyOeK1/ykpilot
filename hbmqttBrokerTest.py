
import time
from hbmqttBroker import broker_coro


if __name__ == "__main__":
    print("maint :)")
    
    broker_coro()    
    while True:
        print(".")
        time.sleep(2)
    
    