"""
@author: 011672

计算盘口挂单买卖压力的EMA
"""

from System.Factor import Factor


class FactorEmaSlicePressure(Factor):
    def __init__(self, para, factorManagement):
        Factor.__init__(self, para, factorManagement)
        self.__paraNumOrderMax = para['paraNumOrderMax']  # 比较盘口档位数
        self.__paraNumOrderMin = para['paraNumOrderMin']  # 比较盘口档位数
        self.__paraEmaSlicePressureLag = para['paraEmaSlicePressureLag']  # EMA参数

        self.__data = self.getTradingUnderlyingData(self.getIndexTradingUnderlying()[0])
        paraEmaSlicePressure = {"name": "emaSlicePressure", "className": "Ema",
                                "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                "indexFactorUnderlying": self.getIndexFactorUnderlying(),
                                "paraLag": self.__paraEmaSlicePressureLag,
                                "paraOriginalData": {"name": "slicePressure", "className": "SlicePressure",
                                                     "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                                     "indexFactorUnderlying": self.getIndexFactorUnderlying(),
                                                     "paraNumOrderMax": self.__paraNumOrderMax,
                                                     "paraNumOrderMin": self.__paraNumOrderMin}}
        self.__emaSlicePressure = self.getFactorData(paraEmaSlicePressure)
        factorManagement.registerFactor(self, para)

    def calculate(self):
        self.addData(-self.__emaSlicePressure.getLastContent(), self.__data.getLastTimeStamp())
