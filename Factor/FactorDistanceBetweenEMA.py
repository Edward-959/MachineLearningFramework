# -*- coding: utf-8 -*-
"""
Created on 2017/12/13 9:32

@author: 011672
"""
# 计算两个EMA之间的距离

from System.Factor import Factor


class FactorDistanceBetweenEMA(Factor):
    def __init__(self, para, factorManagement):
        Factor.__init__(self, para, factorManagement)

        self.__paraFastLag = para['paraFastLag']
        self.__paraSlowLag = para['paraSlowLag']

        paraEmaMidPrice = {"name": "emaMidPrice", "className": "Ema",
                           "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                           "indexFactorUnderlying": self.getIndexFactorUnderlying(),
                           "paraLag": self.__paraFastLag,
                           "paraOriginalData": {"name": "midPrice", "className": "MidPrice",
                                                "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                                "indexFactorUnderlying": self.getIndexFactorUnderlying()}}
        self.__emaMidPriceFast = self.getFactorData(paraEmaMidPrice)
        paraEmaMidPrice = {"name": "emaMidPrice", "className": "Ema",
                           "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                           "indexFactorUnderlying": self.getIndexFactorUnderlying(),
                           "paraLag": self.__paraSlowLag,
                           "paraOriginalData": {"name": "midPrice", "className": "MidPrice",
                                                "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                                "indexFactorUnderlying": self.getIndexFactorUnderlying()}}
        self.__emaMidPriceSlow = self.getFactorData(paraEmaMidPrice)

        factorManagement.registerFactor(self, para)

    def calculate(self):
        lastFactor = (self.__emaMidPriceFast.getLastContent() - self.__emaMidPriceSlow.getLastContent()) / self.__emaMidPriceFast.getLastContent()
        self.addData(lastFactor, self.__emaMidPriceFast.getLastTimeStamp())
