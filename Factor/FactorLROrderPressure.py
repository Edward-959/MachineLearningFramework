# -*- coding: utf-8 -*-
"""
Created on 2018/7/5 14:13

@author: 011672
"""

from System.Factor import Factor


class FactorLROrderPressure(Factor):
    def __init__(self, para, factorManagement):
        Factor.__init__(self, para, factorManagement)
        self.__returnLag = para["returnLag"]
        self.__factorLag = para["factorLag"]
        self.__factorNum = para["factorNum"]
        self.__paraOrderPressureLag = para['paraOrderPressureLag']

        self.__data = self.getTradingUnderlyingData(self.getIndexTradingUnderlying()[0])

        paraRegressionOrderPressure = {"name": "LinearRegressionOrderPressure", "className": "LinearRegression",
                                       "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                       "indexFactorUnderlying": self.getIndexFactorUnderlying(),
                                       "returnLag": self.__returnLag,
                                       "factorLag": self.__factorLag,
                                       "factorNum": self.__factorNum,
                                       "paraOriginalData": {"name": "orderPressure",
                                                            "className": "FactorOrderPressure",
                                                            "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                                            "indexFactorUnderlying": self.getIndexFactorUnderlying(),
                                                            "paraOrderPressureLag": self.__paraOrderPressureLag}}
        self.__regressionOrderPressure = self.getFactorData(paraRegressionOrderPressure)

        factorManagement.registerFactor(self, para)

    def calculate(self):
        self.addData(self.__regressionOrderPressure.getLastContent(), self.__data.getLastTimeStamp())
