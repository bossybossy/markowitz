import tushare as ts
import pandas as pd
import numpy as np
import datetime
import copy



def dateRange(beginDate, endDate):
    dates = []
    dt = datetime.datetime.strptime(beginDate, "%Y%m%d")
    date = beginDate[:]
    while date <= endDate:
        dates.append(date)
        dt = dt + datetime.timedelta(1)
        date = dt.strftime("%Y%m%d")
    return list(reversed(dates))

def multiply(a,b):
    #a,b两个列表的数据一一对应相乘之后求和
    sum_ab=0.0
    for i in range(len(a)):
        temp=a[i]*b[i]
        sum_ab +=temp
    return sum_ab

def cal_pearson(x,y):
    n=len(x)
    #求x_list、y_list元素之和
    sum_x=sum(x)
    sum_y=sum(y)
    #求x_list、y_list元素乘积之和
    sum_xy=multiply(x,y)
    #求x_list、y_list的平方和
    sum_x2 = sum([pow(i,2) for i in x])
    sum_y2 = sum([pow(j,2) for j in y])
    molecular=n*sum_xy-(float(sum_x)*float(sum_y))
    #计算Pearson相关系数，molecular为分子，denominator为分母
    denominator=np.sqrt(abs((n*sum_x2-float(sum_x**2))*(n*sum_y2-float(sum_y**2))))
    if abs(denominator)<=0.001:
        return 1
    else:
        return molecular/denominator

ts.set_token('869203382d224ae2699e7ad6949f1325bbb52a1ec323504fe3d58b03')
pro = ts.pro_api()


code=['ts_code','000670.SZ','002049.SZ','002077.SZ','002079.SZ','002119.SZ','002156.SZ','002185.SZ','002371.SZ','300046.SZ','300053.SZ',
     '300077.SZ','300139.SZ','300223.SZ','300327.SZ','300346.SZ','300373.SZ','300458.SZ','300493.SZ','300613.SZ','300623.SZ',
     '300661.SZ','300666.SZ','300671.SZ','300672.SZ','300706.SZ','300782.SZ','600171.SH','600198.SH','600360.SH','600460.SH',
     '600584.SH','600667.SH','603005.SH','603068.SH','603160.SH','603501.SH','603933.SH','603986.SH','688002.SH','688008.SH',
     '688018.SH','688019.SH','300316.SZ','300724.SZ','300751.SZ','002519.SZ','300250.SZ','300123.SZ','600100.SH','600601.SH',
     '000066.SZ','300369.SZ','002415.SZ']


lenstock=len(code)-1
#tushare中不同模块需要的指标
daily_index=['vol','pct_chg']#日线行情指标（成交量，涨跌幅）
daily_basic_index=['total_mv','pb','ps_ttm','turnover_rate']#每日指标
fina_indicator_index=['roe','roa']

#生成一个全为nan的dataframe
s_date="20180101"
e_date="20190812"
dates=dateRange(s_date, e_date)
len_dates=len(dates)
df_daily_copy=pd.DataFrame(dates).T
nan_list=[]
for i in range(len(df_daily_copy)):
    nan_list.append(np.nan)
df_nan=pd.DataFrame(nan_list).T
for i in range(lenstock):
    df_daily_copy=pd.concat([df_daily_copy,df_nan])
    
daily=df_daily_copy.values
daily=np.insert(daily,0,values=code,axis=1)
df_daily_copy=pd.DataFrame(daily)
#变列号为时间
col_num=df_daily_copy.columns.size
for i in range(col_num):
    df_daily_copy.rename(columns={i:df_daily_copy[i][0]}, inplace=True)
    
#存储所有股票的所有指标，每个指标一个dataframe
data_list=[]

#提取数据存入df_daily,再加入data_list
for j in range(len(daily_index)):
    df_daily=copy.deepcopy(df_daily_copy)
    for i in range(lenstock):
        df_trade_date = pro.daily(ts_code=code[i+1], start_date=s_date, end_date=e_date,fields='trade_date')
        df_single = pro.daily(ts_code=code[i+1], start_date=s_date, end_date=e_date,fields=daily_index[j])
        trade_date=df_trade_date.values.tolist()
        single=df_single.values.tolist()
        for k in range(len(trade_date)):
            df_daily[trade_date[k][0]][i+1]=single[k][0]
        for k in range(1,len_dates):
            reversed_dates=list(reversed(dates))
            if np.isnan(df_daily[reversed_dates[k]][i+1]):
                df_daily[reversed_dates[k]][i+1]=df_daily[reversed_dates[k-1]][i+1]
    data_list.append(df_daily)
    
    
#提取数据存入df_daily_basic,再加入data_list
for j in range(len(daily_basic_index)):
    df_daily_basic=copy.deepcopy(df_daily_copy)
    for i in range(lenstock):
        df_trade_date = pro.daily(ts_code=code[i+1], start_date=s_date, end_date=e_date,fields='trade_date')
        df_single = pro.daily_basic(ts_code=code[i+1], start_date=s_date, end_date=e_date,fields=daily_basic_index[j])
        trade_date=df_trade_date.values.tolist()
        single=df_single.values.tolist()
        for k in range(len(trade_date)):
            df_daily_basic[trade_date[k][0]][i+1]=single[k][0]
        for k in range(1,len_dates):
            reversed_dates=list(reversed(dates))
            if np.isnan(df_daily_basic[reversed_dates[k]][i+1]):
                df_daily_basic[reversed_dates[k]][i+1]=df_daily_basic[reversed_dates[k-1]][i+1]
    data_list.append(df_daily_basic)
    

#提取数据存入df_fina_indicator,再加入data_list
for j in range(len(fina_indicator_index)):
    df_fina_indicator=copy.deepcopy(df_daily_copy)
    for i in range(lenstock):
       
        alinfo = pro.query('fina_indicator',ts_code=code[i+1], start_date=s_date, end_date=e_date)
        end_date=list(alinfo['end_date'])
        single=list(alinfo[fina_indicator_index[j]])
        
        for k in range(len(end_date)):
            df_fina_indicator[end_date[k]][i+1]=single[k]
        for k in range(1,len_dates):
            reversed_dates=list(reversed(dates))
            if np.isnan(df_fina_indicator[reversed_dates[k]][i+1]):
                df_fina_indicator[reversed_dates[k]][i+1]=df_fina_indicator[reversed_dates[k-1]][i+1]
                
    data_list.append(df_fina_indicator)







#计算离散度
lag=20#使用前20个交易日的数据
std_df_list=[]#保存每个指标的标准差
for j in range(len(data_list)):
    df_std=data_list[j].iloc[0:1,1:data_list[0].columns.size-lag+1]
    df_std.columns = range(0,df_std.columns.size)
    for i in range(lenstock):
        std_list=[]
        for k in range(data_list[0].columns.size-lag):
           temp=data_list[j].iloc[i+1:i+2,k+1:k+lag+1].values.tolist()
           std_list.append(np.var(temp))
        df_std=pd.concat([df_std,pd.DataFrame(std_list).T])
    std=df_std.values
    std=np.insert(std,0,values=code,axis=1)
    df_std=pd.DataFrame(std)
    #变列号为时间
    std_col_num=df_std.columns.size
    for l in range(std_col_num):
        df_std.rename(columns={l:df_std[l][0]}, inplace=True)
    
    std_df_list.append(df_std[:])


#标准差标准化到[0,1]
new_std_df_list=[]
for j in range(len(std_df_list)):
    new_df_std=std_df_list[j].iloc[0:1,1:std_df_list[0].columns.size]
    new_df_std.columns=range(0,new_df_std.columns.size)
    for i in range(lenstock):
        new_std_list=[]
        find_std_list=std_df_list[j].iloc[i+1:i+2,1:std_df_list[0].columns.size].values.tolist()[0]
        min_std=min(find_std_list)
        max_std=max(find_std_list)
        for k in range(len(find_std_list)):
            try:
                y=1/(max_std-min_std)*find_std_list[k]-(min_std)/(max_std-min_std)
            except ZeroDivisionError:
                y=0.5   #标准化为多少合理？
            new_std_list.append(y)
        new_df_std=pd.concat([new_df_std,pd.DataFrame(new_std_list).T])
    new_std=new_df_std.values
    new_std=np.insert(new_std,0,values=code,axis=1)
    new_df_std=pd.DataFrame(new_std)
    
    new_std_col_num=new_df_std.columns.size
    for i in range(new_std_col_num):
        new_df_std.rename(columns={i:new_df_std[i][0]}, inplace=True)
    
        
    new_std_df_list.append(new_df_std[:])
        
         

    
#计算pearson
lag=20#使用前20个交易日的数据
pearson_df_list=[]#保存每个指标的pearson
for j in range(len(data_list)):
    df_pearson=data_list[j].iloc[0:1,1:data_list[0].columns.size-lag+1]
    df_pearson.columns = range(0,df_pearson.columns.size)
    for i in range(lenstock):
        pearson_list=[]   #储存每一行的Pearson的值
        for k in range(data_list[0].columns.size-lag-1):
           x=data_list[j].iloc[i+1:i+2,k+1:k+lag+1].values.tolist()
           y=data_list[j].iloc[i+1:i+2,k+2:k+lag+2].values.tolist()
           P=abs(cal_pearson(x[0], y[0]))
           
           pearson_list.append(P)
       
        
        df_pearson=pd.concat([df_pearson,pd.DataFrame(pearson_list).T])
    pearson=df_pearson.values
    pearson=np.insert(pearson,0,values=code,axis=1)
    df_pearson=pd.DataFrame(pearson)
    #变列号为时间
    pearson_col_num=df_pearson.columns.size
    for l in range(pearson_col_num):
        df_pearson.rename(columns={l:df_pearson[l][0]}, inplace=True)
        
    pearson_df_list.append(df_pearson[:])


weight_df_list=[]   #保存每个指标的权重
n=len(data_list)    #一共有n个指标
for j in range(n):
    df_weight=pearson_df_list[j].iloc[0:1,1:pearson_df_list[j].columns.size]
    df_weight.columns = range(0,df_weight.columns.size)
    for i in range(lenstock):
        weight_list=[]   #存储每一行的权重
        for k in range(pearson_df_list[j].columns.size-1):
            al=0
            for l in range(n):
                al+=new_std_df_list[l][dates[k]][i+1]+pearson_df_list[l][dates[k]][i+1]
            weightk=(new_std_df_list[j][dates[k]][i+1]+pearson_df_list[j][dates[k]][i+1])/al
            weight_list.append(weightk)
        
        df_weight=pd.concat([df_weight,pd.DataFrame(weight_list).T])
    weight=df_weight.values
    weight=np.insert(weight,0,values=code,axis=1)
    df_weight=pd.DataFrame(weight)
    #变列号为时间
    weight_col_num=df_weight.columns.size
    for l in range(weight_col_num):
        df_weight.rename(columns={l:df_weight[l][0]}, inplace=True)
        
    weight_df_list.append(df_weight[:])


#截面标准化
new_data_df_list=[]
for j in range(len(data_list)):
    df_new_data=data_list[j].iloc[0:lenstock+1,0]
    for k in range(data_list[0].columns.size-1):
        new_data_list=data_list[j].iloc[0:1,k+1].values.tolist()
        for i in range(lenstock):
            new_data_list.append(data_list[j][new_data_list[0]][i+1])
        nonan_new_data_list=np.array(new_data_list[1:])
        nonan_new_data_list=nonan_new_data_list[~np.isnan(nonan_new_data_list)].tolist()
        new_data_mean=np.mean(nonan_new_data_list)
        new_data_std=np.sqrt(np.var(nonan_new_data_list))
        for i in range(lenstock):
            new_data_list[i+1]=(new_data_list[i+1]-new_data_mean)/new_data_std
        df_new_data=pd.concat([df_new_data,pd.DataFrame(new_data_list)],axis=1)
        #变列号为时间
        df_new_data.columns = range(0,df_new_data.columns.size)
        col_num=df_new_data.columns.size
        for i in range(col_num):
            df_new_data.rename(columns={i:df_new_data[i][0]}, inplace=True)
    new_data_df_list.append(df_new_data[:])

#计算总得分
df_score=new_data_df_list[0].iloc[0:lenstock+1,0]
for k in range(weight_df_list[0].columns.size-1):
    score_list=weight_df_list[0].iloc[0:1,k+1].values.tolist()
    for i in range(lenstock):
        total_score=0
        for j in range(len(weight_df_list)):
            total_score=total_score+new_data_df_list[j][score_list[0]][i+1]*weight_df_list[j][score_list[0]][i+1]
        score_list.append(total_score)
    df_score=pd.concat([df_score,pd.DataFrame(score_list)],axis=1)
    #变列号为时间
    df_score.columns = range(0,df_score.columns.size)
    col_num=df_score.columns.size
    for i in range(col_num):
        df_score.rename(columns={i:df_score[i][0]}, inplace=True)        

#排序
df_sort_code=df_score.iloc[0:lenstock+1,0]
for k in range(df_score.columns.size-1):
    sort_list=df_score.iloc[1:lenstock+1,k+1].values.tolist()
    index_list=sorted(range(len(sort_list)), key=lambda t: sort_list[t])
    list.sort(sort_list)
    nan_num=0
    nonan_index_list=[]
    for t in range(len(sort_list)):
        if sort_list[t]!=sort_list[t]:
            nan_num=nan_num+1
        else:
            nonan_index_list.append(index_list[t])
    sort_code_list=df_score.iloc[0:1,k+1].values.tolist()
    for t in range(len(nonan_index_list)):
        sort_code_list.append(df_score['ts_code'][nonan_index_list[len(nonan_index_list)-t-1]+1])
    df_sort_code=pd.concat([df_sort_code,pd.DataFrame(sort_code_list)],axis=1)
#编列号为时间
df_sort_code.columns = range(0,df_sort_code.columns.size)
col_num=df_sort_code.columns.size
for i in range(col_num):
    df_sort_code.rename(columns={i:df_sort_code[i][0]}, inplace=True)





