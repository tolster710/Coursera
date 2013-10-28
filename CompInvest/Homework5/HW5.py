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



def bollinger_value(price_array, ldt_timestamps, bollinger_date):
	d= {'price': price_array, 'time': ldt_timestamps}
	data=pd.DataFrame(d)
	data['roll_mean']=pd.rolling_mean(data['price'],20)
	data['roll_std']=pd.rolling_std(data['price'],20)
	data['boll_low']=data['roll_mean']-data['roll_std']
	data['boll_high']=data['roll_mean']+data['roll_std']
	data['boll_val']= (data['price']-data['roll_mean']) / data['roll_std']
	result_array=[]
	for i in range(0, len(ldt_timestamps)):
		if data['time'][i]==bollinger_date:
			for j in keys:
				result_array.append(data[j][i])
	return result_array, data





def getdata(dt_start,dt_end,ls_symbols):
    #dt_start=dt.datetime(na_dates[0,0],na_dates[0,1],na_dates[0,2])
    #dt_end=dt.datetime(na_dates[len(na_dates)-1,0],na_dates[len(na_dates)-1,1],na_dates[len(na_dates)-1,2]+1)
    dt_timeofday = dt.timedelta(hours=16)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)
    c_dataobj = da.DataAccess('Yahoo')
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    na_price = d_data['close'].values
    return na_price, ldt_timestamps


def printresults(result_array,keys):
	for i in range(0,len(keys)):
		print str(keys[i]) + " : " + str(result_array[i])



if __name__ == '__main__':
	'''def get_data(symlist,filename):'''
	print 'Number of arguments:', len(sys.argv), 'arguments.'
	print 'Argument List:', str(sys.argv)
	days=252
	k=math.sqrt(days)
	ls_symbols=sys.argv[1]
	lookback=int(sys.argv[2])
	#date1=[]
	#date1.append(sys.argv[3])
	#print date1
	year=int(sys.argv[3])
	month=int(sys.argv[4])
	day=int(sys.argv[5])
	date=dt.datetime(year,month,day)
	dt_start = dt.datetime(2008, 1, 1)
	dt_end = dt.datetime(2010, 12, 31)
	keys= ['time', 'roll_mean', 'roll_std', 'boll_low', 'boll_high', 'boll_val']
	na_price, ldt_timestamps=getdata(dt_start,dt_end,ls_symbols)
	price_array=[]
	for i in range(0, len(na_price)):
		price_array.append(na_price[i][0])
	#d= {'price': price_array, 'time': ldt_timestamps}
	#data-pd.DataFrame(d)
	#price_data=pd.Series(price_array,index=ldt_timestamps)
	#timestamps
	bollinger_date=pd.tslib.Timestamp(dt.datetime(date.year, date.month, date.day, 16))
	result_array, all_data=bollinger_value(price_array, ldt_timestamps, bollinger_date)
	printresults(result_array,keys)







    
