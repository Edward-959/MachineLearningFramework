# -*- coding: utf-8 -*-
"""
Created on 2018/6/12 14:41
读取NonFactor下的ActiveVol, 然后分别输出
"BS"可取3个值——B：买量； S：卖量； Net：净买量
@author: 011672
"""
from System.Factor import Factor


class FactorActiveVol(Factor):
    def __init__(self, para, factorManagement):  # 传入因子参数,归属的因子管理模块，需要用到的其他因子或非因子
        Factor.__init__(self, para, factorManagement)
        self.__data = self.getTradingUnderlyingData(self.getIndexTradingUnderlying()[0])
        self.__benchmarkPriceType = para["benchmarkPriceType"]
        self.__benchmarkPriceLag = para["benchmarkPriceLag"]
        self.__BS = para["BS"]  # "BS"可取3个值——B：买量； S：卖量； Net：净买量
        paraActiveVol = {"name": "activeVol", "className": "ActiveVol",
                         "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                         "indexFactorUnderlying": self.getIndexFactorUnderlying(),
                         "benchmarkPriceType": self.__benchmarkPriceType,
                         "benchmarkPriceLag": self.__benchmarkPriceLag}
        self.__activeVol = self.getFactorData(paraActiveVol)
        factorManagement.registerFactor(self, para)

    def calculate(self):
        if self.__activeVol.getLastContent().__len__() > 0:
            if self.__BS == "B":
                factorValue = self.__activeVol.getLastContent()[0]
            elif self.__BS == "S":
                factorValue = self.__activeVol.getLastContent()[1]
            elif self.__BS == "Net":
                factorValue = self.__activeVol.getLastContent()[2]
        else:
            factorValue = 0

        self.addData(factorValue, self.__data.getLastTimeStamp())
