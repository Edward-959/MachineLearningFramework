"""
@author: 011672

计算active order 的EMA
"""

from System.Factor import Factor


class FactorEmaOrderMomentum(Factor):
    def __init__(self, para, factorManagement):
        Factor.__init__(self, para, factorManagement)

        self.__paraEmaOrderMomentumLag = para['paraEmaOrderMomentumLag']  # EMA参数

        self.__data = self.getTradingUnderlyingData(self.getIndexTradingUnderlying()[0])
        paraEmaOrderMomentum = {"name": "emaSlicePressure", "className": "Ema",
                                "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                "indexFactorUnderlying": self.getIndexFactorUnderlying(),
                                "paraLag": self.__paraEmaOrderMomentumLag,
                                "paraOriginalData": {"name": "factorOrderMomentum", "className": "FactorOrderMomentum", "indexTradingUnderlying": [0],
         "indexFactorUnderlying": []}
                                                    }
        self.__paraEmaOrderMomentum= self.getFactorData(paraEmaOrderMomentum)
        factorManagement.registerFactor(self, para)

    def calculate(self):
        self.addData(self.__paraEmaOrderMomentum.getLastContent(), self.__data.getLastTimeStamp())
