""" 
@Time    : 2022/1/1 18:52
@Author  : Carl
@File    : basicData.py
@Software: PyCharm
"""
import pickle

class BasicData:
    @classmethod
    def set_mkt(cls, mkt='ag'):
        with open(f'./data/cleanData/day/{mkt}_dict.txt', 'rb') as file:
            cls.basicData = pickle.load(file)

    def __new__(cls):
        return cls