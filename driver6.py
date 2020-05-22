
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
# dummy bot turn tu direction off error 

class driver6:
	fps = 30.0
	work = False
	
	episodeLen = fps*60.00
	
	EPISODES = 500000
	SHOW_EVERY = 1000
	epsilon = 0.998
	LEARNING_RATE = 0.1
	DISCOUNT = 0.95
	
	q_table = []
	

	
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
		for episode in range(self.EPISODES):
			if episode >= 1:
				self.episodeNow = episode
				if not episode%100:
					nm = episode*(self.episodeLen/self.fps)/60.0/60.0*self.sim.boat['sog']
					print("episode: %s \texpiriance: %s [nm] memory size [%s]"%(episode,round(nm,2), len(self.q_table[self.qnet])))
					print("res:%s",self.ep_rewards[-1])
				self.itersLeft = self.episodeLen
				self.sim.reset()
				self.qnet = 0
				for n in range(0,10,1):
					self.q_table.append({})
				self.mainLoop()
			
			
			if not (episode+1)%self.SHOW_EVERY:
				_thread.start_new(self.buildPlot,())
			
				
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
		if self.qnetOld == 1:
			ce*=10.0
			gr*=10.0
		tola = int(self.sim.boat['ruderPos'])//5
		divs = []
		
		
		cefoldIn = None
		grfoldIn = None
		tolafoldIn = None
		res = 0.0
		sufix = 0
		base = 40.0

		if ce >= base:
			ce = base
		elif ce <= -base:
			ce = -base
		if gr >= base:
			gr = base
		elif gr <= -base:
			gr = -base
		if tola >= base:
			tola = base
		elif tola <= -base:
			tola = -base
		
		
			
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
		qnetOld = 0
		self.qnetOld = 0
		discrete_state = self.get_discrete_state(b)
		
		while self.itersLeft > 0:
			randomAllowed = False
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
			
			
			
			reward = -1.0
			self.qnet = 0
			
			if len(self.mh) > 5:

				if self.qnet == 0 and m.fabs(b['cogError'])<5.0 and self.directionChangeCount<=3 and m.fabs(b['gRot']) < 0.05:
					reward = -1.0/(movesc+1.0)
					self.qnet = 1
					#self.itersLeft = 0
					print("0in moves ",movesc)
					movesc = 0
					
					
				if self.qnet == 1 and m.fabs(b['cogError'])<0.5 and self.directionChangeCount<=3 and m.fabs(b['gRot']) < 0.01:
					reward = -1.0/(movesc+1.0)
					self.qnet = 2
					print("1in moves ",movesc)
					self.itersLeft = 0
					
				
			
			
			
			
			if random.random() > self.epsilon and randomAllowed:
				keys = list(self.q_table[qnetOld].keys())
				keysLen = len(keys)
				random_discrete_state = keys[random.randint(0,keysLen-1)]
				aa = max(self.q_table[qnetOld][random_discrete_state])
				action = self.q_table[qnetOld][random_discrete_state].index(aa)
				randomDesision = True
				randomDesisionCount+=1
			else:
				self.chkQtable(discrete_state)
				aa = max(self.q_table[qnetOld][discrete_state])
				action = self.q_table[qnetOld][discrete_state].index(aa)


			
			
			self.mh.append(action-1)
			
			if self.qnet != 2:
				self.sim.iter(action-1)
			#print( action-1 )
			if action != actionOld:
				movesc+=1
			
			
			self.discreteHistory.append([discrete_state,0])
			if self.qnet != 2:
				self.discreteHistory[-1][1] = action

		
			
			new_discrete_state = self.get_discrete_state(b)
			
			max_future_q = max(self.q_table[qnetOld][new_discrete_state])
			current_q = self.q_table[qnetOld][discrete_state][int(action)]
			new_q = (1 - self.LEARNING_RATE) * current_q + self.LEARNING_RATE * (reward + self.DISCOUNT * max_future_q)

			
			self.q_table[qnetOld][discrete_state][int(action)] = new_q
			#self.q_table[self.discreteHistory[0][0]][int(self.discreteHistory[0][1])] = new_q
			
			#if self.itersLeft == 1:
			#	print("new_q %s"%new_q)

			rewardMem.append(reward)
			

			discrete_state = new_discrete_state
			actionOld = action
			
			
			offCorseSum+= m.fabs(b['cogError'])
			if self.render and not self.episodeNow%self.SHOW_EVERY:
				self.sim.renderFrame()
				#print('discrete_state',discrete_state,' timeOfLastWork',self.timeOfLastMove)
				#print(reward)
				print("qnet",self.qnet)
				time.sleep(1.00/self.fps)
				if randomDesision:
					print("random desision")
					randomDesision = False
			self.itersLeft-=1
			iterNo+=1
			qnetOld = self.qnet
			self.qnetOld = self.qnet
			self.get_discrete_state(b)
			

		self.ep_rewards.append({
			'offCorseSum': round(offCorseSum,2),
			'reward': reward,
			'onGoal': round(self.goal,3),
			'moves': movesc,
			'off':round(timeOfOff,2),
			'on':round(timeOfWork,2),
			'changes': directionChangeCount,
			'offCourse': offCourse,
			'randDesisions': randomDesisionCount,
			'min': min(rewardMem),
			'max': max(rewardMem),
			'avg': sum(rewardMem)/len(rewardMem),
			'qnet': self.qnet
			})
		#print( self.ep_rewards[-1])
		
		
		