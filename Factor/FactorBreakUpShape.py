# -*- coding: utf-8 -*-
"""
Created on Wed Aug 23 15:29:45 2017

@author: 011672
"""
from System.Factor import Factor
import numpy as np


class FactorBreakUpShape(Factor):
    def __init__(self, para, factorManagement):  # 传入因子参数,归属的因子管理模块，需要用到的其他因子或非因子
        Factor.__init__(self, para, factorManagement)
        # 因子参数
        self.__paraLowestRatio = para['paraLowestRatio']
        self.__paraFastLag = para['paraFastLag']
        self.__paraSlowLag = para['paraSlowLag']
        # 因子计算会用到的中间变量,取数据时候要注意会不会出现取出的因子还没有计算出值
        # 如果需要实例化因子作为中间变量，则name不要以factor开头，否则会输出到最终的结果中
        # 如果需要实例化因子或者非因子，需要考虑注册因子的先后顺序，即factorManagement.registerFactor(self)
        self.__data = self.getTradingUnderlyingData(self.getIndexTradingUnderlying()[0])
        self.__midPrice = self.getFactorData({"name": "midPrice", "className": "MidPrice",
                                              "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                              "indexFactorUnderlying": self.getIndexFactorUnderlying()})
        self.__extremePoint = self.getFactorData({"name": "extremePoint", "className": "ExtremePoint",
                                                  "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                                  "indexFactorUnderlying": self.getIndexFactorUnderlying(),
                                                  "paraFastLag": self.__paraFastLag, "paraSlowLag": self.__paraSlowLag})
        self.__breakPrice = []
        factorManagement.registerFactor(self, para)

    def calculate(self):
        lines = []
        if self.__extremePoint.getUpdateStatus() == 1:
            tempLinesEnd = []
            tempLinesStart = []
            extremePointInfo = self.__extremePoint.getExtremePointInfo()
            length = len(extremePointInfo)
            if length >= 2:
                for i in range(1, length):
                    if extremePointInfo[i][0] == 1:
                        for j in range(0, i):
                            tempMinPrice = extremePointInfo[j][1]
                            tempMaxPrice = extremePointInfo[j][1]
                            for k in range(j, i + 1):
                                if extremePointInfo[k][1] < tempMinPrice:
                                    tempMinPrice = extremePointInfo[k][1]
                                if extremePointInfo[k][1] > tempMaxPrice:
                                    tempMaxPrice = extremePointInfo[k][1]
                            if extremePointInfo[j][0] == -1 and tempMinPrice == extremePointInfo[j][1] and \
                                    tempMaxPrice == extremePointInfo[i][1]:
                                tempMinPrice = extremePointInfo[i][1]
                                tempMaxPrice = extremePointInfo[i][1]
                                for k in range(i, length):
                                    if extremePointInfo[k][1] < tempMinPrice:
                                        tempMinPrice = extremePointInfo[k][1]
                                    if extremePointInfo[k][1] > tempMaxPrice:
                                        tempMaxPrice = extremePointInfo[k][1]
                                if tempMinPrice >= (
                                        (1 - self.__paraLowestRatio) * extremePointInfo[j][1] + self.__paraLowestRatio *
                                        extremePointInfo[i][1]) and tempMaxPrice == extremePointInfo[i][1]:
                                    # if extremePointInfo[i][1] / extremePointInfo[j][1] - 1 >= self.__paraIncreaseRate:
                                        tempLinesEnd.append(extremePointInfo[i][1])
                                        tempLinesStart.append(extremePointInfo[j][1])
                if len(tempLinesEnd) >= 1:
                    uniqueLinesEnd = list(set(tempLinesEnd))
                    for i in range(len(uniqueLinesEnd)):
                        linesEnd = uniqueLinesEnd[i]
                        tempIndex = np.argwhere(np.array(tempLinesEnd) == linesEnd)
                        tempLinesStart2 = []
                        for j in tempIndex:
                            tempLinesStart2.append(tempLinesStart[j[0]])
                        linesStart = min(tempLinesStart2)
                        lines.append([linesEnd, linesStart])
            if len(lines) == 0:
                self.addData(0., self.__data.getLastTimeStamp())
                self.__breakPrice.append(0)
            else:
                factorValue = 1
                breakPrice = 0
                preValue = 1
                for i in range(len(lines)):
                    tempValue = abs(lines[i][0] / self.__midPrice.getLastContent() - 1)
                    if tempValue < preValue:
                        factorValue = lines[i][0] / lines[i][1] - 1
                        breakPrice = lines[i][0]
                        preValue = tempValue
                self.addData(factorValue, self.__data.getLastTimeStamp())
                self.__breakPrice.append(breakPrice)
        else:
            if len(self.getContent()) == 0:
                self.addData(0., self.__data.getLastTimeStamp())
                self.__breakPrice.append(0)
            else:
                self.addData(self.getLastContent(), self.__data.getLastTimeStamp())
                self.__breakPrice.append(self.__breakPrice[-1])

    def getBreakPrice(self):
        return self.__breakPrice
