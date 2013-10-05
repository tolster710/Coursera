#importing all libraries
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import csv
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da
import math as math
import sys


def readcsv(orderfile):
	reader = csv.reader(open(orderfile,'rU'), delimiter=',')
	csvdata=[]
	for row in reader:
		csvdata.append(row)

	na_data=np.copy(csvdata)
	return na_data



	
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
	shares=np.zeros((len(na_price),len(ls_symbols)))	# creates empty array to mirror data
	value=np.zeros((len(na_price),len(ls_symbols)))	# creates empty array to mirror data
	cash=np.zeros((len(na_price)))					#initialized the cash array
	total_value=np.zeros((len(na_price)))		
	cash[0]=initial_Cash

	total_shares=np.zeros((len(ls_symbols)))		# count the total shares	
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



#MAIN FUNCTION BELOW
if __name__ == '__main__':
	print 'Number of arguments:', len(sys.argv), 'arguments.'
	print 'Argument List:', str(sys.argv)
	initial_Cash=sys.argv[1]
	infile=sys.argv[2]
	outfile=sys.argv[3]
	#get data below
	na_data=readcsv(infile)
	na_symbols = na_data[:,3]
	na_dates= np.int_(na_data[:,0:3])
	ls_symbols=getsymbols(na_symbols)
	na_price,ldt_timestamps=getdata(na_dates,ls_symbols)
	cash, value, total_value=buildportfolio(na_price,ls_symbols,initial_Cash,ldt_timestamps,na_data,na_dates)
	writeresults(total_value,ldt_timestamps,outfile)






