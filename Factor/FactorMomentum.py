# -*- coding: utf-8 -*-
"""
@author: 011672
"""
from System.Factor import Factor
import math

#
# {"name": "factorMomentum", "className": "FactorMomentum",
#          "indexTradingUnderlying": [0], "indexFactorUnderlying": [],
#          "paraLag": 3, "paraEmaMidPriceLag": 3, "save": True}


class FactorMomentum(Factor):  # 因子类
    def __init__(self, para, factorManagement):  # 传入因子参数,归属的因子管理模块，需要用到的其他因子或非因子
        Factor.__init__(self, para, factorManagement)
        # 因子参数
        self.__paraEmaMidPriceLag = para['paraEmaMidPriceLag']
        self.__paraLag = para['paraLag']
        # 因子计算会用到的中间变量,取数据时候要注意会不会出现取出的因子还没有计算出值
        # 如果需要实例化因子作为中间变量，则name不要以factor开头，否则会输出到最终的结果中
        # 如果需要实例化因子或者非因子，需要考虑注册因子的先后顺序，即factorManagement.registerFactor(self)
        self.__data = self.getTradingUnderlyingData(self.getIndexTradingUnderlying()[0])
        paraEmaMidPrice = {"name": "emaMidPrice", "className": "Ema",
                           "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                           "indexFactorUnderlying": self.getIndexFactorUnderlying(),
                           "paraLag": self.__paraEmaMidPriceLag,
                           "paraOriginalData": {"name": "midPrice", "className": "MidPrice",
                                                "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                                "indexFactorUnderlying": self.getIndexFactorUnderlying()}}
        self.__emaMidPrice = self.getFactorData(paraEmaMidPrice)
        factorManagement.registerFactor(self, para)
        self.__data = self.getTradingUnderlyingData(self.getIndexTradingUnderlying()[0])

    def calculate(self):
        lastFactorSpeed = 0
        factormomentum = 0
        if len(self.__emaMidPrice.getContent()) > self.__paraEmaMidPriceLag and len(self.__data.getContent()) > self.__paraLag:
            if self.__emaMidPrice.getContent()[int(-1 - self.__paraLag)] != 0:
                lastFactorSpeed = (self.__emaMidPrice.getLastContent() / self.__emaMidPrice.getContent()[
                    int(-1 - self.__paraLag)] - 1) / (self.__paraLag / 20)
            lastData = self.__data.getLastContent()
            compareData = self.__data.getContent()[int(-self.__paraLag)]
            volume = 0
            if lastData.totalAmount - compareData.totalAmount + 1 > 0:
                volume = math.log(lastData.totalAmount - compareData.totalAmount + 1)
            factormomentum = lastFactorSpeed * volume
        self.addData(factormomentum, self.__data.getLastTimeStamp())
