# -*- coding: utf-8 -*-
# @Time    : 2018/7/11 10:30
# @Author  : 011672
# @File    : FactorSellPresure.py
from System.Factor import Factor
import math
import numpy as np


class FactorSellDistribution(Factor):
    def __init__(self, para, factorManagement):
        Factor.__init__(self, para, factorManagement)
        self.__data = self.getTradingUnderlyingData(self.getIndexTradingUnderlying()[0])
        self.__transaction_distribution=self.getFactorData({'name':'transactionDistribution',
                                                            'className':'TransactionDistribution',
                                                            "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                                            "indexFactorUnderlying": self.getIndexFactorUnderlying()
                                                            })
        self.__n=para['paraLag']
        factorManagement.registerFactor(self, para)

    def calculate(self):
        result=self.ema(self.getContent(),self.__transaction_distribution.getLastContent()[2],self.__n)
        self.addData(result,self.__data.getLastTimeStamp())

    @staticmethod
    def ema(content_list,value,n):
        alpha = 2 / (n + 1)
        if len(content_list) == 0:
            ema_pre = value
        else:
            ema_pre = content_list[-1]
        ema_new = value * alpha + ema_pre * (1 - alpha)
        return(ema_new)