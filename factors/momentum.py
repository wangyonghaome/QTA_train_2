""" 
@Time    : 2022/1/1 18:44
@Author  : Carl
@File    : momentum.py
@Software: PyCharm
"""
import pandas as pd
import numpy as np
from data.basicData import BasicData

class Momentum:
    def __init__(self):
        self.factorData = dict()

    def __cal_mid(self, data):
        return (data.ap1 + data.bp1) / 2

    def cal_factor(self):
        for d in BasicData.basicData.keys():
            factorData_1_d = BasicData.basicData[d].copy()
            factorData_1_d['mid'] = (factorData_1_d.ap1 + factorData_1_d.bp1) / 2
            factorData_1_d['ma10'] = factorData_1_d.mid.rolling(20).agg(np.mean)
            self.factorData[d] = factorData_1_d[['time', 'milsec', 'ma10']]


