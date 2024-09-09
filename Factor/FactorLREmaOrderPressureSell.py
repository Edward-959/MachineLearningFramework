# -*- coding: utf-8 -*-
"""
Created on 2017/9/11 18:48

@author: 011672
"""
from System.Factor import Factor


class FactorLREmaOrderPressureSell(Factor):
    def __init__(self, para, factorManagement):
        Factor.__init__(self, para, factorManagement)
        self.__returnLag = para["returnLag"]
        self.__factorLag = para["factorLag"]
        self.__factorNum = para["factorNum"]
        self.__paraOrderPressureLag = para['paraOrderPressureLag']

        self.__data = self.getTradingUnderlyingData(self.getIndexTradingUnderlying()[0])
        paraRegressionEmaOrderPressureSell = {"name": "LinearRegressionEmaOrderPressureSell",
                                              "className": "LinearRegression",
                                              "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                              "indexFactorUnderlying": self.getIndexFactorUnderlying(),
                                              "returnLag": self.__returnLag,
                                              "factorLag": self.__factorLag,
                                              "factorNum": self.__factorNum,
                                              "paraOriginalData": {"name": "emaOrderPressureSell",
                                                                   "className": "FactorEmaOrderPressureSell",
                                                                   "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                                                   "indexFactorUnderlying": self.getIndexFactorUnderlying(),
                                                                   "paraOrderPressureLag": self.__paraOrderPressureLag}}
        self.__regressionEmaOrderPressureSell = self.getFactorData(paraRegressionEmaOrderPressureSell)
        factorManagement.registerFactor(self, para)

    def calculate(self):
        self.addData(self.__regressionEmaOrderPressureSell.getLastContent(), self.__data.getLastTimeStamp())
