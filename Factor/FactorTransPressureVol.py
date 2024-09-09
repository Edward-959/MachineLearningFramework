# -*- coding: utf-8 -*-
"""
Created on 2018/7/11 18:48
@author: 011672
@revised by 006566 2018/7/25
@revised on 2018/10/13
"""

from System.Factor import Factor
import math


class FactorTransPressureVol(Factor):
    def __init__(self, para, factorManagement):
        Factor.__init__(self, para, factorManagement)
        self.__paraDecayNum = para['paraDecayNum']
        self.__paraMALag = para['paraMALag']
        self.__data = self.getTradingUnderlyingData(self.getIndexTradingUnderlying()[0])
        paraTradeVolumePressure = {"name": "TradeVolumeWeighted", "className": "TradeVolumeWeighted",
                                   "paraDecayNum": self.__paraDecayNum,
                                   "paraMALag": self.__paraMALag,
                                   "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                   "indexFactorUnderlying": self.getIndexFactorUnderlying()}
        self.__TradeVolumePressure = self.getFactorData(paraTradeVolumePressure)
        factorManagement.registerFactor(self, para)
        self.__TradeVolumePressureBid = []
        self.__TradeVolumePressureAsk = []

    def calculate(self):
        PressureBid = self.__TradeVolumePressure.getLastContent()[0]
        PressureAsk = self.__TradeVolumePressure.getLastContent()[1]
        if PressureBid == 0 and PressureAsk == 0:
            FactorValue = 0
        elif PressureBid == 0:
            FactorValue = -10
        elif PressureAsk == 0:
            FactorValue = 10
        else:
            FactorValue = math.log(PressureBid) - math.log(PressureAsk)
        if self.__TradeVolumePressureBid.__len__() > 0:
            self.__TradeVolumePressureBid.append(PressureBid)
            self.__TradeVolumePressureAsk.append(PressureAsk)
            self.addData(FactorValue, self.__data.getLastTimeStamp())
        else:
            self.__TradeVolumePressureBid.append(0)
            self.__TradeVolumePressureAsk.append(0)
            self.addData(0, self.__data.getLastTimeStamp())

    def getVolumePressureBid(self):
        return self.__TradeVolumePressureBid

    def getVolumePressureAsk(self):
        return self.__TradeVolumePressureAsk
