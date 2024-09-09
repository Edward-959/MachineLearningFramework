# -*- coding: utf-8 -*-
"""
Created on 2017/8/30 13:26

@author: 011672
"""
import numpy as np
from System.Factor import Factor


class FactorBreakHugeBidOrder(Factor):
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
            BidVolumePre = np.array(self.__data.getContent()[-2].bidVolume)
            BidPricePre = np.array(self.__data.getContent()[-2].bidPrice)
            BidVolumePre = BidVolumePre[BidVolumePre > 0]
            BidPricePre = BidPricePre[BidPricePre > 0]
            if len(BidVolumePre) < 10 or len(BidPricePre) < 10:
                factorValue = 0
                self.__OldTargetVolume = 0
                self.__OldTargetPrice = 0
            else:
                SortedBidVolumePre = np.sort(BidVolumePre)
                BidVolumePreId = np.argsort(BidVolumePre)
                tempJudge1 = SortedBidVolumePre >= max(
                    [self.__OldTargetVolume * self.__paraOldTargetVolumeShrink,
                     self.__paraMinPressureRate * min([np.mean(SortedBidVolumePre[2:8]),
                                                       self.__emaAveOrderVolume.getLastContent()[0]])])
                tempJudge2 = SortedBidVolumePre * BidPricePre[BidVolumePreId] >= self.__paraMinPressureAmount * 10000

                ###########################################################################
                # tempTargetId = BidVolumePreId[tempJudge1.tolist() or tempJudge2.tolist()]
                # 取逻辑或运算，不能用list的方式进行
                tempTargetId = []
                for i in range(len(tempJudge1)):
                    if(tempJudge1[i] or tempJudge2[i]):
                        tempTargetId.append(BidVolumePreId[i])
                ###########################################################################

                if tempTargetId.__len__() == 0:
                    TargetId = []
                else:
                    tempTargetId.sort()
                    tempTargetId2 = []
                    if tempTargetId.__len__() >= 2:
                        for i in range(tempTargetId.__len__() - 1):
                            if 1 - BidPricePre[tempTargetId[i + 1]] / BidPricePre[tempTargetId[i]] \
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
                    TargetVolume = BidVolumePre[TargetId[0]]
                    TargetPrice = BidPricePre[TargetId[0]]
                    OldPosition = np.argwhere(BidPricePre == self.__OldTargetPrice)
                    if self.__OldTargetVolume > 0 and OldPosition.__len__() > 0:
                        if (OldPosition[0][0] == TargetId[0] and TargetVolume < self.__OldTargetVolume) or \
                                (OldPosition[0][0] > TargetId[0]):
                            TargetVolume = self.__OldTargetVolume
                            TargetPrice = self.__OldTargetPrice

                    self.__OldTargetPrice = TargetPrice
                    self.__OldTargetVolume = TargetVolume
                else:
                    OldPosition = np.argwhere(BidPricePre == self.__OldTargetPrice)
                    if OldPosition.__len__() == 0:
                        self.__OldTargetVolume = 0
                        self.__OldTargetPrice = 0
                OrderNow = self.__orderEvaluate.getOrderBook()[-1]
                tempJudge = 0
                if OrderNow.__len__() > 1:
                    for i in range(OrderNow.__len__()):
                        if OrderNow[i][1] <= self.__OldTargetPrice and OrderNow[i][3] == "S" and \
                                        self.__OldTargetPrice > 0 and OrderNow[i][0] == self.__data.getLastTimeStamp():
                            tempJudge = 1
                if tempJudge == 1:
                    tempBidOrderV = np.array(self.__data.getContent()[-1].bidVolume)
                    tempBidOrderP = np.array(self.__data.getContent()[-1].bidPrice)
                    tempBidOrderV = tempBidOrderV[tempBidOrderV > 0]
                    tempBidOrderP = tempBidOrderP[tempBidOrderP > 0]
                    if tempBidOrderP.__len__() > 0:
                        if tempBidOrderP[0] < self.__OldTargetPrice or \
                                        tempBidOrderV[tempBidOrderP == self.__OldTargetPrice] <= \
                                        self.__paraTargetVolumeLeft * self.__OldTargetVolume:
                            factorValue = self.__OldTargetVolume / self.__emaAveOrderVolume.getLastContent()[0]
                            self.__OldTargetVolume = 0
                            self.__OldTargetPrice = 0
        self.addData(factorValue, self.__data.getLastTimeStamp())
