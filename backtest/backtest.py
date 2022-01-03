""" 
@Time    : 2022/1/1 19:19
@Author  : Carl
@File    : backtest.py
@Software: PyCharm
"""
import pandas as pd
import numpy as np
from data.basicData import BasicData

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

    def backtest(self):
        pass












