
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

class driver4:
	fps = 30.0
	work = False
	
	episodeLen = fps*60.00
	
	EPISODES = 500000
	SHOW_EVERY = 1000
	epsilon = 0.998
	LEARNING_RATE = 0.1
	DISCOUNT = 0.95
	
	q_table = {}
	

	
	def __init__(self, simEng):
		self.sim = simEng
	
	
	def run(self,render = True):
		
		self.render = render
		self.work = True
		self.gRotExp = 0.0
		
		self.ep_rewards = []
		
		_thread.start_new(self.startIt,())
		
	def startIt(self):
		for episode in range(self.EPISODES):
			if episode >= 1:
				self.episodeNow = episode
				if not episode%100:
					nm = episode*(self.episodeLen/self.fps)/60.0/60.0*self.sim.boat['sog']
					print("episode: %s \texpiriance: %s [nm] memory size [%s]"%(episode,round(nm,2), len(self.q_table)))
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
		for i in r:
			onGoal.append(i['onGoal'])
			moves.append(i['moves'])
			on.append(i['on'])
			off.append(i['off'])
			offCorse.append(int(i['offCourse']))
		try:
			plt.plot(onGoal,label="onGoal")
			plt.plot(moves, label="moves")
			plt.plot(on, label="on")
			plt.plot(off, label="off")
			plt.plot(offCorse, label="offCourse")
			plt.legend(loc=1)
			plt.show()
		except:
			pass
		
	def get_discrete_state(self,b):
		ce = b['cogError']
		gr = self.sim.boat['gRot']*100.00
		divs = []
		
		
		cefoldIn = None
		grfoldIn = None
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
		
			
		divsCount = 20
		if ce < -(base*0.5) and ce >=-base:
			cefoldIn = divsCount
		if gr < -(base*0.5) and gr >=-base:
			grfoldIn = divsCount
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
					
			else:
				res = -divs[sufix-1]
				divs.append(res)
				sufix-=1
				#print(res,resOld)
				if res <= ce and ce <= resOld:
					cefoldIn = d
				if res <= gr and gr <= resOld:
					grfoldIn = d
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
		
		n = "%s_%s"%(cefoldIn,grfoldIn)
		
		try:
			self.q_table[n] 
		except:
			print("making new entry to qtable %s"%n)
			new = [-random.random(),-random.random(),-random.random()]
			self.q_table[n] = new 
		
		return n 
		
		
	def mainLoop(self):
		s = self.sim
		b = s.boat
		offCorseSum = 0.0
		self.gRotExp = random.random()
		movesc = 0
		offCourse = False 
		
		discrete_state = self.get_discrete_state(b)
		
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
		while self.itersLeft > 0:
			randomAllowed = True
			try:
				self.directionChangeCount = 0
				self.timeOfWork = 0.0
				self.timeOfOff = 0.0
				
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
						if d != 0:
							self.timeOfWork+=1.0/self.fps
						if d == 0:
							self.timeOfOff+=1.0 / self.fps
							
						dirOld = d
						
				if not iterNo % ( 2.0*self.fps ):
					timeOfOff+= self.timeOfOff
					timeOfWork+= self.timeOfWork
					directionChangeCount+= self.directionChangeCount
			except:
				pass
			
			
			
			reward = -0.9
			if action == 1:
				reward = -0.89
				
			#if (b['cogError']<0.0 and b['gRot']>0.0 and action == 2 and b['ruderPos'] > 0.0) or \
			#	(b['cogError']>0.0 and b['gRot']<0.0 and action == 0 and b['ruderPos'] < 0.0 ): 
			#	reward = -1.0
			
			
			
			if iterNo>2:
				
						
				if m.fabs(b['cogError']%360.0) < 5.0 and m.fabs(b['gRot']) <= 0.005 :
					reward = -0.2 + (m.fabs(b['cogError']%360.0))
					self.goal+= 0.3/(self.fps)
						
				elif m.fabs((b['cogError']%360.0)) < 0.5  and self.directionChangeCount == 0 and self.sim.boat['gRot'] == 0.0:
						reward = 0.0
						self.goal+= 1.0/(self.fps)
						randomAllowed = False
				
				elif m.fabs((b['cogError']%360.0)) < 0.5  and self.sim.boat['gRot'] == 0.0:
						reward = -0.1
						self.goal+= 0.5/(self.fps)
						
				
				#if int(b['cogError']%360.0) != 0 and m.fabs(b['cogError'])>2.0:
				#	reward+=(m.fabs(b['cogError'])*b['cogError'])*10.0
				#if int(self.sim.xte) == 0:
				#	reward+= 0.05 
				#if self.timeOfOff>self.timeOfWork:
				#	reward+=0.1
				elif b['cogError'] > 5.0 or b['cogError'] < -5.0:
					reward = -0.6
				elif b['cogError'] > 15.0 or b['cogError'] < -15.0:
					reward = -0.7
				elif b['cogError'] > 25.0 or b['cogError'] < -25.0:
					reward = -0.8
				elif b['cogError'] > 35.0 or b['cogError'] < -35.0:
					reward = -0.9
				if b['cogError'] > 45.0 or b['cogError'] < -45.0:
					reward = -1.0
					self.itersLeft = 0	
					offCourse = True
				
				if self.directionChangeCount == 0:
					reward+=0.05
				if self.timeOfOff > self.timeOfWork:
					reward+=0.05
				
					
			
			
			if random.random() > self.epsilon and randomAllowed:
				keys = list(self.q_table.keys())
				keysLen = len(keys)
				random_discrete_state = keys[random.randint(0,keysLen-1)]
				aa = max(self.q_table[random_discrete_state])
				action = self.q_table[random_discrete_state].index(aa)
				randomDesision = True
				randomDesisionCount+=1
			else:
				aa = max(self.q_table[discrete_state])
				action = self.q_table[discrete_state].index(aa)
			
			
			self.mh.append(action-1)
			
			self.sim.iter(action-1)
			#print( action-1 )
			if action != actionOld:
				movesc+=1
			
			
			self.discreteHistory.append([discrete_state,0])
			self.discreteHistory[-1][1] = action
		
			
			new_discrete_state = self.get_discrete_state(b)
			
			max_future_q = max(self.q_table[new_discrete_state])
			current_q = self.q_table[discrete_state][int(action)]
			new_q = (1 - self.LEARNING_RATE) * current_q + self.LEARNING_RATE * (reward + self.DISCOUNT * max_future_q)

			self.q_table[discrete_state][int(action)] = new_q
			#self.q_table[self.discreteHistory[0][0]][int(self.discreteHistory[0][1])] = new_q
			
			#if self.itersLeft == 1:
			#	print("new_q %s"%new_q)


			discrete_state = new_discrete_state
			actionOld = action
			
			offCorseSum+= m.fabs(b['cogError'])
			if self.render and not self.episodeNow%self.SHOW_EVERY:
				self.sim.renderFrame()
				print(discrete_state)
				time.sleep(1.00/self.fps)
				if randomDesision:
					print("random desision")
					randomDesision = False
			self.itersLeft-=1
			iterNo+=1
			
		self.ep_rewards.append({
			'offCorseSum': round(offCorseSum,2),
			'reward': reward,
			'onGoal': round(self.goal,3),
			'moves': movesc,
			'off':round(timeOfOff,2),
			'on':round(timeOfWork,2),
			'changes': directionChangeCount,
			'offCourse': offCourse,
			'randDesisions': randomDesisionCount
			})
		#print( self.ep_rewards[-1])
		
		
		