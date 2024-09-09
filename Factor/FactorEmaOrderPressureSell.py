# -*- coding: utf-8 -*-
"""
Created on 2017/9/11 18:56

@author: 011672
"""
from System.Factor import Factor


class FactorEmaOrderPressureSell(Factor):
    def __init__(self, para, factorManagement):
        Factor.__init__(self, para, factorManagement)
        self.__paraOrderPressureLag = para['paraOrderPressureLag']

        self.__data = self.getTradingUnderlyingData(self.getIndexTradingUnderlying()[0])
        self.__orderPressure = self.getFactorData({"name": "orderPressure", "className": "FactorOrderPressure",
                                                   "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                                   "indexFactorUnderlying": self.getIndexFactorUnderlying(),
                                                   "paraOrderPressureLag": self.__paraOrderPressureLag})
        factorManagement.registerFactor(self, para)

    def calculate(self):
        factorValue = self.__orderPressure.getEmaOrderPressureSell()[-1]
        self.addData(factorValue, self.__data.getLastTimeStamp())
