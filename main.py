#!/usr/bin/env python3
#import kivy
import asyncio
import time
from gui import gui
import DataSaveRestore
import traceback

from kivy import platform as kplatform
from DataSaveRestore import DataSR_save
import sys
from hbmqttBroker import hbmqttBroker


hbTask = None
guiTask = None

if __name__ == "__main__":

	g = gui()

	if kplatform == "android":
		g.run()
		g.on_pouse()
		sys.exit(0)


	async def guiStarter():
		print("guiStarter")
		g = gui()
		
		if kplatform == "android":
			try:
				#g.asyncioRun()
				await g.run()				
			except:
				print("EE - there is a big error")
				print("------------ trackback ------------")
				print( traceback.format_exc() )
				print("------------ trackback ------------")
				print("-------------print_exc")
				traceback.print_exc(limit=100, file=sys.stdout)
				print("-------------print_exc")
				
			
		# not android
		else: 
			print("not android host")
			await g.run()
			print("force to save config for ykpilot")
			g.on_pause()
			
			print("end process trying to save qrl status to file")
			data = g.driver9.qa.q_table
			file = "./qs_q_table_test2.zip"
			res = DataSR_save(data, file, True)
			print("saved ? res",res)
	
	print("------------ trackback ------------")
	print( traceback.format_exc() )


	async def hbStarter():
		print("hbStarter")
		hb = hbmqttBroker()
		await hb.runIt()
		print("hbStart DONE")
		i = 0
		while True:
			print("hbBroker loop",i)
			i+=1
			await asyncio.sleep(5)
			
		print("II - hbStarter quiting")
		
	async def run_app_happily( guiTask, hbTast):
		#await async_runTouchApp(guiTask, async_lib='asyncio')  # run Kivy
		guiTask.async_run()
		print('App done')
		hbTask.cancel()
		
	def allStart():
		hbTask = asyncio.ensure_future(hbStarter())
		async def run_wrapper():
			print('App done')
			await g.async_run(async_lib='asyncio')
			print("run_wrapper")
			g.on_pause() # force to save configs
			hbTask.cancel()
		
		return asyncio.gather(run_wrapper(), hbTask)

	
	loop = asyncio.get_event_loop()
	loop.run_until_complete(allStart())
	#loop.run_until_complete(guiStarter())
	loop.close()

'''
TODO
[] - vfb load in kivy
[] - load page on add widget list of widgets
[] - load page on add widget form

[+] - screen sensors on load page
'''

