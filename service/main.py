import asyncio
import time 
from FileActions import *
from TimeHelper import *
from helperTwistedTcp import *
import sys,os,platform
from hbmqttBroker import hbmqttBroker

iterCount = 0


async def startHB():
	hb = hbmqttBroker()
	await hb.runIt()


if __name__ == "__main__":
	print("service ?")
	
	loop = asyncio.get_event_loop()
	loop.run_until_complete(startHB())
	#loop.run_until_complete(guiStarter())
	loop.close()
	
	while True:
		print("service iter:",iterCount)
		time.sleep(1)
		iterCount+= 1
	print("service DONE")


		