"""
@author: 011672

计算active order 的EMA
"""

from System.Factor import Factor


class FactorEmaActiveOrder(Factor):
    def __init__(self, para, factorManagement):
        Factor.__init__(self, para, factorManagement)

        self.__paraEmaActiveOrderLag = para['paraEmaActiveOrderLag']  # EMA参数

        self.__data = self.getTradingUnderlyingData(self.getIndexTradingUnderlying()[0])
        paraEmaActiveOrder = {"name": "emaSlicePressure", "className": "Ema",
                                "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                "indexFactorUnderlying": self.getIndexFactorUnderlying(),
                                "paraLag": self.__paraEmaActiveOrderLag,
                                "paraOriginalData": {"name": "factorActiveOrder", "className": "FactorActiveOrder", "indexTradingUnderlying": [0],
         "indexFactorUnderlying": []}
                                                    }
        self.__paraEmaActiveOrder = self.getFactorData(paraEmaActiveOrder)
        factorManagement.registerFactor(self, para)

    def calculate(self):
        self.addData(self.__paraEmaActiveOrder.getLastContent(), self.__data.getLastTimeStamp())
