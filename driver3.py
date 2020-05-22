
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

class driver3:
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
					print("episode: %s \texpiriance: %s [nm]"%(episode,round(nm,2)))
					print("res:%s",self.ep_rewards[-1])
				self.itersLeft = self.episodeLen
				self.sim.reset()
				self.mainLoop()
			
			
			if not episode%10000:
				r = self.ep_rewards
				try:
					plt.plot(r['moves'])
					plt.plot(r['onGoal'])
					plt.show()
				except:
					pass
		
	def get_discrete_state(self,b):
		ce = b['cogError']
		r = 15.00
		if ce >= r:
			ce = r
		elif ce<=-r:
			ce = -r
				
			
		rudder = int(self.sim.boat['ruderPos'])/2
		
		n = "%s_%s"%(round(m.atan(ce),1),int(rudder))
		
		try:
			self.q_table[n] 
		except:
			print("making new entry to qtable %s"%n)
			new = [random.random(),random.random(),random.random()]
			self.q_table[n] = new 
		
		return n 
		
		
	def mainLoop(self):
		s = self.sim
		b = s.boat
		offCorseSum = 0.0
		self.gRotExp = random.random()
		movesc = 0
		
		discrete_state = self.get_discrete_state(b)
		
		action = 0
		actionOld = 0
		self.mh = []
		self.discreteHistory = []
		self.goal = 0.0
		iterNo = 0
		while self.itersLeft > 0:
			try:
				self.directionChangeCount = 0
				self.timeOfWork = 0.0
				self.timeOfOff = 0.0
				
				dirOld = None
				if len(self.mh)>(2.0*self.fps):
					self.mh.pop()
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
			except:
				pass
			
			
			
			reward = -0.9
			
				
			#if (b['cogError']<0.0 and b['gRot']>0.0 and action == 2 and b['ruderPos'] > 0.0) or \
			#	(b['cogError']>0.0 and b['gRot']<0.0 and action == 0 and b['ruderPos'] < 0.0 ): 
			#	reward = -1.0
			
			
			
			if iterNo>2:
				rewarCogError = m.fabs(b['cogError']%360.0)
				if rewarCogError < 6.0:
						reward = -0.3 - ( rewarCogError/3.0 )
						self.goal+= 1.0/(self.fps*2.0)
				
				if int(b['cogError']%360.0) == 0 and action == 1 and int(self.sim.boat['gRot']) == 0:
						reward = -0.3
						self.goal+= 1.0/(self.fps*2.0)
				if (b['cogError']%360.0) == 0.0 and action == 1 and self.sim.boat['gRot'] == 0.0:
						reward = -0.1
						self.goal+= 1.0/(self.fps)
				if (b['cogError']%360.0) == 0.0 and action == 1 and self.directionChangeCount == 0 and self.sim.boat['gRot'] == 0.0:
						reward = 0.0
						self.goal+= 1.0/(self.fps)
				#if int(b['cogError']%360.0) != 0 and m.fabs(b['cogError'])>2.0:
				#	reward+=(m.fabs(b['cogError'])*b['cogError'])*10.0
				#if int(self.sim.xte) == 0:
				#	reward+= 0.05 
				#if self.timeOfOff>self.timeOfWork:
				#	reward+=0.1
				if b['cogError'] > 2.0 or b['cogError'] < -2.0:
					reward = -0.6
				if b['cogError'] > 15.0 or b['cogError'] < -15.0:
					reward = -0.7
				if b['cogError'] > 25.0 or b['cogError'] < -25.0:
					reward = -0.8
				if b['cogError'] > 35.0 or b['cogError'] < -35.0:
					reward = -0.9
				if b['cogError'] > 45.0 or b['cogError'] < -45.0:
					reward = -1.0
					self.itersLeft = 0	
				
				
				
					
			
			
			if random.random() > self.epsilon:
				keys = list(self.q_table.keys())
				keysLen = len(keys)
				random_discrete_state = keys[random.randint(0,keysLen-1)]
				aa = max(self.q_table[random_discrete_state])
				action = self.q_table[random_discrete_state].index(aa)
				
			else:
				aa = max(self.q_table[discrete_state])
				action = self.q_table[discrete_state].index(aa)
			
			
			self.mh.append(action)
			
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
				time.sleep(1.00/self.fps)
			
			self.itersLeft-=1
			iterNo+=1
			
		self.ep_rewards.append({
			'offCorseSum': round(offCorseSum,2),
			'reward': reward,
			'onGoal': round(self.goal,3),
			'moves': movesc,
			'off':round(self.timeOfOff,2),
			'on':round(self.timeOfWork,2),
			'changes': self.directionChangeCount
			})
		#print( self.ep_rewards[-1])
		
		
		