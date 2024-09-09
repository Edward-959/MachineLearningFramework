# -*- coding: utf-8 -*-
"""
Created on 2018/7/11 15:09

@author: 011672
"""

from System.Factor import Factor


class FactorEmaOrderPressureTransactionSell(Factor):
    def __init__(self, para, factorManagement):
        Factor.__init__(self, para, factorManagement)
        self.__paraOrderPressureTransactionLag = para['paraOrderPressureTransactionLag']

        self.__data = self.getTradingUnderlyingData(self.getIndexTradingUnderlying()[0])
        self.__orderPressureTransaction = self.getFactorData(
            {"name": "orderPressureTransaction", "className": "FactorOrderPressureTransaction",
             "indexTradingUnderlying": self.getIndexTradingUnderlying(),
             "indexFactorUnderlying": self.getIndexFactorUnderlying(),
             "paraOrderPressureTransactionLag": self.__paraOrderPressureTransactionLag})
        factorManagement.registerFactor(self, para)

    def calculate(self):
        factorValue = self.__orderPressureTransaction.getEmaOrderPressureTransactionSell()[-1]
        self.addData(factorValue, self.__data.getLastTimeStamp())
