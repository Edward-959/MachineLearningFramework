# -*- coding: utf-8 -*-
"""
Created on 2018/4/12
@author: 011672
"""


from System.Factor import Factor
import numpy as np

class FactorDistanceToVwap(Factor):
    def __init__(self, para, factorManagement):
        Factor.__init__(self, para, factorManagement)
        self.__paraLag = para["paraLag"]

        self.__data = self.getTradingUnderlyingData(self.getIndexTradingUnderlying()[0])
        self.__midPrice = self.getFactorData({"name": "midPrice", "className": "MidPrice",
                                              "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                              "indexFactorUnderlying": self.getIndexFactorUnderlying()})
        factorManagement.registerFactor(self, para)

    def calculate(self):
        lastData = self.__data.getLastContent()
        distance = 0
        if len(self.__midPrice.getContent()) > self.__paraLag:
            compareData = self.__data.getContent()[-self.__paraLag]
            if (lastData.totalVolume - compareData.totalVolume) == 0:
                distance = 0
            else:
                ave_price = (lastData.totalAmount - compareData.totalAmount) / (lastData.totalVolume
                                                                                - compareData.totalVolume)
                distance = self.__midPrice.getLastContent() / ave_price - 1
        self.addData(distance, lastData.timeStamp)


