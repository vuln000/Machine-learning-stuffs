import pandas as pd
import numpy as np
import matplotlib.pylab as plt
import math

citys = [[1304,2312],[3639,1315],[4177,2244],[3712,1399],[3488,1535],[3326,1556],[3238,1229],[4196,1004],[4312,790],[4386,570],[3007,1970],[2562,1756],[2788,1491],[2381,1676],[1332,695],[3715,1678],[3918,2179],[4061,2370],[3780,2212],[3676,2578],[4029,2838],[4263,2931],[3429,1908],[3507,2367],[3394,2643],[3439,3201],[2935,3240],[3140,3550],[2545,2357],[2778,2826],[2370,2975]]
a = pd.DataFrame(citys)
l = len(citys)
#数据从网上找来的
def review():#展示所有点
	a.plot(x=0,y=1,kind = 'scatter')
	plt.show()
#计算任意两省之间的距离,得到31*31的矩阵
def dist(x1,y1,x2,y2):
	return np.sqrt(np.power(x1-x2,2)+np.power(y1-y2,2))
#init
b = []
a.columns = ['x','y']
[b.append(dist(a.loc[i].x,a.loc[i].y,a.loc[j].x,a.loc[j].y)) for i in range(l) for j in range(l)]
c = np.reshape(b,(l,l))
#c为距离矩阵
global path
path = list(range(l))
path.append(0)
#初始路径为0-1-2-3-。。。-30-0
#init#

def alpha(t):
	return t*0.9
def possibilities(t,fi,fj):#计算转移概率
	if fj<fi:
		return 1
	elif(fj==fi):
		return 0
	else:
		return math.exp((fi-fj)/t)
def get_random():
	return np.random.uniform(low=0,high=1,size=1)[0]
def sum_path(path):#计算总路程
	sum = 0
	for i in range(31):
		sum = sum+c[path[i],path[i+1]]
	return sum
def get_new_path(pa):#用二交换法取一条新路
	t = np.random.randint(low=1,high=31,size=2)
	u = min(t)
	v = max(t)
	newpath = list.copy(pa)
	swit = newpath[v]
	newpath[v] =newpath[u]
	newpath[u]=swit
	return newpath

def plot_double(path_org,path_finnal):
	plt.subplot(1,2,1)
	plot(path_org)
	plt.subplot(1,2,2)
	plot(path_finnal)
	#plt.show()
def plot(path):##绘制一次路径
	plt.scatter(a['x'],a['y'],color='b')
	x=[]
	y=[]
	for i in range(l+1):
		x.append(citys[path[i]][0])
		y.append(citys[path[i]][1])
	#print(x)
	#print(y)
	plt.plot(x,y,color='r')
	#plt.show()
print('close the figure windows and program run')
plot(path)
plt.show()
#for i in range(100000):#先测试三次
t = 100
s=0
T = []
while(True):
	flag = False
	for i in range(20000):
		fi = sum_path(path)
		#print(path)
		new_path = get_new_path(path)
		#print(path)
		fj = sum_path(new_path)
		rand = get_random()
		poss = possibilities(t,fi,fj)
	#	print('posssss',poss,t)
		if(rand<poss):
			#print(path,new_path)
			#print(fi,'->',fj,flag,s,poss)
			path = new_path
			flag = True
			#print(fi,'->',fj,flag,t,s,poss)
	t = alpha(t)
	if(flag==False):
		s +=1
		print('no trans at',t,'fi',fi)
	else:
		s=0
	#print(s)
	print(fi,flag,t,s)
	T.append(fi)
	if(s==2):	
		print('s==2 at',t,'fi',fi)
		print(path)
		break

plot(path)
plt.show()