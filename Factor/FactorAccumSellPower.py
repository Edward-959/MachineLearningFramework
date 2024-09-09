# -*- coding: utf-8 -*-
"""
Created on 2018/7/11 18:48
@author: 011672
@revised by 006566 2018/7/25
"""

from System.Factor import Factor


class FactorAccumSellPower(Factor):
    def __init__(self, para, factorManagement):
        Factor.__init__(self, para, factorManagement)
        self.__paraMAVolumeLag = para["paraMAVolumeLag"]

        self.__data = self.getTradingUnderlyingData(self.getIndexTradingUnderlying()[0])

        self.__historyVolume = self.getFactorData({"name": "historyVolume", "className": "HistoryVolume",
                                                   "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                                   "indexFactorUnderlying": self.getIndexFactorUnderlying()})
        paraOrderEvaluate = {"name": "orderEvaluate", "className": "OrderEvaluate2",
                             "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                             "indexFactorUnderlying": self.getIndexFactorUnderlying()}

        self.__paraOrderEvaluate = self.getFactorData(paraOrderEvaluate)
        factorManagement.registerFactor(self, para)

    def calculate(self):
        accAskAmount = self.__paraOrderEvaluate.getAccAmountSell()[-1]
        if len(self.__historyVolume.getContent()) <= self.__paraMAVolumeLag:
            FactorValue = float(len(self.__historyVolume.getContent()) * accAskAmount) / sum(self.__historyVolume.getContent())
        else:
            FactorValue = float(self.__paraMAVolumeLag * accAskAmount) / sum(self.__historyVolume.getContent()[-self.__paraMAVolumeLag:])
        self.addData(FactorValue, self.__data.getLastTimeStamp())
