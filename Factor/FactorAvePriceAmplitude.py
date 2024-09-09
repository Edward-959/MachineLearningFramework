# -*- coding: utf-8 -*-
"""
Created on 2017/9/5 13:11

@author: 011672
"""
from System.Factor import Factor
import numpy as np


class FactorAvePriceAmplitude(Factor):  # 过去paraPriceAmplitudeLag波的价格分位变化的平均值
    def __init__(self, para, factorManagement):  # 传入因子参数,归属的因子管理模块，需要用到的其他因子或非因子
        Factor.__init__(self, para, factorManagement)
        # 因子参数
        self.__paraPriceAmplitudeLag = para['paraPriceAmplitudeLag']
        self.__paraFastLag = para['paraFastLag']
        self.__paraSlowLag = para['paraSlowLag']
        # 因子计算会用到的中间变量,取数据时候要注意会不会出现取出的因子还没有计算出值
        # 如果需要实例化因子作为中间变量，则name不要以factor开头，否则会输出到最终的结果中
        # 如果需要实例化因子或者非因子，需要考虑注册因子的先后顺序，即factorManagement.registerFactor(self)
        self.__data = self.getTradingUnderlyingData(self.getIndexTradingUnderlying()[0])
        self.__extremePoint = self.getFactorData({"name": "extremePoint", "className": "ExtremePoint",
                                                  "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                                  "indexFactorUnderlying": self.getIndexFactorUnderlying(),
                                                  "paraFastLag": self.__paraFastLag, "paraSlowLag": self.__paraSlowLag})
        self.__extremePointInfo = self.__extremePoint.getExtremePointInfo()
        factorManagement.registerFactor(self, para)

    def calculate(self):
        factorValue = 0.
        if self.__extremePoint.getUpdateStatus() == 1:
            if self.__extremePointInfo.__len__() <= 1:
                pass
            elif self.__extremePointInfo.__len__() <= self.__paraPriceAmplitudeLag:
                temp = []
                for i in range(self.__extremePointInfo.__len__()-1):
                    temp.append(abs(self.__extremePointInfo[i+1][1] - self.__extremePointInfo[i][1]))
                factorValue = np.mean(temp)
            else:
                temp = []
                for i in range(self.__paraPriceAmplitudeLag):
                    temp.append(abs(self.__extremePointInfo[-i-1][1] - self.__extremePointInfo[-i-2][1]))
                factorValue = np.mean(temp)
        else:
            if len(self.getContent()) == 0:
                factorValue = 0
            else:
                factorValue = self.getLastContent()
        self.addData(factorValue, self.__data.getLastTimeStamp())
