#
"""
@author: 011672

计算当前时间段成交量相对于买卖盘的大小
"""

from System.Factor import Factor
import math
import numpy as np

# {"name": "factorBuyPower", "className": "FactorBuyPower",
#          "indexTradingUnderlying": [0], "indexFactorUnderlying": [],
#          "paraNumOrderMax": 7, "paraNumOrderMin": 4,
#          "paraLag": 3, "save": True}
#
#
#
# {"name": "factorEmaAskHugeOrderMultiple2", "className": "FactorEmaAskHugeOrderMultiple",
#          "indexTradingUnderlying": [0], "indexFactorUnderlying": [],
#          "paraLag": 2, "paraNumOrderMax": 7, "paraNumOrderMin": 4, "paraNumOrderMaxForAveOrderVolume": 10,
#          "paraNumOrderMinForAveOrderVolume": 1, "paraEmaAveOrderVolumeLag": null, "save": true},

class FactorBuyPower(Factor):
    def __init__(self, para, factorManagement):
        Factor.__init__(self, para, factorManagement)
        self.__paraNumOrderMax = para['paraNumOrderMax']
        self.__paraNumOrderMin = para['paraNumOrderMin']
        self.__paraLag = para['paraLag']
        self.__data = self.getTradingUnderlyingData(self.getIndexTradingUnderlying()[0])

        self.__aveOrderVolume = self.getFactorData({"name": "aveOrderVolume", "className": "AveOrderVolume",
                                                   "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                                   "indexFactorUnderlying": self.getIndexFactorUnderlying(),
                                                   "paraNumOrderMax": self.__paraNumOrderMax,
                                                    "paraNumOrderMin": self.__paraNumOrderMin})
        factorManagement.registerFactor(self, para)

    def calculate(self):
        lastData = self.__data.getLastContent()
        buyPower = 0
        if len(self.__data.getContent()) > self.__paraLag:
            compareData = self.__data.getContent()[int(-self.__paraLag)]
            volume = 0
            if lastData.totalAmount - compareData.totalAmount + 1 > 0:
                volume = math.log(lastData.totalAmount - compareData.totalAmount+1)
            rise = lastData.lastPrice - compareData.lastPrice
            aveOrderVolume = 0
            if rise > 0 or rise == 0:
                if self.__aveOrderVolume.getLastContent()[1]+1 > 0:
                    aveOrderVolume = math.log(self.__aveOrderVolume.getLastContent()[1]+1)
            else:
                if self.__aveOrderVolume.getLastContent()[0] + 1 > 0:
                    aveOrderVolume = math.log(self.__aveOrderVolume.getLastContent()[0]+1)
            if aveOrderVolume != 0:
                buyPower = np.true_divide(rise*volume, aveOrderVolume)
        self.addData(buyPower, lastData.timeStamp)

