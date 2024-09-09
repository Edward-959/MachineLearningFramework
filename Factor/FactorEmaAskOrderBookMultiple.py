# -*- coding: utf-8 -*-
"""
Created on 2018/1/29 19:37

@author: 011672
"""
from System.Factor import Factor


class FactorEmaAskOrderBookMultiple(Factor):
    def __init__(self, para, factorManagement):
        Factor.__init__(self, para, factorManagement)
        self.__paraNumOrderMax = para['paraNumOrderMax']
        self.__paraNumOrderMin = para['paraNumOrderMin']
        self.__paraNumOrderMaxForAveOrderVolume = para["paraNumOrderMaxForAveOrderVolume"]
        self.__paraNumOrderMinForAveOrderVolume = para["paraNumOrderMinForAveOrderVolume"]
        self.__paraEmaAveOrderVolumeLag = para['paraEmaAveOrderVolumeLag']
        self.__paraLag = para["paraLag"]

        self.__data = self.getTradingUnderlyingData(self.getIndexTradingUnderlying()[0])
        paraEmaOrderBookMultiple = {"name": "emaOrderBookMultiple", "className": "Ema",
                                    "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                    "indexFactorUnderlying": self.getIndexFactorUnderlying(),
                                    "paraLag": self.__paraLag,
                                    "paraOriginalData": {"name": "orderBookMultiple", "className": "OrderBookMultiple",
                                                         "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                                         "indexFactorUnderlying": self.getIndexFactorUnderlying(),
                                                         "paraNumOrderMax": self.__paraNumOrderMax,
                                                         "paraNumOrderMin": self.__paraNumOrderMin,
                                                         "paraNumOrderMaxForAveOrderVolume": self.__paraNumOrderMaxForAveOrderVolume,
                                                         "paraNumOrderMinForAveOrderVolume": self.__paraNumOrderMinForAveOrderVolume,
                                                         "paraEmaAveOrderVolumeLag": self.__paraEmaAveOrderVolumeLag}}
        self.__emaOrderBookMultiple = self.getFactorData(paraEmaOrderBookMultiple)
        factorManagement.registerFactor(self, para)

    def calculate(self):
        factorValue = self.__emaOrderBookMultiple.getLastContent()[1]
        self.addData(factorValue, self.__data.getLastTimeStamp())
