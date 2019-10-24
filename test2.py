import pandas as pd
import numpy as np
import statsmodels.api as sm
import scipy.stats as scs
import matplotlib.pyplot as plt
import scipy.optimize as sco
from jqdatasdk import *
auth('13921453366','453366')

num=int(input("请输入股票种类"))

stock=[]

for i in range(num):

    print("请输入第",i+1,"支股票")

    str = input()

    if (str.find('.SZ') != '-1'):

        str = str.replace('.SZ','.XSHE')

    if (str.find('.SH') != '-1'):

        str = str.replace('.SH','.XSHG')

    stock.append(str)

print(stock)

noa = len(stock)

start_date = '2019-01-01'

end_date = '2019-09-01'

df = get_price(stock, start_date, end_date, 'daily',['close'])

data = df['close']

#计算不同证券的均值、协方差
returns = np.log(data / data.shift(1))
print(returns)


#给不同资产随机分配初始权重
weights = np.random.random(noa)

weights /= np.sum(weights)

weights

#投资组合优化1——sharpe最大
def statistics(weights):

    weights = np.array(weights)

    port_returns = np.sum(returns.mean()*weights)*252

    port_variance = np.sqrt(np.dot(weights.T, np.dot(returns.cov()*252,weights)))

    return np.array([port_returns, port_variance, port_returns/port_variance])

#最小化夏普指数的负值
def min_sharpe(weights):

    return -statistics(weights)[2]

#约束是所有参数(权重)的总和为1。
cons = ({'type':'eq', 'fun':lambda x: np.sum(x)-1})

bnds = tuple((0,1) for x in range(noa))

#初始权重使用平均分布。
opts = sco.minimize(min_sharpe, noa*[1./noa,], method = 'SLSQP', bounds = bnds, constraints = cons)

opts

print("sharp最优的权重组合为:")

print(opts['x'].round(3))

#预期收益率、预期波动率、最优夏普指数
print("预期收益率、预期波动率、最优夏普指数为：")

print(statistics(opts['x']).round(3))

#方差最小
def min_variance(weights):

    return statistics(weights)[1]

optv = sco.minimize(min_variance, noa*[1./noa,],method = 'SLSQP', bounds = bnds, constraints = cons)

optv

print("方差最小的情况下权重组合为：")

print(optv['x'].round(3))

#得到的预期收益率、波动率和夏普指数
print("得到的预期收益率、波动率和夏普指数为：")

print(statistics(optv['x']).round(3))


