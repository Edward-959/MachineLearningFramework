# -*- coding: utf-8 -*-
"""
Created on 2018/7/11 18:48
@author: 011672
@revised by 006566 2018/7/25
"""

from System.Factor import Factor


class FactorTransBidPressure(Factor):
    def __init__(self, para, factorManagement):
        Factor.__init__(self, para, factorManagement)
        self.__paraDecayNum = para['paraDecayNum']
        self.__paraMALag = para['paraMALag']

        self.__data = self.getTradingUnderlyingData(self.getIndexTradingUnderlying()[0])
        self.__transPressure = self.getFactorData({"name": "factorTransPressure", "className": "FactorTransPressure",
                                                   "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                                   "indexFactorUnderlying": self.getIndexFactorUnderlying(),
                                                   "paraDecayNum": self.__paraDecayNum,
                                                   "paraMALag": self.__paraMALag})
        factorManagement.registerFactor(self, para)

    def calculate(self):
        factorValue = self.__transPressure.getNumPressureBid()[-1]
        self.addData(factorValue, self.__data.getLastTimeStamp())