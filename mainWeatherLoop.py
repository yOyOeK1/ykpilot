#!/usr/bin/env python3


from TimeHelper import *
import os
import time

adres = "https://www.pancanal.com/eng/eie/radar/current_image.gif"
iterSleep = 60*15 # 10 min

if __name__ == "__main__":
	
	th = TimeHelper()
	tLast = th.getTimestamp()
	
	while True:
		tn = th.getTimestamp()
		if (tn-tLast)> iterSleep:
			fileName = "./wRadar/wRadar_%s.gif" % th.getNiceFileNameFromTimestamp()
			cmd = "wget '%s' -O '%s'" % (adres, fileName)
			os.system(cmd)
			print("downloaded ",fileName)
			tLast = tn
		else:
			print(th.getNiceHowMuchTimeItsTaking(iterSleep-(tn-tLast)) )
		
		time.sleep(10)
	