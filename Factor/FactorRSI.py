"""
@author: 011672
@revise: 006688

计算中间价序列的RSI值
N日RSI=[A÷(A+B)]×100%
公式中，A——N日内收盘涨幅之和
B——N日内收盘跌幅之和(取正值)
"""
from System.Factor import Factor
import numpy as np


class FactorRSI(Factor):
    def __init__(self, para, factorManagement):
        Factor.__init__(self, para, factorManagement)

        self.__paraRSILag = para["paraRSILag"]

        self.__midPrice = self.getFactorData({"name": "midPrice", "className": "MidPrice",
                                              "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                              "indexFactorUnderlying": self.getIndexFactorUnderlying()})

        factorManagement.registerFactor(self, para)

    def calculate(self):
        midPrice = np.array(self.__midPrice.getContent())

        # 计算计算周期内相邻切片中间价的价差
        if len(midPrice) <= self.__paraRSILag:
            difPrice = midPrice[1:] - midPrice[:-1]
        else:
            difPrice = midPrice[-self.__paraRSILag:] - midPrice[-self.__paraRSILag-1:-1]
        # 对价差序列中所有的正值和负值（绝对值）分别求和，据此计算RSI
        if len(difPrice) == 0:  # 第一个值计为0
            RSI = 0
        else:
            positiveSum = sum(difPrice[difPrice > 0])
            negativeSum = abs(sum(difPrice[difPrice < 0]))
            if positiveSum == 0 and negativeSum == 0:
                RSI = 50
            else:
                RSI = positiveSum / (positiveSum + negativeSum) * 100
        self.addData(RSI, self.__midPrice.getLastTimeStamp())
