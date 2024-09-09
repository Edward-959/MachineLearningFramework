# -*- coding: utf-8 -*-
"""
Created on 2017/12/13 9:47

@author: 011672
"""
# 计算当前中间价相对于EMA价的相对距离
# 计算方式为:(中间价-EMA价)/移动平均价
from System.Factor import Factor


class FactorDistanceToEMAPrice(Factor):
    def __init__(self, para, factorManagement):
        Factor.__init__(self, para, factorManagement)
        self.__paraEMALag = para["paraEMALag"]

        self.__midPrice = self.getFactorData({"name": "midPrice", "className": "MidPrice",
                                              "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                              "indexFactorUnderlying": self.getIndexFactorUnderlying()})
        paraEMAPrice = {"name": "EMAPrice", "className": "Ema",
                        "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                        "indexFactorUnderlying": self.getIndexFactorUnderlying(),
                        "paraLag": self.__paraEMALag,
                        "paraOriginalData": {"name": "midPrice", "className": "MidPrice",
                                             "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                             "indexFactorUnderlying": self.getIndexFactorUnderlying()}}
        self.__EMAPrice = self.getFactorData(paraEMAPrice)

        factorManagement.registerFactor(self, para)

    def calculate(self):
        midPrice = self.__midPrice.getLastContent()
        emaPrice = self.__EMAPrice.getLastContent()
        self.addData(midPrice / emaPrice - 1, self.__midPrice.getLastTimeStamp())
