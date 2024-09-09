# -*- coding: utf-8 -*-
"""
Created on 2018/7/11 15:05

@author: 011672
"""

from System.Factor import Factor
import math


class FactorOrderPressureTransaction(Factor):
    def __init__(self, para, factorManagement):
        Factor.__init__(self, para, factorManagement)
        self.__paraOrderPressureTransactionLag = para['paraOrderPressureTransactionLag']

        self.__data = self.getTradingUnderlyingData(self.getIndexTradingUnderlying()[0])
        paraEmaOrderPressureTransaction = {"name": "emaOrderPressureTransaction", "className": "Ema",
                                           "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                           "indexFactorUnderlying": self.getIndexFactorUnderlying(),
                                           "paraLag": self.__paraOrderPressureTransactionLag,
                                           "paraOriginalData": {"name": "orderEvaluateTransaction",
                                                                "className": "OrderEvaluateTransaction",
                                                                "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                                                "indexFactorUnderlying": self.getIndexFactorUnderlying()}}
        self.__emaOrderPressureTransaction = self.getFactorData(
            paraEmaOrderPressureTransaction)  # 取OrderEvaluate中计算的买卖压的EMA
        factorManagement.registerFactor(self, para)
        self.__emaOrderPressureTransactionBuy = []
        self.__emaOrderPressureTransactionSell = []

    def calculate(self):
        PressureBuy = self.__emaOrderPressureTransaction.getLastContent()[0]
        PressureSell = self.__emaOrderPressureTransaction.getLastContent()[1]
        if PressureBuy == 0 and PressureSell == 0:
            FactorValue = 0
        elif PressureBuy == 0:
            FactorValue = -10
        elif PressureSell == 0:
            FactorValue = 10
        else:
            FactorValue = math.log(PressureBuy) - math.log(PressureSell)
        self.__emaOrderPressureTransactionBuy.append(PressureBuy)
        self.__emaOrderPressureTransactionSell.append(PressureSell)
        self.addData(FactorValue, self.__data.getLastTimeStamp())

    def getEmaOrderPressureTransactionBuy(self):
        return self.__emaOrderPressureTransactionBuy

    def getEmaOrderPressureTransactionSell(self):
        return self.__emaOrderPressureTransactionSell
