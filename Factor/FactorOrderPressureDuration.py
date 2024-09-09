"""
@author: 011672

买卖压力持续时间，单位为秒
买压较强时，持续时间显示为正
卖压较强时，持续时间显示为负
"""

from System.Factor import Factor
import time


class FactorOrderPressureDuration(Factor):
    def __init__(self, para, factorManagement):
        Factor.__init__(self, para, factorManagement)
        self.__paraOrderPressureLag = para['paraOrderPressureLag']
        self.__paraHorizon = para['paraHorizon']

        self.__data = self.getTradingUnderlyingData(self.getIndexTradingUnderlying()[0])
        self.__orderPressure = self.getFactorData({"name": "factorOrderPressure", "className": "FactorOrderPressure",
                                                   "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                                   "indexFactorUnderlying": self.getIndexFactorUnderlying(),
                                                   "paraOrderPressureLag": self.__paraOrderPressureLag})
        factorManagement.registerFactor(self, para)

    def calculate(self):
        TempDuration = 0
        if self.getContent().__len__() >= 1:
            datanow = self.__orderPressure.getLastContent() - self.__paraHorizon
            datalast = self.__orderPressure.getContent()[-2] - self.__paraHorizon
            timenow = self.__data.getLastTimeStamp()
            timelast = self.__data.getTimeStamp()[-2]
            if datanow > 0 and datalast > 0:  # 买压持续较强
                TempDuration = self.getLastContent() + self.getTimeLength(timelast, timenow)
            elif datanow < 0 and datalast < 0:  # 卖压持续较强
                TempDuration = self.getLastContent() - self.getTimeLength(timelast, timenow)
        self.addData(TempDuration, self.__data.getLastTimeStamp())
