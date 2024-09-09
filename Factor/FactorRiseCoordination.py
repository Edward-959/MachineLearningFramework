# -*- coding: utf-8 -*-
"""
Created on 2018/4/12
@author: 011672
"""


from System.Factor import Factor
from scipy import *
import numpy as np
import scipy.stats.stats as stats
import scipy.stats.stats as stats
import operator as op


class FactorRiseCoordination(Factor):
    def __init__(self, para, factorManagement):
        Factor.__init__(self, para, factorManagement)
        self.__paraLag = para["paraLag"]

        self.__midPrice = self.getFactorData({"name": "midPrice", "className": "MidPrice",
                                              "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                              "indexFactorUnderlying": self.getIndexFactorUnderlying()})
        factorManagement.registerFactor(self, para)
        self.__tick = 0

    def calculate(self):
        self.__tick += 1
        if self.__tick == 1638:
            print("")

        r = 0
        if len(self.__midPrice.getContent()) > self.__paraLag:
            price_list = self.__midPrice.getContent()[-self.__paraLag:]
            price_list_rank = list(np.sort(price_list))

            if op.eq(price_list, price_list_rank):
                r = 1
            else:
                r, _ = stats.pearsonr(price_list, price_list_rank)
            if np.isnan(r) or (r<0.001 and r>-0.001) :
                r=0
            
        self.addData(r, self.__midPrice.getLastTimeStamp())
