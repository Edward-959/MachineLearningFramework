# -*- coding: utf-8 -*-
"""
Created on 2017/12/13 9:32

@author: 011672
"""
# 计算两个EMA之间的距离

from System.Factor import Factor


class FactorDistanceBetweenVWAPPrice(Factor):
    def __init__(self, para, factorManagement):
        Factor.__init__(self, para, factorManagement)

        self.__paraFastLag = para['paraFastLag']
        self.__paraSlowLag = para['paraSlowLag']

        paraVWAPPriceFast = {"name": "VWAPPriceFast", "className": "VWAPPrice",
                             "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                             "indexFactorUnderlying": self.getIndexFactorUnderlying(),
                             "N": self.__paraFastLag}
        self.__VWAPPriceFast = self.getFactorData(paraVWAPPriceFast)
        paraVWAPPriceSlow = {"name": "VWAPPriceFast", "className": "VWAPPrice",
                             "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                             "indexFactorUnderlying": self.getIndexFactorUnderlying(),
                             "N": self.__paraSlowLag}
        self.__VWAPPriceSlow = self.getFactorData(paraVWAPPriceSlow)

        factorManagement.registerFactor(self, para)

    def calculate(self):
        if self.__VWAPPriceFast.getLastContent() != 0:
            lastFactor = 1000 * (self.__VWAPPriceFast.getLastContent() - self.__VWAPPriceSlow.getLastContent()) / self.__VWAPPriceFast.getLastContent()
        else:
            lastFactor = 0
        self.addData(lastFactor, self.__VWAPPriceFast.getLastTimeStamp())
