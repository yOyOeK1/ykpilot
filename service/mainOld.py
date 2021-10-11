
import time 
from FileActions import *
from TimeHelper import *
from helperTwistedTcp import *
import sys,os,platform

if platform.release() == "4.15.0-111-generic":
	print("platform my laptop?")
	weatherPath = "/home/yoyo"
else:
	weatherPath = "/storage/emulated/0"
weatherDir = "ykWeather"
weatherAdress = "http://www.pancanal.com/eng/eie/radar/current_image.gif"
weatherIterSleep = 5 # min

iterCount = 0

def getSleepTimeToNext():
	tNow = th.getDate(resAsDic=True)
	print("time now is:",tNow)
	sNow = (tNow['M']*60)+(tNow['S'])
	print("sNow:",sNow)
	
	nextIn = -1
	for m in eMin:
		if sNow < m:
			nextIn = m - sNow 
			break
	if nextIn == -1:
		nextIn = 0
		
	print("next is in: [",nextIn,"] sec. in:",th.getNiceHowMuchTimeItsTaking(nextIn))
	print("	it will be at:",th.getNiceDateFromTimestamp(th.getTimestamp()+nextIn))
	return nextIn




if __name__ == "__main__":
	fa = FileActions()
	th = TimeHelper()
	fLog = fa.join(weatherPath, weatherDir)
	fLog = fa.join(fLog, "service.log")
	
	eMin = []
	for m in range (0,60*61, weatherIterSleep*60):
		eMin.append(m)
	print("every:",eMin)
	
	
	print("---------------")
	print("--------------- service ")
	weatherFullPath = "%s/%s" % (weatherPath, weatherDir)
	print("weather dir ",weatherFullPath)
	print("chk if weather dir is there ?")
	fa.mkDir( weatherFullPath )
	print("dir is ", fa.isDir( weatherFullPath ) )

	f = open(fLog,"a")
	f.write("-------- new run--------\n")
	f.close()
	print("service	log file [",fLog,"]")

	while True:
		print("service ",iterCount)
		print("service is making it's thing....")
		

				

		fileName = "%s/wRadar_%s.gif" % (
			weatherFullPath,
			th.getNiceFileNameFromTimestamp()
			)
		DownloadFile( weatherAdress, fileName )
		
		fSize = fa.getSizeNice( fileName )
		print("service Download done !")
		print("service file [",fileName,"]")
		print("service		file size is:",fSize)
		print("service is done going to sleep")
		
		sleepFor = getSleepTimeToNext()

		s = "iter:		"+str(iterCount)+"\n"
		s+= "	time:			"+th.getNiceDateFromTimestamp()+"\n"
		s+= "	file size:		"+fSize+"\n"

		f = open(fLog,"a")
		f.write(s)
		f.close()

		time.sleep(sleepFor)
		iterCount+= 1


		