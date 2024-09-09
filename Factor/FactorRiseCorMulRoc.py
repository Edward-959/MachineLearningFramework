# -*- coding: utf-8 -*-
"""
Created on 2018/4/17
@author: 011672
"""


from System.Factor import Factor
from scipy import *
import numpy as np
import scipy.stats.stats as stats
import scipy.stats.stats as stats
import operator as op


class FactorRiseCorMulRoc(Factor):
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
        r = 0
        factor = 0
        if len(self.__midPrice.getContent()) > self.__paraLag:
            price_list = self.__midPrice.getContent()[-self.__paraLag:]
            price_list_rank = list(np.sort(price_list))
            if op.eq(price_list, price_list_rank):
                r = 1
            else:
                r, _ = stats.pearsonr(price_list, price_list_rank)
            if np.isnan(r) or (r<0.001 and r>-0.001) :
                r=0

        lastFactorSpeed = 0
        if len(self.__emaMidPrice.getContent()) > self.__paraLag:
            lastFactorSpeed = (self.__emaMidPrice.getLastContent() / self.__emaMidPrice.getContent()[
                int(-1 - self.__paraLag)] - 1) / (self.__paraLag / 20)

        factor = r*lastFactorSpeed

        self.addData(factor, self.__midPrice.getLastTimeStamp())