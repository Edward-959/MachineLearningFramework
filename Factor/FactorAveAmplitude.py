# -*- coding: utf-8 -*-
"""
Created on 2017/9/5 10:40

@author: 011672
"""
from System.Factor import Factor
import numpy as np


class FactorAveAmplitude(Factor):  # 过去paraAmplitudeLag波的平均振幅
    def __init__(self, para, factorManagement):  # 传入因子参数,归属的因子管理模块，需要用到的其他因子或非因子
        Factor.__init__(self, para, factorManagement)
        # 因子参数
        self.__paraAmplitudeLag = para['paraAmplitudeLag']
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
            if self.__extremePointInfo.__len__() == 0:
                pass
            elif self.__extremePointInfo.__len__() < self.__paraAmplitudeLag:
                temp = []
                for iExtremePointInfo in self.__extremePointInfo:
                    temp.append(abs(iExtremePointInfo[3]))
                factorValue = np.mean(temp)
            else:
                temp = []
                for i in range(self.__paraAmplitudeLag):
                    temp.append(abs(self.__extremePointInfo[-i-1][3]))
                factorValue = np.mean(temp)
        else:
            if len(self.getContent()) == 0:
                factorValue = 0
            else:
                factorValue = self.getLastContent()
        self.addData(factorValue, self.__data.getLastTimeStamp())
