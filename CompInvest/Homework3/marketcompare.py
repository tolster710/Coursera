#script to take two inputs, a values python file and a stock index, and compare 

import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import csv
import sys
import math


days=252
k=math.sqrt(days)

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


#MAIN FUNCTION BELOW
if __name__ == '__main__':
	print 'Number of arguments:', len(sys.argv), 'arguments.'
	print 'Argument List:', str(sys.argv)
	infile=sys.argv[1]
	stock_index=sys.argv[2]
	#get data below
	na_data=np.copy(readcsv(infile))
	na_dates= np.int_(na_data[:,0:3])
	results=np.zeros((2,4))
	results[0]=simulate(dt.datetime(int(na_data[0][0]) , int(na_data[0][1]) , int(na_data[0][2]) ), dt.datetime(int(na_data[len(na_data)-1][0]),int(na_data[len(na_data)-1][1]),int(na_data[len(na_data)-1][2])) , ["$SPX"], [1.0])
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









