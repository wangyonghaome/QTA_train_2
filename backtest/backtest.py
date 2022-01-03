""" 
@Time    : 2022/1/1 19:19
@Author  : Carl
@File    : backtest.py
@Software: PyCharm
"""
import pandas as pd
import numpy as np
from data.basicData import BasicData
import matplotlib.pyplot as plt
class Backtest:
    def __init__(self, factorData):
        self.rolling_window = 2
        self.long_bar = 0.95
        self.liquidLong_bar = 0.90
        self.short_bar = 0.05
        self.liquidShort_bar = 0.10
        self.factorData = factorData


    def cal_bars(self, date):
        dateList = [int(d) for d in self.factorData.keys()]
        dateList.sort()
        try:
            datePosition = dateList.index(int(date))
            if datePosition < 2:
                raise IOError('Lack date for bar calculation !!!')
            dateInterval = [str(dateList[datePosition-i]) for i in range(1,3)]
        except:
            raise IOError('Date out of range !!!')
        for i, d in enumerate(dateInterval):
            if i == 0:
                factorInterval = self.factorData[d]
            else:
                factorInterval = factorInterval.append(self.factorData[d])
        factorInterval = factorInterval.iloc[:, -1].dropna()
        return [np.quantile(factorInterval, self.long_bar), np.quantile(factorInterval, self.liquidLong_bar),
                np.quantile(factorInterval, self.short_bar), np.quantile(factorInterval, self.liquidShort_bar)]

    def get_longInfo(self, date, longBars):
        longInfo = self.factorData[date].copy().dropna()
        longInfo.loc[(longInfo.iloc[:, 2] >= longBars[0]) | (longInfo.iloc[:, 2] < longBars[1]), ['long', 'liquid_long']] = 0
        longInfo.loc[longInfo.iloc[:, 2] >= longBars[0] ,'long'] = 1
        longInfo.loc[longInfo.iloc[:, 2] < longBars[1], 'liquid_long'] = -1
        longInfo['trdInfo'] = longInfo.long + longInfo.liquid_long
        longInfo['trdInfo'].fillna(method='pad', inplace=True)
        longPoint = longInfo.loc[(longInfo.trdInfo == 1) & (longInfo.trdInfo.shift(1) == -1), ['time', 'milsec', 'trdInfo']].copy()
        liquidPoint = longInfo.loc[(longInfo.trdInfo == -1) & (longInfo.trdInfo.shift(1) == 1), ['time', 'milsec', 'trdInfo']].copy()
        if len(longPoint) > len(liquidPoint):
            liquidPoint = liquidPoint.append(longInfo.iloc[-1][['time', 'milsec', 'trdInfo']])
            liquidPoint.iloc[-1, 2] = -1
        elif len(longPoint) < len(liquidPoint):
            longPoint = longPoint.append(longInfo.iloc[0][['time', 'milsec', 'trdInfo']])
            longPoint.iloc[-1, 2] = 1
        longPoint = longPoint.append(liquidPoint)
        return longPoint

    def get_shortInfo(self, date, shortBars):
        shortInfo = self.factorData[date].copy().dropna()
        shortInfo.loc[
            (shortInfo.iloc[:, 2] < shortBars[0]) | (shortInfo.iloc[:, 2] > shortBars[1]), ['short', 'liquid_short']] = 0
        shortInfo.loc[shortInfo.iloc[:, 2] < shortBars[0], 'short'] = -1
        shortInfo.loc[shortInfo.iloc[:, 2] >= shortBars[1], 'liquid_short'] = 1
        shortInfo['trdInfo'] = shortInfo.short + shortInfo.liquid_short
        shortInfo['trdInfo'].fillna(method='pad', inplace=True)
        shortPoint = shortInfo.loc[
            (shortInfo.trdInfo == -1) & (shortInfo.trdInfo.shift(1) == 1), ['time', 'milsec', 'trdInfo']].copy()
        liquidPoint = shortInfo.loc[
            (shortInfo.trdInfo == 1) & (shortInfo.trdInfo.shift(1) == -1), ['time', 'milsec', 'trdInfo']].copy()
        if len(shortPoint) > len(liquidPoint):
            liquidPoint = liquidPoint.append(shortInfo.iloc[-1][['time', 'milsec', 'trdInfo']])
            liquidPoint.iloc[-1, 2] = 1
        elif len(shortPoint) < len(liquidPoint):
            shortPoint = shortPoint.append(shortInfo.iloc[0][['time', 'milsec', 'trdInfo']])
            shortPoint.iloc[-1, 2] = -1
        shortPoint = shortPoint.append(liquidPoint)
        return shortPoint

    def get_tradeInfo(self, date):
        bars = self.cal_bars(date)
        longInfo = pd.merge(self.get_longInfo(date, bars[0:2]), BasicData.basicData[date][['time', 'milsec', 'ap1', 'bp1']],
                            on=['time', 'milsec'], how='left')
        shortInfo = pd.merge(self.get_shortInfo(date, bars[2:]), BasicData.basicData[date][['time', 'milsec', 'ap1', 'bp1']],
                            on=['time', 'milsec'], how='left')
        return longInfo, shortInfo

    def backtest(self,fee=3/10000,startday='20210804'):
        def get_factor_inf(df):
            def maxdrawdown(arr):
            	i = np.argmax((np.maximum.accumulate(arr) - arr)/np.maximum.accumulate(arr)) # end of the period
            	j = np.argmax(arr[:i]) # start of period
            	return (1-arr[i]/arr[j])
            series=df['cumu_nav']
            ann_ret=series.iloc[-1]**(250/len(validday_list))-1
            daily_return_series=pd.merge(pd.DataFrame(index=validday_list),df['return_'],left_index=True,right_on=df.index.get_level_values('date'),how='left')
            daily_return_series=daily_return_series.set_index('key_0').fillna(0)
            daily_return_series=daily_return_series.groupby(daily_return_series.index).sum()
            daily_vol=(np.std(daily_return_series)*np.sqrt(252)).values[0]
            sharp=((ann_ret-0.03)/daily_vol)
            maxdraw=maxdrawdown((1+daily_return_series.values).cumprod())
            return_series=pd.Series(index=['ann_ret','vol','sharp','maxdrawdown'],data=[ann_ret,daily_vol,sharp,maxdraw])
            return return_series
        f=lambda x:x['ap1'] if x['id']==1 else x['bp1']
        tradeday_list=sorted([int(i) for i in list(BasicData.basicData.keys())])
        validday_list=[i for i in tradeday_list if i>=int(startday)]
        trade_record={"long":[],"short":[]}
        #获得每天的买点卖点
        for date in validday_list:
            longInfo, shortInfo=self.get_tradeInfo(str(date))
            longInfo['date']=date
            shortInfo['date']=date
            longInfo['time']=longInfo['time']+longInfo['milsec']/1000
            shortInfo['time']=shortInfo['time']+shortInfo['milsec']/1000
            longInfo=longInfo.set_index(['date','time']).drop(labels='milsec',axis=1)
            shortInfo=shortInfo.set_index(['date','time']).drop(labels='milsec',axis=1)
            trade_record['long'].append(longInfo)
            trade_record['short'].append(shortInfo)
        trade_record['long']=pd.concat(trade_record['long']).sort_index()
        trade_record['short']=pd.concat(trade_record['short']).sort_index()
        ##此处生成的id应该与trdInfo相同，验证买卖点是否正确
        trade_record['long']['id']=range(trade_record['long'].shape[0])
        trade_record['short']['id']=range(trade_record['short'].shape[0])
        trade_record['long']['id']=trade_record['long'].apply(lambda x:1 if int(x['id'])%2==0 else -1,axis=1)
        trade_record['short']['id']=trade_record['short'].apply(lambda x:1 if int(x['id'])%2==1 else -1,axis=1)
        #回测获得夏普比、波动率、年化、回测等
        factor_info={}
        for key in trade_record.keys():
            trade_record[key]['deal_price']=trade_record[key].apply(f,axis=1)
            trade_record[key]['return_']=trade_record[key]['deal_price']/trade_record[key]['deal_price'].shift(1)-1-fee
            if key == 'short':
                trade_record[key].loc[trade_record[key]['id']==-1,'return_']=0
            else:
                trade_record[key].loc[trade_record[key]['id']==1,'return_']=0
            trade_record[key]['cumu_nav']=(1+trade_record[key]['return_'].fillna(0)).cumprod()
            factor_info[key]=get_factor_inf(trade_record[key])
        long_short_nav=pd.merge(trade_record['short']['cumu_nav'],trade_record['long']['cumu_nav'],left_index=True,right_index=True,how='outer').fillna(method='ffill').fillna(1)
        long_short=pd.DataFrame(long_short_nav['cumu_nav_x']*long_short_nav['cumu_nav_y'],columns=['cumu_nav'])
        long_short['return_']=(long_short['cumu_nav'].diff()/long_short['cumu_nav'].shift()).fillna(0)
        factor_info['long_short']=get_factor_inf(long_short)
        #画图
        plt.figure(dpi=300,figsize=(15,10))
        i=1
        for key in trade_record:
            slice_return=trade_record[key].query('return_ !=0')['return_']
            ax=plt.subplot(2,2,i)
            ax.hist(slice_return.values,bins=50, density=True, cumulative=True, label='CDF', histtype='step')
            plt.title(key)
            i=i+1
        ax=plt.subplot(2,2,i)
        slice_ls_ret=long_short.query('return_ !=0')["return_"]
        plt.hist(slice_ls_ret.values,bins=50, density=True, cumulative=True, label='CDF', histtype='step')
        plt.title('long-short')
        plt.show()
        return pd.DataFrame(factor_info)












