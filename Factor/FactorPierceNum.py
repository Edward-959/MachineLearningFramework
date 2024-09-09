# -*- coding: utf-8 -*-
"""
Created on Wed Aug 29 15:26:45 2017

@author: 011672
"""
# 用于计算产生新的界点后突破大单的次数

import numpy as np

from System.Factor import Factor


class FactorPierceNum(Factor):
    def __init__(self, para, factorManagement):
        Factor.__init__(self, para, factorManagement)
        self.__paraMinSupportRate = para['paraMinSupportRate']
        self.__paraMinSupportAmount = para['paraMinSupportAmount']
        self.__paraFastLag = para['paraFastLag']
        self.__paraSlowLag = para['paraSlowLag']

        self.__data = self.getTradingUnderlyingData(self.getIndexTradingUnderlying()[0])
        self.__extremePoint = self.getFactorData({"name": "extremePoint", "className": "ExtremePoint",
                                                  "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                                  "indexFactorUnderlying": self.getIndexFactorUnderlying(),
                                                  "paraFastLag": self.__paraFastLag, "paraSlowLag": self.__paraSlowLag})
        self.__orderEvaluate = self.getFactorData({"name": "orderEvaluate", "className": "OrderEvaluate",
                                                   "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                                   "indexFactorUnderlying": self.getIndexFactorUnderlying()})
        factorManagement.registerFactor(self, para)
        self.__JudgeBoardNew = 0
        self.__JudgeBoardOld = 0
        self.__SupportPositionOld = []
        self.__PierceNum = 0

    def calculate(self):
        extremePointInfo = self.__extremePoint.getExtremePointInfo()
        if extremePointInfo.__len__() >= 1:  # 产生第一个界点
            lastData = self.__data.getLastContent()
            lastOrderBook = self.__orderEvaluate.getOrderBook()[-1]
            if self.__extremePoint.getUpdateStatus() == 1:  # 产生新的界点
                self.__JudgeBoardNew = -extremePointInfo[-1][0]
            if self.__JudgeBoardOld == 0:
                self.__JudgeBoardOld = self.__JudgeBoardNew

            # 下跌过程
            if self.__JudgeBoardOld == self.__JudgeBoardNew and self.__JudgeBoardNew == -1:
                bidprice = np.array(lastData.bidPrice)
                bidvolume = np.array(lastData.bidVolume)
                SupportPosition = []
                for i in range(self.__SupportPositionOld.__len__()):
                    orderPierce = False
                    for ii in range(lastOrderBook.__len__()):
                        if lastOrderBook[ii][3] == 'S' and lastOrderBook[ii][1] <= self.__SupportPositionOld[i]:
                            orderPierce = True
                            break
                    if orderPierce:
                        if self.__SupportPositionOld[i] not in bidprice:
                            self.__PierceNum += 1  # 如果原有大单位置被跌破，且该位置不在当前买盘，则次数加1
                        else:
                            SupportPosition.append(self.__SupportPositionOld[i])  # 如果原有大单位置被跌破，但该位置在当前买盘，则保留该位置
                averageVolume = np.mean(np.sort(bidvolume)[2:8])
                tempId = []
                for ii in range(10):
                    if bidvolume[ii] >= self.__paraMinSupportRate * averageVolume and \
                                            bidvolume[ii] * bidprice[ii] >= self.__paraMinSupportAmount * 10000:  # 大单的判定条件
                        tempId.append(ii)
                tempId2 = []
                if tempId.__len__() >= 2:
                    for ii in range(1, tempId.__len__()):
                        if tempId[ii] - tempId[ii - 1] > 1:
                            tempId2.append(tempId[ii - 1])  # 连续价位大单去重
                    tempId2.append(tempId[-1])
                else:
                    tempId2 = tempId
                for ii in range(tempId2.__len__()):
                    if bidprice[tempId2[ii]] not in SupportPosition:
                        SupportPosition.append(bidprice[tempId2[ii]])  # 添加新的大单
                self.__SupportPositionOld = SupportPosition[:]
                self.addData(self.__PierceNum, self.__data.getLastTimeStamp())

            # 上涨过程
            elif self.__JudgeBoardOld == self.__JudgeBoardNew and self.__JudgeBoardNew == 1:
                askprice = np.array(lastData.askPrice)
                askvolume = np.array(lastData.askVolume)
                SupportPosition = []
                for i in range(self.__SupportPositionOld.__len__()):
                    orderPierce = False
                    for ii in range(lastOrderBook.__len__()):
                        if lastOrderBook[ii][3] == 'B' and lastOrderBook[ii][1] >= self.__SupportPositionOld[i]:
                            orderPierce = True
                            break
                    if orderPierce:
                        if self.__SupportPositionOld[i] not in askprice:
                            self.__PierceNum -= 1  # 如果原有大单位置被涨破，且该位置不在当前卖盘，则次数减1
                        else:
                            SupportPosition.append(self.__SupportPositionOld[i])  # 如果原有大单位置被涨破，但该位置在当前卖盘，则保留该位置
                averageVolume = np.mean(np.sort(askvolume)[2:8])
                tempId = []
                for ii in range(10):
                    if askvolume[ii] >= self.__paraMinSupportRate * averageVolume and \
                                            askvolume[ii] * askprice[ii] >= self.__paraMinSupportAmount * 10000:
                        tempId.append(ii)
                tempId2 = []
                if tempId.__len__() >= 2:
                    for ii in range(1, tempId.__len__()):
                        if tempId[ii] - tempId[ii - 1] > 1:
                            tempId2.append(tempId[ii - 1])
                    tempId2.append(tempId[-1])
                else:
                    tempId2 = tempId
                for ii in range(tempId2.__len__()):
                    if askprice[tempId2[ii]] not in SupportPosition:
                        SupportPosition.append(askprice[tempId2[ii]])
                self.__SupportPositionOld = SupportPosition[:]
                self.addData(self.__PierceNum, self.__data.getLastTimeStamp())

            else:
                self.__SupportPositionOld = []
                self.__PierceNum = 0
                self.addData(0, self.__data.getLastTimeStamp())

            self.__JudgeBoardOld = self.__JudgeBoardNew

        else:
            self.addData(0, self.__data.getLastTimeStamp())
