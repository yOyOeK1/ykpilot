#!/usr/bin/env python3
import kivy
from gui import *
import DataSaveRestore
import traceback

if __name__ == "__main__":
	if kivy.platform == "android":

		g = gui()
		g.run()
		
	# not android
	else: 
		print("not android host")
		g = gui() 
		g.run()

		print("force to save config for ykpilot")
		g.on_pause()
		
		
		print("end process trying to save qrl status to file")
		data = g.driver9.qa.q_table
		file = "./qs_q_table_test2.zip"
		res = DataSR_save(data, file, True)
		print("saved ? res",res)

print("------------ trackback ------------")
print( traceback.format_exc() )