"""
@author: 011672
计算当前中间价相对于全天成交均价的距离，即相对于黄色均线的位置
@ revised by 006566 on 2018/7/26
"""

from System.Factor import Factor


class FactorDistanceToAvePrice(Factor):
    def __init__(self, para, factorManagement):
        Factor.__init__(self, para, factorManagement)

        self.__data = self.getTradingUnderlyingData(self.getIndexTradingUnderlying()[0])
        self.__midPrice = self.getFactorData({"name": "midPrice", "className": "MidPrice",
                                              "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                              "indexFactorUnderlying": self.getIndexFactorUnderlying()})
        self.__avePrice = self.getFactorData({"name": "avePrice", "className": "AvePrice",
                                              "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                              "indexFactorUnderlying": self.getIndexFactorUnderlying()})

        factorManagement.registerFactor(self, para)

    def calculate(self):
        midPrice = self.__midPrice.getLastContent()
        avePrice = self.__avePrice.getLastContent()
        if avePrice > 0:
            value = midPrice / avePrice - 1
        else:
            value = 0
        self.addData(value, self.__midPrice.getLastTimeStamp())
