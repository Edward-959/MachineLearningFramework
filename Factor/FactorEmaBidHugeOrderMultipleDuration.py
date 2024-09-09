# -*- coding: utf-8 -*-
"""
Created on 2017/9/7 19:42

@author: 011672
"""
from System.Factor import Factor
import time


class FactorEmaBidHugeOrderMultipleDuration(Factor):
    def __init__(self, para, factorManagement):
        Factor.__init__(self, para, factorManagement)
        self.__paraNumOrderMax = para['paraNumOrderMax']
        self.__paraNumOrderMin = para['paraNumOrderMin']
        self.__paraNumOrderMaxForAveOrderVolume = para["paraNumOrderMaxForAveOrderVolume"]
        self.__paraNumOrderMinForAveOrderVolume = para["paraNumOrderMinForAveOrderVolume"]
        self.__paraEmaAveOrderVolumeLag = para['paraEmaAveOrderVolumeLag']
        self.__paraLag = para["paraLag"]
        self.__paraHorizon = para['paraHorizon']

        self.__data = self.getTradingUnderlyingData(self.getIndexTradingUnderlying()[0])
        self.__emaBidHugeOrderMultiple = self.getFactorData({"name": "emaBidHugeOrderMultiple",
                                                             "className": "FactorEmaBidHugeOrderMultiple",
                                                             "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                                             "indexFactorUnderlying": self.getIndexFactorUnderlying(),
                                                             "paraLag": self.__paraLag,
                                                             "paraNumOrderMax": self.__paraNumOrderMax,
                                                             "paraNumOrderMin": self.__paraNumOrderMin,
                                                             "paraNumOrderMaxForAveOrderVolume":
                                                                 self.__paraNumOrderMaxForAveOrderVolume,
                                                             "paraNumOrderMinForAveOrderVolume":
                                                                 self.__paraNumOrderMinForAveOrderVolume,
                                                             "paraEmaAveOrderVolumeLag":
                                                                 self.__paraEmaAveOrderVolumeLag})
        factorManagement.registerFactor(self, para)

    def calculate(self):
        TempDuration = 0
        if self.getContent().__len__() >= 1:
            datanow = self.__emaBidHugeOrderMultiple.getLastContent() - self.__paraHorizon
            datalast = self.__emaBidHugeOrderMultiple.getContent()[-2] - self.__paraHorizon
            timenow = self.__data.getLastTimeStamp()
            timelast = self.__data.getTimeStamp()[-2]
            if datanow > 0 and datalast > 0:
                if time.localtime(timenow).tm_hour >= 13 and time.localtime(timelast).tm_hour < 12:
                    TempDuration = self.getLastContent() + (timenow - timelast - 5400)  # 考虑午间休盘
                else:
                    TempDuration = self.getLastContent() + (timenow - timelast)
        self.addData(TempDuration, self.__data.getLastTimeStamp())
