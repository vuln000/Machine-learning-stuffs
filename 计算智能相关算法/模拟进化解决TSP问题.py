import pandas as pd
import numpy as np
import matplotlib.pylab as plt
import random
citys = [[1304,2312],[3639,1315],[4177,2244],[3712,1399],[3488,1535],[3326,1556],[3238,1229],[4196,1004],[4312,790],[4386,570],[3007,1970],[2562,1756],[2788,1491],[2381,1676],[1332,695],[3715,1678],[3918,2179],[4061,2370],[3780,2212],[3676,2578],[4029,2838],[4263,2931],[3429,1908],[3507,2367],[3394,2643],[3439,3201],[2935,3240],[3140,3550],[2545,2357],[2778,2826],[2370,2975]]
nums = 100

a = pd.DataFrame(citys)
l = len(citys)
#数据从网上找来的
def review():#展示所有点
	a.plot(x=0,y=1,kind = 'scatter')
	plt.show()
#计算任意两省之间的距离,得到31*31的矩阵
def dist(x1,y1,x2,y2):
	return np.sqrt(np.power(x1-x2,2)+np.power(y1-y2,2))
b = []
a.columns = ['x','y']
[b.append(dist(a.loc[i].x,a.loc[i].y,a.loc[j].x,a.loc[j].y)) for i in range(l) for j in range(l)]
c = np.reshape(b,(l,l))
#c为距离矩阵

###########以上部分复用退火算法中写的代码

def get_random_gene():#随机生成一些路径作为种群基因，显然基因长度为32
	path = list(range(l))[1:31]
	random.shuffle(path)
	path.insert(0,0)
	path.append(0)
	return path
	
def get_random_init():#随机生成num个初始个体作为种群,返回df
	parents = []
	[parents.append(get_random_gene()) for i in range(nums)]
	return pd.DataFrame(parents)
df = get_random_init()
def cal_adaptability(path):#cal_adaptability(list(df.loc[n]))
	sum = 0
	for i in range(31):
		sum = sum+c[path[i],path[i+1]]
	return sum

def poss_for_reproduct(df):##返回归一化的由适应度决定的选择概率以及索引
	adapt_list = []
	[adapt_list.append(cal_adaptability(list(df.loc[i]))) for i in range(nums)]
	te = pd.DataFrame(adapt_list)
	te['ind'] = range(nums)
	sum_ = sum(te[0])
	poss_list = []
	[poss_list.append(te.loc[i][0]/sum_) for i in range(nums)]
	te['poss'] = poss_list
	ma = max(te['poss'])
	mi = min(te['poss'])
	new_poss_list = []
	[new_poss_list.append((te.loc[i]['poss']-mi)/(ma-mi)) for i in range(nums)]
	te['poss'] = new_poss_list
	te['poss'] = 1-te['poss']
	te = te.sort_values('poss',ascending=False)
	return te.reset_index(drop=True)
#te = poss_for_reproduct(df)
def reproduct(te):	#选择进化
	better = 0.1	#凭一定概率前0.01为强者复制，中间保留，后面0.01被复制替换
	counter = better*nums #直到找够前0.01为止
	new = []
	j = 0
	mark = 0
	for i in range(nums):
		if te.loc[i]['poss']>=np.random.random(1)[0]:
			new.append(df.loc[int(te.loc[i]['ind'])])
			new.append(df.loc[int(te.loc[i]['ind'])]) #复制
			j +=1
		else:
			new.append(df.loc[int(te.loc[i]['ind'])]) #保持不变
		if j >= counter:
			mark = i
			break
	for i in range(mark+1,nums-len(new)+mark+1): 
		new.append(df.loc[int(te.loc[i]['ind'])])
	return pd.DataFrame(new).reset_index(drop=True)
	
def hybridize(te):#单点杂交，（控制杂交，使其必然产生新个体）
	father = list(df.loc[int(te.loc[0]['ind'])])
	pos = 0
	for i in range(1,nums):
		if(te.loc[0][0]!=te.loc[i][0]):
			pos = i
			break
	mother = list(df.loc[int(te.loc[pos]['ind'])])
	child_1 = list.copy(father)
	child_2 = list.copy(mother)
	pos_1 = 0
	pos_2 = 0
	#pos_1 = np.random.randint(low=1,high=31,size=1)[0]
	for i in range(31):
		if(father[i]!=mother[i]):
			pos_1=i
			break
	for i in range(31):
		if(child_2[i]==child_1[pos_1]):
			pos_2 = i
			break
#	print(pos_1,pos_2)
#	print(child_1[pos_1],child_2[pos_2])
	temp = []
	child_1[pos_1]=father[pos_2]
	child_1[pos_2]=father[pos_1]
	child_2[pos_1]=mother[pos_2]
	child_2[pos_2]=mother[pos_1]
	temp.append(child_1)
	temp.append(child_2)
	new = pd.DataFrame.copy(df)
	new = new.drop([nums-2,nums-1])
	new.loc[nums-2] = child_1
	new.loc[nums-1] = child_2
	#print('杂交：')
	#print('1',child_1)
	#print('2',child_2)
	return new
def mutate(te):#变异
	p = 0.6	#每个个体变异的概率
	new = pd.DataFrame.copy(df)
	temp = 0 
	num =0 
	for i in range(int(0.2*nums),nums):#取后0.5变异,同时变异概率为0.05
		r = np.random.random(1)[0]
		if(r<=p) :
			ran = np.random.randint(low=1,high=31,size=2)
			ma = max(ran)
			mi = min(ran)
			#print(list(new.loc[te.loc[i]['ind']]))
			temp = new.loc[te.loc[i]['ind']][ma]
			new.loc[te.loc[i]['ind']][ma] = new.loc[te.loc[i]['ind']][mi]
			new.loc[te.loc[i]['ind']][mi] = temp
			num+=1
			#print(list(new.loc[te.loc[i]['ind']]))
	print('mutate times: %d 个' % num)
	return new
def plot(path):##绘制一次路径
	plt.scatter(a['x'],a['y'],color='b')
	x=[]
	y=[]
	for i in range(l+1):
		x.append(citys[path[i]][0])
		y.append(citys[path[i]][1])
	plt.plot(x,y,color='r')
def main():
	global df
	poss_reproduct = 0.1 #繁殖的概率
	poss_hybridize=0.3	 #杂交的概率
	poss_mutate = 0.6	 #变异的概率
	for i in range(100000):
		te = poss_for_reproduct(df)
		r = np.random.random(1)[0]
		if(r<poss_reproduct):
			df = reproduct(te)
			print(1)
		if(poss_reproduct<r<poss_reproduct+poss_hybridize):
			df = hybridize(te)
			print('2')
		if(poss_reproduct+poss_hybridize<r):
			#pass
			df = mutate(te)
			print('3')
		if(i%10==0):
			test =list(df.loc[te.loc[0]['ind']])
			plot(test)
			plt.draw()
			plt.pause(0.01)
			plt.clf()
		print(te.loc[0][0])
		#print(df)
		#print(df.loc[te.loc[0]['ind']])
		test =list(df.loc[te.loc[0]['ind']])
	#print(df.loc[te.loc[0][0]])
main()
#te = poss_for_reproduct(df)
