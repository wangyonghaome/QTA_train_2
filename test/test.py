""" 
@Time    : 2022/1/1 16:06
@Author  : Carl
@File    : test.py
@Software: PyCharm
"""
import pandas as pd
from factors.momentum import Momentum
from data.basicData import BasicData
from backtest.backtest import Backtest

BasicData.set_mkt()
m = Momentum()
m.cal_factor()
factorData = m.factorData

b = Backtest(factorData=factorData)
longInfo, shortInfo = b.get_tradeInfo('20210804')
backtesta_reult=b.backtest(fee=3/10000,startday='20210804')
