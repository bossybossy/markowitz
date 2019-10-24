import tushare as ts
import datetime
import math
import pandas as pd
import numpy as np
import copy
import matplotlib.pyplot as plt
import matplotlib.dates as md

def dateRange(beginDate, endDate):
    dates = []
    dt = datetime.datetime.strptime(beginDate, "%Y%m%d")
    date = beginDate[:]
    while date <= endDate:
        dates.append(date)
        dt = dt + datetime.timedelta(1)
        date = dt.strftime("%Y%m%d")
    return list(reversed(dates))

#需要调的参数
n=10    #买入和卖出的交易间隔日
s=5    #取前s支股票买入


#读入excel:sort
csvfile = 'sort_18.csv'
sort=pd.read_csv(csvfile,header=None,sep=',')
col_num=sort.columns.size
for i in range(col_num):
    sort.rename(columns={i:sort[i][0]}, inplace=True)
sort=sort.iloc[2:,2:]


#调出每天前s只股票并删去nan
sort=sort.iloc[0:s,0:]
sort_col_num=sort.columns.size
drop_col=[]
for i in range(0,sort_col_num):
    if not isinstance(sort.iloc[0:1,i].values[0],str):
        drop_col.append(sort.columns[i])
sort=sort.drop(columns=drop_col)

#调出每天前s只股票的开盘价(list)
ts.set_token('7557fca71a12f31ff9d79f65ac25fc9f6d288ca51cce05696f6430cc')
pro = ts.pro_api()
code=['ts_code','000670.SZ','002049.SZ','002077.SZ','002079.SZ','002119.SZ','002156.SZ','002185.SZ','002371.SZ','300046.SZ','300053.SZ',
     '300077.SZ','300139.SZ','300223.SZ','300327.SZ','300346.SZ','300373.SZ','300458.SZ','300493.SZ','300613.SZ','300623.SZ',
     '300661.SZ','300666.SZ','300671.SZ','300672.SZ','300706.SZ','300782.SZ','600171.SH','600198.SH','600360.SH','600460.SH',
     '600584.SH','600667.SH','603005.SH','603068.SH','603160.SH','603501.SH','603933.SH','603986.SH','688002.SH','688008.SH',
     '688018.SH','688019.SH','300316.SZ','300724.SZ','300751.SZ','002519.SZ','300250.SZ','300123.SZ','600100.SH','600601.SH',
     '000066.SZ','300369.SZ','002415.SZ']



#只保留交易日的排名
dates=list(sort.columns)
s_date=dates[-1]
e_date=dates[0] 
file=r'index_18.xlsx'
#index_dates 所有上交所的交易日
index_dates=list(pd.read_excel(file).columns)
for k in range(len(index_dates)):
    index_dates[k]=str(index_dates[k])[0:10]
    day=''
    d=index_dates[k]
    for i in range(len(d)):
        if d[i]!='-':
            day=day+d[i]
    index_dates[k]=day
    
save_col=set(index_dates)
all_col=set(sort.columns)
drop_col=all_col.difference(save_col)  #取补集
drop_col=list(drop_col)
#在sort里面去掉非交易日的排名
sort=sort.drop(columns=drop_col)
sort.index=range(len(sort))


trade_dates=list(reversed(index_dates))
len_dates=len(trade_dates)

df_daily_open=[]
for i in range(s):
    list_open=[]
    for t in range(len_dates):
        df_single_open=pro.daily(ts_code=sort.iloc[i:i+1,t].values[0],start_date=trade_dates[t],end_date=trade_dates[t],fields='open')
        if df_single_open.empty:
            list_open.append(np.nan)
        else:
            list_open.append(df_single_open.values[0])
    df_daily_open.append(list_open)



#提取所有交易日所有股票开盘价
df_daily_all_open=[]
df_daily_single_open=pd.DataFrame(trade_dates)
df_daily_single_open=df_daily_single_open.T
for i in range(len(code)-1):
    df_single_open=pro.daily(ts_code=code[i+1],start_date=s_date,end_date=e_date,fields='open')
    df_daily_single_open=pd.concat([df_daily_single_open,df_single_open.T])
daily_single_open=df_daily_single_open.values
daily_single_open=np.insert(daily_single_open,0,values=code,axis=1)
df_daily_all_open=pd.DataFrame(daily_single_open)



for i in range(len_dates+1):
    df_daily_all_open.rename(columns={i:df_daily_all_open[i][0]}, inplace=True)
for i in range(len(code)):
    df_daily_all_open.rename(index={i:code[i]},inplace=True)


df_daily_open_buy=[]
for i in range(s):
    list_daily_open=[]
    for t in range(len_dates-1):
        append_open=df_daily_all_open[trade_dates[t]][sort.iloc[i:i+1,t+1].values[0]]
        list_daily_open.append(append_open)
    df_daily_open_buy.append(list_daily_open)
    
    
df_open_buy_col=trade_dates[0:-1]     #去掉第一个交易日
df_daily_open_buy=pd.DataFrame(df_daily_open_buy,columns=df_open_buy_col)


df_daily_open_sell=[]
for i in range(s):
    list_daily_open=[]
    for t in range(len_dates-n-1):
        append_open=df_daily_all_open[trade_dates[t]][sort.iloc[i:i+1,t+n+1].values[0]]
        list_daily_open.append(append_open)
    df_daily_open_sell.append(list_daily_open)
    
    
df_open_sell_col=trade_dates[0:-n-1]
df_daily_open_sell=pd.DataFrame(df_daily_open_sell,columns=df_open_sell_col)


#提取每隔n天前s支股票的开盘价（参数为n,df_daily_open）
def abstract_open_price_n(n,df_daily_open):
    trade_dates=list(df_daily_open.columns)
    r_trade_dates=list(reversed(trade_dates))
    r_trade_n_dates=[]
    for i in range(0,len(r_trade_dates),n):
        r_trade_n_dates.append(r_trade_dates[i])
    trade_n_dates=list(reversed(r_trade_n_dates))
    drop_dates=list(set(trade_dates).difference(set(trade_n_dates)))
    df_ndays_open=df_daily_open.drop(columns=drop_dates)
    return df_ndays_open

df_ndays_open_buy=abstract_open_price_n(n,df_daily_open_buy)

df_ndays_open_sell=abstract_open_price_n(n,df_daily_open_sell)
    



#计算总交易额（参数为每隔n个交易日买入/卖出的股票dataframe,前s支股票）
def total_price(df,s):
    len_dates=len(df.columns)
    dates=list(df.columns)
    price_list=[]
    for i in range(len_dates):
        day_price_list=list(df[dates[i]])
        for j in range(s-1,-1,-1):
            if math.isnan(day_price_list[j]):
                del day_price_list[j]
        day_price=np.mean(day_price_list)
        price_list.append(day_price)
    df_total_price=pd.DataFrame(price_list,index=dates)
    df_total_price=df_total_price.T
    return df_total_price
        
df_total_buy=total_price(df_ndays_open_buy,s)   
df_total_sell=total_price(df_ndays_open_sell,s)   

    
#计算当日收益 参数为df_total_buy,df_total_sell,返回的是每日收益率的dataframe
def rate(df_total_buy,df_total_sell):
    dates=list(df_total_buy.columns)
    len_dates=len(dates)
    rate_list=[]
    for i in range(len_dates-1):
        rate=(df_total_sell[dates[i]][0]-df_total_buy[dates[i+1]][0])/df_total_buy[dates[i+1]][0]
        rate_list.append(rate)
    dates=list(df_total_sell.columns)
    df_rate=pd.DataFrame(rate_list,index=dates)
    df_rate=df_rate.T
    return df_rate

df_rate=rate(df_total_buy,df_total_sell)

#计算累计收益率(参数为收益率dataframe),返回累计收益率dataframe
def accumulated_returnrate(df_rate):
    rate_list=df_rate.values.tolist()[0]
    r_rate_list=list(reversed(rate_list))
    r_accumulated=[1.0]
    for i in range(len(r_rate_list)-1):
        r_accumulated.append((r_rate_list[i+1]+1)*(r_accumulated[i]))
    accumulated=list(reversed(r_accumulated))
    dates=list(df_rate.columns)
    df_accumulated_rate=pd.DataFrame(accumulated,index=dates)
    df_accumulated_rate=df_accumulated_rate.T
    return df_accumulated_rate

df_accumulated_rate=accumulated_returnrate(df_rate)
df_accumulated_rate_T= df_accumulated_rate.T


accumulated_rate_list=df_accumulated_rate.values.tolist()[0]
l1,=plt.plot(list(range(len(accumulated_rate_list))),list(reversed(accumulated_rate_list)))

file=r'index_18.xlsx'
index_semi=list(pd.read_excel(file).values[0])
index_semi=pd.DataFrame(list(reversed(index_semi))).T
index_semi_n=list(abstract_open_price_n(n,index_semi).values[0])
index_semi_n=pd.DataFrame(list(reversed(index_semi_n))).T
return_index_semi_n=[]
for i in range(len(index_semi_n.columns)-1):
    append_value=index_semi_n[i+1].values[0]/index_semi_n[i].values[0]-1
    return_index_semi_n.append(append_value)
return_index_semi_n=pd.DataFrame(return_index_semi_n).T
accu_return_index_semi=accumulated_returnrate(return_index_semi_n)
accu_return_index_semi=accu_return_index_semi.values[0]
rate=accumulated_rate_list/accu_return_index_semi
l2,=plt.plot(list(range(len(accu_return_index_semi))),list(reversed(accu_return_index_semi)))
l3,=plt.plot(list(range(len(rate))),list(reversed(rate)))
plt.legend(handles=[l1,l2,l3],labels=['Our method','Wind','rate'],loc='upper right')
plt.show()
