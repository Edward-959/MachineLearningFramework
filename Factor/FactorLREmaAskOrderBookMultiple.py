# -*- coding: utf-8 -*-
"""
Created on 2018/7/5 14:13

@author: 011672
"""

from System.Factor import Factor


class FactorLREmaAskOrderBookMultiple(Factor):
    def __init__(self, para, factorManagement):
        Factor.__init__(self, para, factorManagement)
        self.__returnLag = para["returnLag"]
        self.__factorLag = para["factorLag"]
        self.__factorNum = para["factorNum"]
        self.__paraNumOrderMax = para['paraNumOrderMax']
        self.__paraNumOrderMin = para['paraNumOrderMin']
        self.__paraNumOrderMaxForAveOrderVolume = para["paraNumOrderMaxForAveOrderVolume"]
        self.__paraNumOrderMinForAveOrderVolume = para["paraNumOrderMinForAveOrderVolume"]
        self.__paraEmaAveOrderVolumeLag = para['paraEmaAveOrderVolumeLag']
        self.__paraLag = para["paraLag"]

        self.__data = self.getTradingUnderlyingData(self.getIndexTradingUnderlying()[0])

        paraRegressionEmaAskOrderBookMultiple = {"name": "LinearRegressionEmaAskOrderBookMultiple",
                                                 "className": "LinearRegression",
                                                 "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                                 "indexFactorUnderlying": self.getIndexFactorUnderlying(),
                                                 "returnLag": self.__returnLag,
                                                 "factorLag": self.__factorLag,
                                                 "factorNum": self.__factorNum,
                                                 "paraOriginalData": {"name": "emaAskOrderBookMultiple",
                                                                      "className": "FactorEmaAskOrderBookMultiple",
                                                                      "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                                                      "indexFactorUnderlying": self.getIndexFactorUnderlying(),
                                                                      "paraNumOrderMax": self.__paraNumOrderMax,
                                                                      "paraNumOrderMin": self.__paraNumOrderMin,
                                                                      "paraNumOrderMaxForAveOrderVolume": self.__paraNumOrderMaxForAveOrderVolume,
                                                                      "paraNumOrderMinForAveOrderVolume": self.__paraNumOrderMinForAveOrderVolume,
                                                                      "paraEmaAveOrderVolumeLag": self.__paraEmaAveOrderVolumeLag,
                                                                      "paraLag": self.__paraLag}}
        self.__regressionEmaAskOrderBookMultiple = self.getFactorData(paraRegressionEmaAskOrderBookMultiple)

        factorManagement.registerFactor(self, para)

    def calculate(self):
        self.addData(self.__regressionEmaAskOrderBookMultiple.getLastContent(), self.__data.getLastTimeStamp())
