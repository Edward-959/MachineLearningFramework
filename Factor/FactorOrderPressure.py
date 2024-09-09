"""
@author: 011672

根据买卖压力的EMA计算买卖压力的比较
"""

from System.Factor import Factor
import math


class FactorOrderPressure(Factor):
    def __init__(self, para, factorManagement):
        Factor.__init__(self, para, factorManagement)
        self.__paraOrderPressureLag = para['paraOrderPressureLag']

        self.__data = self.getTradingUnderlyingData(self.getIndexTradingUnderlying()[0])
        paraEmaOrderPressure = {"name": "emaOrderPressure", "className": "Ema",
                                "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                "indexFactorUnderlying": self.getIndexFactorUnderlying(),
                                "paraLag": self.__paraOrderPressureLag,
                                "paraOriginalData": {"name": "orderEvaluate", "className": "OrderEvaluate",
                                                     "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                                     "indexFactorUnderlying": self.getIndexFactorUnderlying()}}
        self.__emaOrderPressure = self.getFactorData(paraEmaOrderPressure)  # 取OrderEvaluate中计算的买卖压的EMA
        factorManagement.registerFactor(self, para)
        self.__emaOrderPressureBuy = []
        self.__emaOrderPressureSell = []

    def calculate(self):
        PressureBuy = self.__emaOrderPressure.getLastContent()[0]
        PressureSell = self.__emaOrderPressure.getLastContent()[1]
        if PressureBuy == 0 and PressureSell == 0:
            FactorValue = 0
        elif PressureBuy == 0:
            FactorValue = -10
        elif PressureSell == 0:
            FactorValue = 10
        else:
            FactorValue = math.log(PressureBuy) - math.log(PressureSell)
        self.__emaOrderPressureBuy.append(PressureBuy)
        self.__emaOrderPressureSell.append(PressureSell)
        self.addData(FactorValue, self.__data.getLastTimeStamp())

    def getEmaOrderPressureBuy(self):
        return self.__emaOrderPressureBuy

    def getEmaOrderPressureSell(self):
        return self.__emaOrderPressureSell
