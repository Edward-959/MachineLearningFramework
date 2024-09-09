# -*- coding: utf-8 -*-
"""
Created on 2018/7/11 18:48

@author: 011672
"""

from System.Factor import Factor
import math

class FactorMAVolumeDistance(Factor):
    def __init__(self, para, factorManagement):
        Factor.__init__(self, para, factorManagement)
        self.__paraMAFastLag = para["paraMAFastLag"]
        self.__paraMASlowLag = para["paraMASlowLag"]

        self.__data = self.getTradingUnderlyingData(self.getIndexTradingUnderlying()[0])
        self.__volume = self.getFactorData({"name": "volume", "className": "Volume",
                                              "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                              "indexFactorUnderlying": self.getIndexFactorUnderlying()})

        self.__historyVolume = self.getFactorData({"name": "historyVolume", "className": "HistoryVolume",
                                              "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                              "indexFactorUnderlying": self.getIndexFactorUnderlying()})
        paraMAVolume = {"name": "MAVolume", "className": "MA",
                       "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                       "indexFactorUnderlying": self.getIndexFactorUnderlying(),
                       "paraLag": self.__paraMAFastLag,
                       "paraOriginalData": {"name": "volume", "className": "Volume",
                                            "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                            "indexFactorUnderlying": self.getIndexFactorUnderlying()}}
        self.__MAVolume = self.getFactorData(paraMAVolume)
        factorManagement.registerFactor(self, para)

    def calculate(self):
        lastMAVolume = self.__MAVolume.getLastContent()

        if len(self.__historyVolume.getContent()) == 0:
            FactorValue = 0.0
        elif len(self.__historyVolume.getContent()) <= self.__paraMASlowLag:
            FactorValue = 1000 * lastMAVolume / sum(self.__historyVolume.getContent())
        else:
            FactorValue = 1000 * lastMAVolume / sum(self.__historyVolume.getContent()[-self.__paraMASlowLag:])
        self.addData(FactorValue, self.__data.getLastTimeStamp())


