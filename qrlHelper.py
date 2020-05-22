
import random

class qrlHelper:
	
	def __init__(self,name):
		self.name = name
		self.discrete_stats_reset()
		self.discStatCounter = 0
	
	def initIt(self, epsilon=0.005, learnig_rate=0.1, discount=0.95):
		self.epsilon = epsilon
		self.learnig_rate = learnig_rate
		self.discount = discount
		self.q_table = {}
		self.discrete_state = None
		self.updateq = False
		self.randomMoves = True
		self.rewardHistory = []
		self.episodeHistory = []
		self.rewardStep = 10.0
		self.gRotHistory = []
		print("init")

	def reset(self):
		self.discrete_state = None
		
		
	def startEpisode(self):
		self.rewardHistory = []
		self.gRotHistory = []
		self.actionHistory = []
		self.itersCount = 0
		self.startAtCog = "-"
	
	def endEpisode(self):
		#self.displayIter+=1
		#if not self.displayIter % self.displayDebugEvery:
		#	print("%s end episode sum in episode"%self.name,sum(self.episodeHistory),
		#		" res last 100 ",(sum(self.episodeHistory[-100:])/100.00) )
		if len(self.rewardHistory)>2:
			self.episodeHistory.append(self.rewardHistory[-1])
		self.rewardHistory = []
		
		if self.randomMoves and len(self.episodeHistory) > 100:
			s = sum(self.episodeHistory[-100:])
			if s > -self.rewardStep:
				#print("network traind disable random Moves")
				#self.randomMoves = False
				self.epsilon/=1.01
				#self.rewardStep/=1.01
				self.episodeHistory = []
	
		self.gRotHistory = []
		self.actionHistory = []
		self.startAtCog = "-"
	
	def iter(self,data,myCallBack):
		self.itersCount+= 1
		self.gRotHistory.append(data['gRot'])
		
		
		reward = -1.0
		if self.discrete_state == None:
			self.discrete_state = self.get_discrete_state(data)
			self.updateq = False
		else:
			self.updateq = True
			randomAllowed = True
			reward = self.get_reward(data)
			self.rewardHistory.append(reward)
			if reward == 0.0:
				randomAllowed = False

			if random.random() < self.epsilon and randomAllowed and self.randomMoves:
				keys = list(self.q_table.keys())
				keysLen = len(keys)
				random_discrete_state = keys[random.randint(0,keysLen-1)]
				aa = max(self.q_table[random_discrete_state])
				action = self.q_table[random_discrete_state].index(aa)
				randomDesision = True
			else:
				aa = max(self.q_table[self.discrete_state])
				action = self.q_table[self.discrete_state].index(aa)

			self.actionHistory.append(action-1)
			myCallBack(action-1)

			new_discrete_state = self.get_discrete_state(data)

			max_future_q = max(self.q_table[new_discrete_state])
			current_q = self.q_table[self.discrete_state][int(action)]
			new_q = (1 - self.learnig_rate) * current_q + self.learnig_rate * (reward + self.discount * max_future_q)

			if self.updateq:
				self.q_table[self.discrete_state][int(action)] = new_q
			self.discrete_state = new_discrete_state


		return reward

	def discrete_stats_reset(self):
		self.discStat = {}

	def discrete_stats_used(self,key):
		try:
			self.discStat[key]
		except:
			self.discStat[key] = 0
		self.discStat[key]+=1

		self.discStatCounter+=1
		#if not self.discStatCounter % 1000:
			#print("discread statistics ----",self.name,"--------")
			#print(self.discStat)

		
	def chkHowManyContinuesWorkInAction(self):
		oldAct = None
		movesC = 0
		for a in self.actionHistory:
			if oldAct == None:
				oldAct = a
				
			if oldAct != a and a != 0:
				movesC +=1 
			
			
			oldAct = a
		
		return movesC

	def get_reward(self,data):
		pass

	def get_discrete_state(self,data):
		pass

