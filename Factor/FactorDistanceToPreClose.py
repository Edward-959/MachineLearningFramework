# -*- coding: utf-8 -*-
"""
Created on 2018/4/12
@author: 011672
"""
import numpy as np
from System.Factor import Factor


class FactorDistanceToPreClose(Factor):
    def __init__(self, para, factorManagement):
        Factor.__init__(self, para, factorManagement)

        self.__data = self.getTradingUnderlyingData(self.getIndexTradingUnderlying()[0])
        self.__midPrice = self.getFactorData({"name": "midPrice", "className": "MidPrice",
                                              "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                              "indexFactorUnderlying": self.getIndexFactorUnderlying()})
        factorManagement.registerFactor(self, para)

    def calculate(self):
        lastData = self.__data.getLastContent()
        close = lastData.previousClosingPrice
        distance = self.__midPrice.getLastContent() / close - 1
        
        if np.isnan(distance) or (distance<0.001 and distance>-0.001) :
            distance=0

        self.addData(distance, lastData.timeStamp)
