# -*- coding: utf-8 -*-
"""
Created on 2017/9/7 20:12

@author: 011672
"""
from System.Factor import Factor


class FactorDistanceToBreakUpPrice(Factor):
    def __init__(self, para, factorManagement):  # 传入因子参数,归属的因子管理模块，需要用到的其他因子或非因子
        Factor.__init__(self, para, factorManagement)
        # 因子参数
        self.__paraLowestRatio = para['paraLowestRatio']
        self.__paraFastLag = para['paraFastLag']
        self.__paraSlowLag = para['paraSlowLag']
        # 因子计算会用到的中间变量,取数据时候要注意会不会出现取出的因子还没有计算出值
        # 如果需要实例化因子作为中间变量，则name不要以factor开头，否则会输出到最终的结果中
        # 如果需要实例化因子或者非因子，需要考虑注册因子的先后顺序，即factorManagement.registerFactor(self)
        self.__data = self.getTradingUnderlyingData(self.getIndexTradingUnderlying()[0])
        self.__midPrice = self.getFactorData({"name": "midPrice", "className": "MidPrice",
                                              "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                              "indexFactorUnderlying": self.getIndexFactorUnderlying()})
        self.__breakUpShape = self.getFactorData({"name": "breakUpShape", "className": "FactorBreakUpShape",
                                                  "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                                  "indexFactorUnderlying": self.getIndexFactorUnderlying(),
                                                  "paraLowestRatio": self.__paraLowestRatio,
                                                  "paraFastLag": self.__paraFastLag, "paraSlowLag": self.__paraSlowLag})
        factorManagement.registerFactor(self, para)

    def calculate(self):
        factorValue = 0.2
        breakPrice = self.__breakUpShape.getBreakPrice()[-1]
        if breakPrice != 0:
            factorValue = breakPrice / self.__midPrice.getLastContent() - 1
        self.addData(factorValue, self.__data.getLastTimeStamp())

