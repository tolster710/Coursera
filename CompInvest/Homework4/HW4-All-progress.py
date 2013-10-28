import pandas as pd
import numpy as np
import math
import copy
import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkstudy.EventProfiler as ep
import sys
import csv

def find_events(ls_symbols, d_data):
    ''' Finding the event dataframe '''
    df_close = d_data['close']
    ts_market = df_close['SPY']
    print "Finding Events"
    # Creating an empty dataframe
    df_events = copy.deepcopy(df_close)
    df_events = df_events * np.NAN
    # Time stamps for the event range
    ldt_timestamps = df_close.index
    for s_sym in ls_symbols:
        for i in range(1, len(ldt_timestamps)):
            # Calculating the returns for this timestamp
            f_symprice_today = df_close[s_sym].ix[ldt_timestamps[i]]
            f_symprice_yest = df_close[s_sym].ix[ldt_timestamps[i - 1]]
            f_marketprice_today = ts_market.ix[ldt_timestamps[i]]
            f_marketprice_yest = ts_market.ix[ldt_timestamps[i - 1]]
            f_symreturn_today = (f_symprice_today / f_symprice_yest) - 1
            f_marketreturn_today = (f_marketprice_today / f_marketprice_yest) - 1
            '''if f_symreturn_today <= -0.05 and f_marketreturn_today >= 0.05:
                df_events[s_sym].ix[ldt_timestamps[i]] = 1'''
            if f_symprice_today<=5 and f_symprice_yest>5:
            	df_events[s_sym].ix[ldt_timestamps[i]] = 1    
    return df_events


def sharpe(cum_daily, k, stdev):
    return cum_daily*k/(stdev)

def cum_daily_return(array):
    value=[]
    for i in range(len(array)-1, 0, -1):
        value.append(array[i]/array[i-1])
    return value


def simulate(startdate, enddate, symbols, alloc):
    ls_symbols = symbols
    dt_start = startdate
    dt_end = enddate
    print ls_symbols 
    print dt_start 
    print dt_end
    dt_timeofday = dt.timedelta(hours=16)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)
    c_dataobj = da.DataAccess('Yahoo')
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    na_price = d_data['close'].values
    #
    start_price = na_price[0,:]
    #
    #
    na_price_norm = na_price / na_price[0,:]
    #
    na_price_norm_weight = na_price_norm*alloc
    #
    returns=[]
    for j in range(0, len(na_price)):
        returns.append(sum(na_price_norm_weight[j]))
    #
    daily_returns=cum_daily_return(returns)
    stdev=np.std(daily_returns)
    avgdaily_return=np.average(daily_returns)-1
    weight_return=0
    cumreturn=returns[len(returns)-1]
    s_ratio=sharpe(avgdaily_return,k,stdev)
    
    return stdev, avgdaily_return, s_ratio, cumreturn

def output(label,array):
    print label
    print "Volatility :",
    print array[0]
    print "Average Daily return: ",
    print array[1]
    print "Sharpe Ratio: ",
    print array[2]
    print "Cumulative return : ",
    print  array[3]



def readcsv(orderfile):
    reader = csv.reader(open(orderfile,'rU'), delimiter=',')
    csvdata=[]
    for row in reader:
        csvdata.append(row)
    na_data=np.copy(csvdata)
    return na_data

def writeorder(outfile, array):
    with open(outfile,'wb') as csvfile:
        csvwriter= csv.writer(csvfile, delimiter=',')
        for i in array:
            csvwriter.writerow(i)


def create_orders(ls_symbols,df_events):
    # Time stamps for the event range
    ldt_timestamps = df_events.index
    orders=[]
    for s_sym in ls_symbols:
        for i in range(0, len(ldt_timestamps)):
            # Find events and generate orders
            if (df_events[s_sym][i]==1)&(i+5<=len(ldt_timestamps)):
                Data=[ldt_timestamps[i].year, ldt_timestamps[i].month, ldt_timestamps[i].day,s_sym,"BUY",100]
                orders.append(Data)
                Data2=[ldt_timestamps[i+5].year, ldt_timestamps[i+5].month, ldt_timestamps[i+5].day,s_sym,"SELL",100]
                orders.append(Data2)
    return orders


def getsymbols(na_symbols):
    ls_symbols=['ZZZ']
    for row in na_symbols:
        found=0
        for i in ls_symbols:
            if (row==i):
                found=1
        if (found==0):
            ls_symbols.append(row)
    ls_symbols.pop(0)
    return ls_symbols


def getdata(na_dates,ls_symbols):
    dt_start=dt.datetime(na_dates[0,0],na_dates[0,1],na_dates[0,2])
    dt_end=dt.datetime(na_dates[len(na_dates)-1,0],na_dates[len(na_dates)-1,1],na_dates[len(na_dates)-1,2]+1)
    dt_timeofday = dt.timedelta(hours=16)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)
    c_dataobj = da.DataAccess('Yahoo')
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    na_price = d_data['close'].values
    return na_price, ldt_timestamps

def buildportfolio(na_price,ls_symbols,initial_Cash, ldt_timestamps,na_data,na_dates):  
    #Create data arrays
    shares=np.zeros((len(na_price),len(ls_symbols)))    # creates empty array to mirror data
    value=np.zeros((len(na_price),len(ls_symbols))) # creates empty array to mirror data
    cash=np.zeros((len(na_price)))                  #initialized the cash array
    total_value=np.zeros((len(na_price)))       
    cash[0]=initial_Cash

    total_shares=np.zeros((len(ls_symbols)))        # count the total shares    
    orders_executed=0
    for j in range(0,len(na_dates)):
        order_date=dt.date(na_dates[j][0],na_dates[j][1],na_dates[j][2])
        for i in range(0,(len(ldt_timestamps))):
            timedate=ldt_timestamps[i].date()
            if (order_date==timedate):
                index=i
        if (na_data[j][4]=='Buy'):
            price=int(na_data[j][5])*na_price[index][ls_symbols.index(na_data[j][3])]
            shares[index][ls_symbols.index(na_data[j][3])] = shares[index][ls_symbols.index(na_data[j][3])] + int(na_data[j][5])
            total_shares[ls_symbols.index(na_data[j][3])]=total_shares[ls_symbols.index(na_data[j][3])] + int(na_data[j][5])
            cash[index]=cash[index]-price
            orders_executed=orders_executed+1
        if (na_data[j][4]=='Sell'):
            #if (int(na_data[j][5])<=total_shares[ls_symbols.index(na_data[j][3])]):
            if (1==1):
                price=int(na_data[j][5])*na_price[index][ls_symbols.index(na_data[j][3])]
                shares[index][ls_symbols.index(na_data[j][3])] = shares[index][ls_symbols.index(na_data[j][3])]-int(na_data[j][5])
                total_shares[ls_symbols.index(na_data[j][3])]=total_shares[ls_symbols.index(na_data[j][3])] - int(na_data[j][5])
                cash[index]=cash[index]+price   
                orders_executed=orders_executed+1
    #now fill in the share
    for i in range(1,len(cash)):
        if (cash[i]==0):
            cash[i]=cash[i-1]
        else:
            cash[i]=cash[i-1]+cash[i]
        for j in range(0,len(ls_symbols)):  
            if (shares[i][j]==0):
                shares[i][j]=shares[i-1][j]
            else:   
                shares[i][j]=shares[i-1][j]+shares[i][j]
    for i in range(0,len(cash)):
        for j in range(0, len(ls_symbols)):
            value[i][j]=na_price[i][j]*shares[i][j]
        total_value[i]=np.sum(value[i])+cash[i]
    return cash, value, total_value


def writeresults(total_value,ldt_timestamps,outfile):
    with open(outfile,'wb') as csvfile:
        writeout=csv.writer(csvfile, delimiter=',')
        for i in range(0,len(total_value)):
            Data=[ldt_timestamps[i].year, ldt_timestamps[i].month, ldt_timestamps[i].day, total_value[i]]
            writeout.writerow(Data)





if __name__ == '__main__':
    '''def get_data(symlist,filename):'''
    print 'Number of arguments:', len(sys.argv), 'arguments.'
    print 'Argument List:', str(sys.argv)
    days=252
    k=math.sqrt(days)
    initial_Cash=sys.argv[1]
    outfile=sys.argv[2]
    stock_index=sys.argv[3]
    dt_start = dt.datetime(2008, 1, 1)
    dt_end = dt.datetime(2009, 12, 31)
    tempfile='temporders.csv'
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))
    #
    dataobj = da.DataAccess('Yahoo')
    ls_symbols = dataobj.get_symbols_from_list('sp5002012')
    ls_symbols.append('SPY')
    #
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    #
    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)
    #
    df_events = find_events(ls_symbols, d_data)
    print "Dumping to results file"
    returned_orders=create_orders(ls_symbols,df_events)
    writeorder(tempfile,returned_orders)
    #below from hw3
    #Get Data from temporder csv
    na_data=readcsv(tempfile)
    na_symbols = na_data[:,3]
    na_dates= np.int_(na_data[:,0:3])
    ls_symbols=getsymbols(na_symbols)
    na_price,ldt_timestamps=getdata(na_dates,ls_symbols)
    cash, value, total_value=buildportfolio(na_price,ls_symbols,initial_Cash,ldt_timestamps,na_data,na_dates)
    writeresults(total_value,ldt_timestamps,outfile)
    #below from market compare
    na_data=np.copy(readcsv(outfile))
    na_dates= np.int_(na_data[:,0:3])
    results=np.zeros((2,4))
    results[0]=simulate(dt.datetime(int(na_data[0][0]) , int(na_data[0][1]) , int(na_data[0][2]) ), dt.datetime(int(na_data[len(na_data)-1][0]),int(na_data[len(na_data)-1][1]),int(na_data[len(na_data)-1][2])) , [stock_index], [1.0])
    #reading in values
    csv_value=np.float_(na_data[:,3])
    csv_norm=np.zeros((len(na_data)))
    for i in range(0,len(csv_value)):
        csv_norm[i]=csv_value[i]/csv_value[0]
    daily_returns=cum_daily_return(csv_norm)
    stdev=np.std(daily_returns)
    avgdaily_return=np.average(daily_returns)-1
    cumreturn=csv_norm[len(csv_norm)-1]
    s_ratio=sharpe(avgdaily_return,k,stdev)
    results[1]=[stdev,avgdaily_return,s_ratio,cumreturn]
    output("SP500:",results[0])
    output("Simulated portfolio:", results[1])






