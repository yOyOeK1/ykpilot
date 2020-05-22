
import numpy as np
import math as m
from kivy.clock import Clock
import _thread
import time
import random
import DataSaveRestore
from dis import dis
from DataSaveRestore import DataSR_restore
try:
	from matplotlib import pyplot as plt
except:
	pass
from qrlHelper import *
# dummy bot turn tu direction off error 



class qrlAtomizer(qrlHelper):
	def __init__(self,name):
		super(qrlAtomizer,self).__init__(name)
		self.initIt()
		
		print("qrlAtomizer trying to load last qtable data !")
		file = "./qs_q_table_test2.zip"		
		qdata = DataSR_restore( file, True )
		if qdata != None:
			print("qdata restore elements",len(qdata))
			self.q_table = qdata
		else:
			print("no qdata to restore ")
			
		
			
			
	def get_reward(self,data):
		if self.startAtCog == "-":
			self.startAtCog = data['cogError']
			self.cross180 = False

		scp = self.startAtCog + 720.00
		cep = data['cogError'] + 720.00
		msc = scp - cep
		
		if msc > 180.00 or msc < -180.00:
			self.cross180 = True

			
		grDif = 0.0
		if len(self.gRotHistory)>2:
			grDif = data['gRot']-self.gRotHistory[-2]
		
		
		#if m.fabs(data['cogError']) < 10.0:
		#	if data['cogError'] > 0.0 and data['gRot'] < 0.05 and grDif < 0.0:
		#		return 0.0
		#	if data['cogError'] < 0.0 and data['gRot'] > -0.05 and grDif < 0.0:	
		#		return 0.0
		if m.fabs(data['cogError'])<7.0 and m.fabs(data['gRot'])<0.05 and m.fabs(grDif)<0.02:
			
			if \
				(self.startAtCog <= 0.0 and data['cogError'] <= 0.0 ) or \
				(self.startAtCog > 0.0 and data['cogError'] > 0.0 ):
				self.startAtCog = "-"
				if self.cross180 == False:
					return 0.0#( 1.0/(self.chkHowManyContinuesWorkInAction()+1) ) / (len(self.actionHistory)+1)

		return -1.0

	def get_discrete_state(self,data):
		ce = data['cogError'] # 	-180.00 180.00
		gr = data['gRot']		#	-1.0 1.0
		sog = data['sog']
		grDif = 0.0
		if len(self.gRotHistory)>2:
			grDif = data['gRot']-self.gRotHistory[-3]
			
		ce = round(ce/12.0)
		gr = round(gr/4.0,2)
		grDif = round(grDif/4.0,2)
		sog = int(sog)


		key = "%s_%s_%s_%s" %(ce,gr,grDif,sog)
		
		self.discrete_stats_used(key)

		try:
			self.q_table[key] 
		except:
			print("%s making new entry to qtable %s"%(self.name,key))
			new = [-random.random(),-random.random(),-random.random()]
			self.q_table[key] = new 
		
		return key
		

class driver9:
	fps = 30.0
	work = False
	episodeLen = fps*17.00
	EPISODES = 500000
	SHOW_EVERY = 10000
		
	def __init__(self, simEng):
		self.sim = simEng
	
	def run(self,render = True):		
		self.render = render
		self.work = True
		self.timeOfLastMove = 0.0
		self.timeOfWork = 0.0
		self.ep_rewards = []
		_thread.start_new(self.startIt,())
		
	def startIt(self):
		self.qa = qrlAtomizer("atomizer")
		self.qVer = None
		for episode in range(self.EPISODES):
			if episode >= 1:
				self.episodeNow = episode
				if not episode%100:
					nm = episode*(self.episodeLen/self.fps)/60.0/60.0*self.sim.boat['sog']
					print("episode: %s \texpiriance: %s [nm]"%(episode,round(nm,2)))
					print("res:%s",self.ep_rewards[-1])
				self.itersLeft = self.episodeLen
				self.sim.reset()
				self.mainLoop()
			
			#if not (episode+1)%self.SHOW_EVERY:
			#	_thread.start_new(self.buildPlot,())
			
				
	def buildPlot(self):	
		r = self.ep_rewards
		onGoal = []
		moves = []
		on = []
		off = []
		offCorse = []
		avg = []
		for i in r:
			onGoal.append(i['onGoal'])
			moves.append(i['moves'])
			on.append(i['on'])
			off.append(i['off'])
			offCorse.append(int(i['offCourse']))
			avg.append(i['avg'])
		try:
			#plt.plot(onGoal,label="onGoal")
			#plt.plot(moves, label="moves")
			#plt.plot(on, label="on")
			#plt.plot(off, label="off")
			#plt.plot(offCorse, label="offCourse")
			plt.plot(avg, label="reward avg")
			plt.legend(loc=1)
			plt.show()
		except:
			pass
		
				
	def mainLoop(self, reapeatStart = True):
		s = self.sim
		offCorseSum = 0.0
		movesc = 0
		offCourse = False 
		action = 0
		actionOld = 0
		self.mh = []
		self.discreteHistory = []
		self.goal = 0.0
		iterNo = 0
		timeOfWork = 0.0
		timeOfOff = 0.0
		directionChangeCount = 0
		randomDesision = 0
		randomDesisionCount = 0
		rewardMem = []
		self.sim.iter(0)
		self.q = None
		qOld = None
		itersToUseq = 0
		self.q = self.qa
		qOld = "atomizer"
		self.q.reset()
		self.q.startEpisode()
		qAtomizerTime = 0
		freeFallTime = 0
		cogErrorHistory = []
		self.sim.reset()
		self.sim.iter(0)
		self.sim.iter(0)
		self.sim.iter(0)
		self.sim.iter(0)
		finishSesionOk = True
		while self.itersLeft > 0:
			b = s.boat
			
			try:
				self.directionChangeCount = 0
				self.timeOfWork = 0.0
				self.timeOfOff = 0.0
				self.timeOfLastMove = 0.0
				
				dirOld = None
				if len(self.mh)>(2.0*self.fps):
					self.mh.pop(0)
					self.discreteHistory.pop()
				if len(self.mh)>4:
					for d in self.mh:					
						if dirOld == None:
							dirOld = dir
						if d != dirOld:
							self.directionChangeCount+=1
							self.timeOfLastMove = 0.0
						if d != 0:
							self.timeOfWork+=1.0/self.fps
						if d == 0:
							self.timeOfOff+=1.0 / self.fps
							
						self.timeOfLastMove+=1.0/self.fps
						
						dirOld = d
						
				if not iterNo % ( 2.0*self.fps ):
					timeOfOff+= self.timeOfOff
					timeOfWork+= self.timeOfWork
					directionChangeCount+= self.directionChangeCount
			except:
				pass
			
			if qOld == "free fall":
				self.sim.iter(0)
			else:
				reward = self.q.iter(b,self.sim.iter)
			#if reward == 0.0:
			#	print("main loop for ",qOld," reward 0.0")
			rewardMem.append(reward)
			self.mh.append(action-1)
			
			offCorseSum+= m.fabs(b['cogError'])
			if self.render and not self.episodeNow%self.SHOW_EVERY:
				self.sim.renderFrame()
				#print('discrete_state',discrete_state,' timeOfLastWork',self.timeOfLastMove)
				#print(reward)
				time.sleep(1.00/self.fps)
				
				print("deb ",
					"cog: ",round(b['cog'],1),
					' cogerror:',round(b['cogError'],1), 
					'corss180:',self.q.cross180
					)
			
			
			
			
			if qOld == "atomizer" and reward != -1.0:
				self.q.endEpisode()
				qOld = "free fall"
			elif qOld == "free fall" and self.q.get_reward(b) == -1.0:
				qOld = "atomizer"
				self.q.reset()
				self.q.startEpisode()
			
			if qOld == "atomizer":
				qAtomizerTime +=1
			else:
				freeFallTime+= 1
				
				
			#print("driver now is ",qOld)
			
			
			
			cogErrorHistory.append(b['cogError'])
				
			self.itersLeft-=1
			iterNo+=1
			itersToUseq-=1
			
		self.q.endEpisode()

		self.ep_rewards.append({
			#'offCorseSum': round(offCorseSum,2),
			'reward': reward,
			#'onGoal': round(self.goal,3),
			'moves': movesc,
			'off':round(timeOfOff,2),
			'on':round(timeOfWork,2),
			'changes': directionChangeCount,
			#'offCourse': offCourse,
			#'randDesisions': randomDesisionCount,
			#'min': min(rewardMem),
			#'max': max(rewardMem),
			#'avg': sum(rewardMem)/len(rewardMem),
			'q': self.qa.epsilon,
			'qAcu': sum(self.qa.episodeHistory[-100:]),
			'qMem': len(self.qa.q_table),
			'freeFallTime': freeFallTime
			})
		#print( rewardMem[-10:])
		return finishSesionOk
		
		
		