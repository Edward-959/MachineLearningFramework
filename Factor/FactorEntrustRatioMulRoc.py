# -*- coding: utf-8 -*-
"""
Created on 2018/4/12
@author: 011672
"""


from System.Factor import Factor
from scipy import *
import numpy as np
import scipy.stats.stats as stats


class FactorEntrustRatioMulRoc(Factor):
    def __init__(self, para, factorManagement):
        Factor.__init__(self, para, factorManagement)
        self.__paraLag = para["paraLag"]

        self.__midPrice = self.getFactorData({"name": "midPrice", "className": "MidPrice",
                                              "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                              "indexFactorUnderlying": self.getIndexFactorUnderlying()})

        paraEmaMidPrice = {"name": "emaMidPrice", "className": "Ema",
                           "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                           "indexFactorUnderlying": self.getIndexFactorUnderlying(),
                           "paraLag": self.__paraLag,
                           "paraOriginalData": {"name": "midPrice", "className": "MidPrice",
                                                "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                                "indexFactorUnderlying": self.getIndexFactorUnderlying()}}

        self.__emaMidPrice = self.getFactorData(paraEmaMidPrice)
        factorManagement.registerFactor(self, para)

    def calculate(self):
        er = 0
        factor = 0
        if len(self.__midPrice.getContent()) > self.__paraLag:
            price_list = self.__midPrice.getContent()[-self.__paraLag:]
            price_pre = price_list[:-1]
            price_after = price_list[1:]
            price_gap = list(np.array(price_after) - np.array(price_pre))
            sum = 0
            for data in price_gap:
                sum = sum + abs(data)
            if sum!=0:
                er = (price_list[-1]-price_list[0])/sum
            else:
                er=0

            if np.isnan(er) or (er < 0.001 and er > -0.001):
                er = 0
            lastFactorSpeed = 0
            if len(self.__emaMidPrice.getContent()) > self.__paraLag:
                lastFactorSpeed = (self.__emaMidPrice.getLastContent() / self.__emaMidPrice.getContent()[
                    int(-1 - self.__paraLag)] - 1) / (self.__paraLag / 20)

            factor = er * lastFactorSpeed

        self.addData(factor, self.__midPrice.getLastTimeStamp())
