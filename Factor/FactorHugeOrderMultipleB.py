# -*- coding: utf-8 -*-
"""
Created on 2018/6/11 10:55

@author: 011672
(volumeB - volumeS) / (emaVolumeB + emaVolumeS)
"""
import numpy as np
from System.Factor import Factor


class FactorHugeOrderMultipleB(Factor):
    def __init__(self, para, factorManagement):  # 传入因子参数,归属的因子管理模块，需要用到的其他因子或非因子
        Factor.__init__(self, para, factorManagement)
        # 因子参数
        self.__paraNumOrderMax = para['paraNumOrderMax']
        self.__paraNumOrderMin = para['paraNumOrderMin']
        self.__paraEmaHugeOrderMultipleLag = para['paraEmaHugeOrderMultipleLag']
        # 因子计算会用到的中间变量,取数据时候要注意会不会出现取出的因子还没有计算出值
        # 如果需要实例化因子作为中间变量，则name不要以factor开头，否则会输出到最终的结果中
        # 如果需要实例化因子或者非因子，需要考虑注册因子的先后顺序，即factorManagement.registerFactor(self)
        self.__data = self.getTradingUnderlyingData(self.getIndexTradingUnderlying()[0])
        self.__HugeOrderMultiple = self.getFactorData({"name": "hugeOrderMultipleB", "className": "HugeOrderMultipleB",
                                                       "paraNumOrderMax": self.__paraNumOrderMax,
                                                       "paraNumOrderMin": self.__paraNumOrderMin,
                                                       "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                                       "indexFactorUnderlying": self.getIndexFactorUnderlying()})
        paraEmaHugeOrderMultiple = {"name": "emaAveOrderVolume", "className": "Ema",
                                    "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                    "indexFactorUnderlying": self.getIndexFactorUnderlying(),
                                    "paraLag": self.__paraEmaHugeOrderMultipleLag,
                                    "paraOriginalData": {"name": "emaHugeOrderMultipleB", "className": "HugeOrderMultipleB",
                                                         "paraNumOrderMax": self.__paraNumOrderMax,
                                                         "paraNumOrderMin": self.__paraNumOrderMin,
                                                         "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                                         "indexFactorUnderlying": self.getIndexFactorUnderlying()}}
        self.__emaHugeOrderMultiple = self.getFactorData(paraEmaHugeOrderMultiple)
        factorManagement.registerFactor(self, para)

    def calculate(self):
        volumeB = self.__HugeOrderMultiple.getLastContent()[0]
        volumeS = self.__HugeOrderMultiple.getLastContent()[1]
        emaVolumeB = self.__emaHugeOrderMultiple.getLastContent()[0]
        emaVolumeS = self.__emaHugeOrderMultiple.getLastContent()[1]
        if emaVolumeB != 0 and emaVolumeS != 0:
            factorValue = (volumeB - volumeS) / (emaVolumeB + emaVolumeS)
        else:
            factorValue = 0
        self.addData(factorValue, self.__data.getLastTimeStamp())
