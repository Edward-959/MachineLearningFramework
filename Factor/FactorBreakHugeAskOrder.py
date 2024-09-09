# -*- coding: utf-8 -*-
"""
Created on 2017/8/28 16:28

@author: 011672
"""
import numpy as np
from System.Factor import Factor


class FactorBreakHugeAskOrder(Factor):
    def __init__(self, para, factorManagement):  # 传入因子参数,归属的因子管理模块，需要用到的其他因子或非因子
        Factor.__init__(self, para, factorManagement)
        # 因子参数
        self.__paraOldTargetVolumeShrink = para['paraOldTargetVolumeShrink']
        self.__paraOldTargetPriceSpace = para["paraOldTargetPriceSpace"]
        self.__paraMinPressureRate = para['paraMinPressureRate']
        self.__paraEmaAveOrderVolumeLag = para['paraEmaAveOrderVolumeLag']
        self.__paraMinPressureAmount = para['paraMinPressureAmount']
        self.__paraTargetVolumeLeft = para["paraTargetVolumeLeft"]
        self.__paraNumOrderMax = para['paraNumOrderMax']  # 比较盘口档位数
        self.__paraNumOrderMin = para['paraNumOrderMin']  # 比较盘口档位数
        # 因子计算会用到的中间变量,取数据时候要注意会不会出现取出的因子还没有计算出值
        # 如果需要实例化因子作为中间变量，则name不要以factor开头，否则会输出到最终的结果中
        # 如果需要实例化因子或者非因子，需要考虑注册因子的先后顺序，即factorManagement.registerFactor(self)
        self.__data = self.getTradingUnderlyingData(self.getIndexTradingUnderlying()[0])
        self.__orderEvaluate = self.getFactorData({"name": "orderEvaluate", "className": "OrderEvaluate",
                                                   "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                                   "indexFactorUnderlying": self.getIndexFactorUnderlying()})
        paraEmaAveOrderVolume = {"name": "emaAveOrderVolume", "className": "Ema",
                                 "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                 "indexFactorUnderlying": self.getIndexFactorUnderlying(),
                                 "paraLag": self.__paraEmaAveOrderVolumeLag,
                                 "paraOriginalData": {"name": "aveOrderVolume", "className": "AveOrderVolume",
                                                      "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                                      "indexFactorUnderlying": self.getIndexFactorUnderlying(),
                                                      "paraNumOrderMax": self.__paraNumOrderMax,
                                                      "paraNumOrderMin": self.__paraNumOrderMin}}
        self.__emaAveOrderVolume = self.getFactorData(paraEmaAveOrderVolume)
        factorManagement.registerFactor(self, para)
        self.__OldTargetVolume = 0
        self.__OldTargetPrice = 0

    def calculate(self):
        factorValue = 0.
        if len(self.__data.getContent()) >= 2:
            AskVolumePre = np.array(self.__data.getContent()[-2].askVolume)
            AskPricePre = np.array(self.__data.getContent()[-2].askPrice)
            AskVolumePre = AskVolumePre[AskVolumePre > 0]
            AskPricePre = AskPricePre[AskPricePre > 0]
            if len(AskVolumePre) < 10 or len(AskPricePre) < 10:
                factorValue = 0
                self.__OldTargetVolume = 0
                self.__OldTargetPrice = 0
            else:
                SortedAskVolumePre = np.sort(AskVolumePre)
                AskVolumePreId = np.argsort(AskVolumePre)
                tempJudge1 = SortedAskVolumePre >= max(
                    [self.__OldTargetVolume * self.__paraOldTargetVolumeShrink,
                     self.__paraMinPressureRate * min([np.mean(SortedAskVolumePre[2:8]),
                                                       self.__emaAveOrderVolume.getLastContent()[1]])])
                tempJudge2 = SortedAskVolumePre * AskPricePre[AskVolumePreId] >= self.__paraMinPressureAmount * 10000

                ###########################################################################
                # tempTargetId = AskVolumePreId[tempJudge1.tolist() or tempJudge2.tolist()]
                # 取逻辑或运算，不能用list的方式进行
                tempTargetId = []
                for i in range(len(tempJudge1)):
                    if(tempJudge1[i] or tempJudge2[i]):
                        tempTargetId.append(AskVolumePreId[i])
                ###########################################################################

                if tempTargetId.__len__() == 0:
                    TargetId = []
                else:
                    tempTargetId.sort()
                    tempTargetId2 = []
                    if tempTargetId.__len__() >= 2:
                        for i in range(tempTargetId.__len__() - 1):
                            if AskPricePre[tempTargetId[i + 1]] / AskPricePre[tempTargetId[i]] - 1 \
                                    >= self.__paraOldTargetPriceSpace:
                                tempTargetId2.append(tempTargetId[i])
                                break
                        if tempTargetId2.__len__() > 0:
                            tempTargetId = tempTargetId2
                        else:
                            tempTargetId = [max(tempTargetId)]
                    TargetId = tempTargetId
                if TargetId.__len__() == 0 and self.__OldTargetVolume == 0:
                    self.__OldTargetVolume = 0
                    self.__OldTargetPrice = 0
                elif TargetId.__len__() > 0:
                    TargetVolume = AskVolumePre[TargetId[0]]
                    TargetPrice = AskPricePre[TargetId[0]]
                    OldPosition = np.argwhere(AskPricePre == self.__OldTargetPrice)
                    if self.__OldTargetVolume > 0 and OldPosition.__len__() > 0:
                        if (OldPosition[0][0] == TargetId[0] and TargetVolume < self.__OldTargetVolume) or \
                                (OldPosition[0][0] > TargetId[0]):
                            TargetVolume = self.__OldTargetVolume
                            TargetPrice = self.__OldTargetPrice

                    self.__OldTargetPrice = TargetPrice
                    self.__OldTargetVolume = TargetVolume
                else:
                    OldPosition = np.argwhere(AskPricePre == self.__OldTargetPrice)
                    if OldPosition.__len__() == 0:
                        self.__OldTargetVolume = 0
                        self.__OldTargetPrice = 0
                OrderNow = self.__orderEvaluate.getOrderBook()[-1]
                tempJudge = 0
                if OrderNow.__len__() > 1:
                    for i in range(OrderNow.__len__()):
                        if OrderNow[i][1] >= self.__OldTargetPrice and OrderNow[i][3] == "B" and \
                                        self.__OldTargetPrice > 0 and OrderNow[i][0] == self.__data.getLastTimeStamp():
                            tempJudge = 1
                if tempJudge == 1:
                    tempAskOrderV = np.array(self.__data.getContent()[-1].askVolume)
                    tempAskOrderP = np.array(self.__data.getContent()[-1].askPrice)
                    tempAskOrderV = tempAskOrderV[tempAskOrderV > 0]
                    tempAskOrderP = tempAskOrderP[tempAskOrderP > 0]
                    if tempAskOrderP.__len__() > 0:
                        if tempAskOrderP[0] > self.__OldTargetPrice or \
                                        tempAskOrderV[tempAskOrderP == self.__OldTargetPrice] <= \
                                                self.__paraTargetVolumeLeft * self.__OldTargetVolume:
                            factorValue = self.__OldTargetVolume / self.__emaAveOrderVolume.getLastContent()[1]
                            self.__OldTargetVolume = 0
                            self.__OldTargetPrice = 0
        self.addData(factorValue, self.__data.getLastTimeStamp())
