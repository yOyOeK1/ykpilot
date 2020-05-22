
import numpy as np
import math as m
from kivy.clock import Clock
import _thread
import time
import random
from dis import dis
try:
	from matplotlib import pyplot as plt
except:
	pass
from qrlHelper import *
# dummy bot turn tu direction off error 



class qrlBig(qrlHelper):
	def __init__(self,name):
		super(qrlBig,self).__init__(name)
		self.initIt()
		

	def get_reward(self,data):
		if m.fabs(data['cogError'])<5.0 and m.fabs(data['gRot'])<0.1:
			return 0.0

		return -1.0

	def get_discrete_state(self,data):
		ce = data['cogError']
		gr = data['gRot']
		
		if ce > 60.0:
			ce = 60.0
		elif ce < -60.0:
			ce = -60.0

		if gr > 1.0:
			gr = 1.0
		elif gr < -1.0:
			gr = -1.0

		ce = int(ce)//5
		gr = int(gr*10.0)


		key = "%s_%s" %(ce,gr)

		try:
			self.q_table[key] 
		except:
			print("%s making new entry to qtable %s"%(self.name, key))
			new = [-random.random(),-random.random(),-random.random()]
			self.q_table[key] = new 
		
		return key
		


class qrlSmal(qrlHelper):
	def __init__(self,name):
		super(qrlSmal,self).__init__(name)
		self.initIt()

	def get_reward(self,data):
		if m.fabs(data['cogError'])<0.5 and m.fabs(data['gRot'])<0.05:
			return 0.0

		return -1.0

	def get_discrete_state(self,data):
		ce = data['cogError']
		gr = data['gRot']
		
		if ce > 5.0:
			ce = 5.0
		elif ce < -5.0:
			ce = -5.0

		if gr > 0.2:
			gr = 0.2
		elif gr < -0.2:
			gr = -0.2

		ce = int(ce*4.0)
		gr = int(gr*100.0)


		key = "%s_%s" %(ce,gr)

		try:
			self.q_table[key] 
		except:
			print("%s making new entry to qtable %s"%(self.name,key))
			new = [-random.random(),-random.random(),-random.random()]
			self.q_table[key] = new 
		
		return key
		

class driver7:
	fps = 30.0
	work = False
	episodeLen = fps*30.00
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
		self.qBig = qrlBig("big")
		self.qSmal = qrlSmal("smal")
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
		
	def get_discrete_state(self,b):
		ce = b['cogError']
		gr = self.sim.boat['gRot']*100.00
		tola = int(self.sim.boat['ruderPos'])//5
		divs = []
		cefoldIn = None
		grfoldIn = None
		tolafoldIn = None
		res = 0.0
		sufix = 0
			
		base = 40.0
		divsCount = 6
		if ce < -(base*0.5) and ce >=-base:
			cefoldIn = divsCount
		if gr < -(base*0.5) and gr >=-base:
			grfoldIn = divsCount
		if tola < -(base*0.5) and tola >=-base:
			tolafoldIn = divsCount
		
		for doff in range(divsCount):
			d = doff-(divsCount*0.5)
			if d < 0.0:
				res = base*0.5
				resOld = res
				sufix+=1
				divs.append(round(res,3))
				if base >= ce and ce >= res:
					cefoldIn = d
				if base >= gr and gr >= res:
					grfoldIn = d
				if base >= tola and tola >= res:
					tolafoldIn = d
					
			else:
				res = -divs[sufix-1]
				divs.append(res)
				sufix-=1
				#print(res,resOld)
				if res <= ce and ce <= resOld:
					cefoldIn = d
				if res <= gr and gr <= resOld:
					grfoldIn = d
				if res <= tola and tola <= resOld:
					tolafoldIn = d
				
				resOld = res
				
			base = res
			
			
			
		
		if cefoldIn == None:
			print(res,resOld)
			print("CE None foldIn: %s"%ce)
			print(divs)
		if grfoldIn == None:
			print(res,resOld)
			print("GR None foldIn: %s"%gr)
			print(divs)
		if tolafoldIn == None:
			print(res,resOld)
			print("tola None foldIn: %s"%tola)
			print(divs)
		
		n = "%s_%s"%(cefoldIn,grfoldIn)
		return self.chkQtable(n)
		
	def chkQtable(self,discrete_state):
		try:
			self.q_table[self.qnetOld][discrete_state] 
		except:
			print("making new entry to qtable [%s] %s"%(self.qnetOld,discrete_state))
			new = [-random.random(),-random.random(),-random.random()]
			self.q_table[self.qnetOld][discrete_state] = new 
		
		return discrete_state
				
	def mainLoop(self):
		s = self.sim
		b = s.boat
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
		if m.fabs(b['cogError'])>5.0:
			self.q = self.qBig
			qOld = "big"
			itersToUseq = 2
		else:
			self.q = self.qSmal
			qOld = "smal"
			itersToUseq = 2

		self.q.reset()
		self.q.startEpisode()
		qSmalTime = 0
		qBigTime = 0
		freeFallTime = 0
		while self.itersLeft > 0:
			if qOld == "big":
				qBigTime +=1
			elif qOld == "smal":
				qSmalTime +=1

			#print("network ",qOld)

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
				reward = self.q.iter(self.sim.boat,self.sim.iter)
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
			
			
			
			
			if qOld == "smal" and self.qBig.get_reward(b) != 0.0:
				qOld = "big"
				self.q.endEpisode()
				self.q = self.qBig
				self.q.reset()
				self.q.startEpisode()
			elif qOld == "big" and reward == 0.0:
				qOld = "smal"
				self.q.endEpisode()
				self.q = self.qSmal
				self.q.reset()
				self.q.startEpisode()
			elif qOld == "smal" and reward == 0.0:
				self.q.endEpisode()
				freeFallTime+= 1
				qOld = "free fall"
			elif qOld == "free fall" and self.qSmal.get_reward(b) != 0.0:
				qOld = "smal"
				self.q = self.qSmal
				self.q.reset()
				self.q.startEpisode()
			
			
			
			
				
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
			'qSmal': self.qSmal.epsilon,
			'qSmalAcu': sum(self.qSmal.episodeHistory[-100:]),
			'qSmalTime': qSmalTime,
			'qBig': self.qBig.epsilon,
			'qBigAcu': sum(self.qBig.episodeHistory[-100:]),
			'qBigTime': qBigTime,
			'freeFallTime': freeFallTime
			})
		#print( rewardMem[-10:])
		
		
		