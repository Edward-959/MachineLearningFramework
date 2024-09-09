# -*- coding: utf-8 -*-
"""
Created on 2018/4/12
@author: 011672
"""


from System.Factor import Factor
import numpy as np

class FactorDistanceToLow(Factor):
    def __init__(self, para, factorManagement):
        Factor.__init__(self, para, factorManagement)
        self.__paraLag = para["paraLag"]

        self.__midPrice = self.getFactorData({"name": "midPrice", "className": "MidPrice",
                                              "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                              "indexFactorUnderlying": self.getIndexFactorUnderlying()})

        factorManagement.registerFactor(self, para)

    def calculate(self):
        distance = 0
        if len(self.__midPrice.getContent()) > self.__paraLag:
            if min(self.__midPrice.getContent()[-self.__paraLag:])!=0:
                distance = self.__midPrice.getLastContent() / min(self.__midPrice.getContent()[-self.__paraLag:]) - 1
        self.addData(distance, self.__midPrice.getLastTimeStamp())
