import pandas as pd 
import numpy as np
import matplotlib.pylab as plt
import math
import sys
algo = 0
rang = 0
n=50	#个体的数量
m = 2	#问题的维度
swarm = []	#list of swarm
swarm_bset_id = 0	#最好个体的id
swarm_best_pos = []	#最好个体的位置
swarm_best_fitness = 0	#最好个体的适应值
c1 = 1.2 #学习因子1
c2 = 1.4 #学习因子2
sigma = [] #M个多尺度高斯变异算子方差
standard_deviation = [] #M个多尺度高斯变异算子标准差
M = 10
P = int(n/M) #每个子群个体个数
K = 0  #迭代次数
FitXm = [] #每个子群的适应度值
Td = [] #逃逸点阈值
Vmax = rang	#全局最大速度
G = [] #逃逸次数记录
k1=5
k2=10

def algo_choose(name):
	global algo,rang
	if name == 1:
		print('Tablet Function ')
		algo = 1
		rang = 500
	if name == 2:
		print('Quadratic function')
		m = 1 #二次函数只有一个变量-0.25[1.5]
		algo = 2
		rang = 100
	if name == 3:
		print('Rosenbrock function')
		algo = 3#完美结果0 [1,1,1,1,1,1]
		rang = 5
	if name == 4:
		print('Griewank Function')
		algo = 4#计算精度不够，0 [0,0,0,0,0]
		rang = 600
	if name == 5:
		print('Rastrigin Funtion')
		algo = 5 # 0[0,0,0,0,0]
		rang = 5.12
	if name == 6:
		print('Schaffer\'s F7 Problem')
		algo = 6 # 0[0,0,0,0] 
		rang = 100
	if name == 7:
		print('Generalized Schwefel’s Problem best pos')
		algo = 7
		rang = 500

def cal_fitness(x):
	if algo == 1:
		sum=0
		for i in range(1,m):
			sum = sum + x[i]*x[i]
		return sum+x[0]*x[0]*1000
	if algo == 2:
		sum=0
		a = 1
		b = -3
		c = 2
		return a*x[0]*x[0]+b*x[0]+c
	if algo == 3:
		sum = 0
		for i in range(m-1):
			sum = sum + (100*(x[i+1]-x[i]*x[i])*(x[i+1]-x[i]*x[i])+(x[i]-1)*(x[i]-1))
		return sum
	if algo == 4:
		sum1 = 0
		sum2 = 1
		for i in range(m):
			sum1 = sum1 + x[i]*x[i]/4000
			sum2 = sum2 * math.cos(x[i]/math.sqrt(i+1))
		return sum1-sum2+1
	if algo == 5:
		sum = 0
		for i in range(m):
			sum = sum + x[i]*x[i] -10*math.cos(2*math.pi*x[i]) +10
		return sum
	if algo == 6:
		sum = 0
		normalizer = 1.0/float(len(x)-1)
		for i in range(len(x)-1):
			si = math.sqrt(x[i]**2 + x[i+1]**2)
			sum += (normalizer * math.sqrt(si) * (math.sin(50*si**0.20) + 1))**2
		return sum
	if algo == 7:
		sum=0
		for i in range(m):
			sum= sum - x[i] * math.sin(math.sqrt(abs(x[i])))
		return sum	
class Swarm:
	def __init__(self):
		self.pos = [] 
		self.speed = []
		self.fitness = 0 
		self.best_fitness = 0 
		self.best_pos = []
		for i in range(m):
			self.pos.append(np.random.uniform(-rang, rang))
		for i in range(m):
			#self.speed.append(np.random.uniform(-1,1)*rang/100)#随机初始速度
			self.speed.append(0)#初始速度为0
		self.fitness = cal_fitness(self.pos)
		self.best_fitness = self.fitness
		self.best_pos = list.copy(self.pos)
	def info(self):
		print('pos',self.pos)
		print('speed',self.speed)
		print('fitness',self.fitness)
		print('best_pos',self.best_pos)
	def refresh_memory(self): #每次个体更新适应度及全局最优适应度。
		global swarm_best_fitness,swarm_bset_id,swarm_best_pos 
		self.fitness = cal_fitness(self.pos)
		if(self.fitness<self.best_fitness): #比个体极值好，则更新记忆
			self.best_fitness = self.fitness
			self.best_pos = list.copy(self.pos)
		if(self.fitness<swarm_best_fitness):
			swarm_best_fitness = self.fitness
			swarm_best_pos = list.copy(self.pos)
	def refresh_pos(self):#跟新个体自己的速度和位置,以及适应值

		for i in range(m):
			self.speed[i] = self.speed[i] + c1*np.random.uniform() * (self.best_pos[i]-self.pos[i]) + c2*np.random.uniform()*(swarm_best_pos[i]-self.pos[i])
			next_pos = self.pos[i] + self.speed[i]
			if (-rang<next_pos and next_pos<rang):
				self.pos[i] = next_pos
			else:
				#print('out of range')
				pass
	def escape(self,group):#判断是否可以逃逸################biaozhuncha
		temp1 = list.copy(self.pos)
		temp2 = list.copy(self.pos)
		for i in range(m):
			temp1[i] = temp1[i] + np.random.uniform() * standard_deviation[group]
			temp2[i] = temp2[i] + np.random.uniform()*Vmax
		temp1 = cal_fitness(temp1)
		temp2 = cal_fitness(temp2)
		for i in range(m):
			if (self.speed[i]<Td[i]):
				G[i] = G[i] +1#记录全局逃逸次数
				if(temp1<temp2):
					self.speed[i] = standard_deviation[i]*np.random.uniform()
				else:
					self.speed[i] = np.random.uniform()*Vmax
					G[i] = G[i] +1#记录全局逃逸次数
def update_swarm_best():#找到全局最好的粒子,更新全局最优解和全局极值，写成函数方便切换最大最小
	global swarm_best_fitness,swarm_bset_id,swarm_best_pos 
	for i in range(n):
		if(swarm[i].best_fitness<swarm_best_fitness):
			#print('update at ',i,'best_fitness==',swarm_best_fitness)
			swarm_best_fitness = swarm[i].best_fitness
			swarm_best_pos = list.copy(swarm[i].best_pos)
			swarm_bset_id = i
	return 
def init():
	global swarm_best_fitness
	[swarm.append(Swarm()) for i in range(n)]		#初始化粒子群
	swarm_best_fitness = swarm[0].best_fitness
	#update_swarm_best()
	swarm_best_pos = list.copy(swarm[0].best_pos)
	for i in range(M):
		sigma.append(2*rang)
	for i in range(m):
		Td.append(0.5)
		G.append(0)
	for i in range(M):
		FitXm.append(0)
		standard_deviation.append(0)
		
def sort_swarm():#无法使用排序算法，手写个冒泡
	for i in range(n):
		for j in range(0,n-i-1):
			if(swarm[j].fitness<swarm[j+1].fitness):
				swarm[j],swarm[j+1] = swarm[j+1],swarm[j]
	
def cal_FitXm():	#计算每个子群适应度
	sort_swarm()
	for i in range(M):
		sum = 0
		for j in range(i*P,i*P+P):
			sum = sum + swarm[j].fitness
		FitXm[i]=sum
def cal_standard_deviation():#计算
	FitX_max = max(FitXm)
	FitX_min = min(FitXm)
	for i in range(M):
		standard_deviation[i] = sigma[i]*math.exp(((M*FitXm[i])-(sum(FitXm)))/(FitX_max-FitX_min))
		while(standard_deviation[i]>rang/2): #对标准差加以限制
			standard_deviation[i] = abs(rang/2 - standard_deviation[i])
def update_Td():
	for i in range(m):
		if(G[i]>k1):
			G[i] = 0
			Td[i] = Td[i]/2
def main(a):
	K = 0 #循环次数控制
	algo_choose(a)
	init()
	fit_list = []
	temp = 0
	while(True):
		for i in range(n):
			swarm[i].refresh_memory()
		for i in range(n):
			swarm[i].refresh_pos()
		cal_FitXm()
		cal_standard_deviation()
		for i in range(n):
			group = int(i/(n/M))
			#print(group)
			swarm[i].escape(group)
		update_Td()
		print(swarm_best_fitness,swarm_best_pos)
		#if (#精度控制条件#): 
		#	break			#到达一定精度退出程序
		fit_list.append(swarm_best_fitness)
		plt.plot(fit_list)
		plt.draw()
		plt.pause(0.01)
		plt.clf()
		K = K+1
		temp = swarm_best_fitness
		if K==100:	#到达一定次数退出程序
			break;
main(sys.argv[1]) 