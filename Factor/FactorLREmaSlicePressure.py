# -*- coding: utf-8 -*-
"""
Created on 2018/7/5 14:13

@author: 011672
"""

from System.Factor import Factor


class FactorLREmaSlicePressure(Factor):
    def __init__(self, para, factorManagement):
        Factor.__init__(self, para, factorManagement)
        self.__returnLag = para["returnLag"]
        self.__factorLag = para["factorLag"]
        self.__factorNum = para["factorNum"]
        self.__paraNumOrderMax = para['paraNumOrderMax']  # 比较盘口档位数
        self.__paraNumOrderMin = para['paraNumOrderMin']  # 比较盘口档位数
        self.__paraEmaSlicePressureLag = para['paraEmaSlicePressureLag']  # EMA参数

        self.__data = self.getTradingUnderlyingData(self.getIndexTradingUnderlying()[0])

        paraRegressionEmaSlicePressure = {"name": "LinearRegressionEmaSlicePressure", "className": "LinearRegression",
                                          "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                          "indexFactorUnderlying": self.getIndexFactorUnderlying(),
                                          "returnLag": self.__returnLag,
                                          "factorLag": self.__factorLag,
                                          "factorNum": self.__factorNum,
                                          "paraOriginalData": {"name": "emaSlicePressure", "className": "FactorEmaSlicePressure",
                                                               "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                                               "indexFactorUnderlying": self.getIndexFactorUnderlying(),
                                                               "paraNumOrderMax": self.__paraNumOrderMax,
                                                               "paraNumOrderMin": self.__paraNumOrderMin,
                                                               "paraEmaSlicePressureLag": self.__paraEmaSlicePressureLag}}
        self.__regressionEmaSlicePressure = self.getFactorData(paraRegressionEmaSlicePressure)

        factorManagement.registerFactor(self, para)

    def calculate(self):
        self.addData(self.__regressionEmaSlicePressure.getLastContent(), self.__data.getLastTimeStamp())
