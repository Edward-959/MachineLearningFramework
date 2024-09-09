# -*- coding: utf-8 -*-
"""
Created on Thu Aug 10 20:48:28 2017

@author: 006547
"""
from System.FactorManagement import FactorManagement
from System.TagManagement import TagManagement


class ExecuteStrategy:
    def __init__(self, strategy, iTradingUnderlyingCode):
        self.__strategy = strategy
        self.__iTradingUnderlyingCode = iTradingUnderlyingCode
        # 建立因子管理模块用于储存数据、因子以及分配切片给因子进行计算
        self.__factorManagement = FactorManagement(strategy.getTradingUnderlyingCode()[iTradingUnderlyingCode],
                                                   strategy.getFactorUnderlyingCode())
        # 实例化需要计算的因子和非因子
        for i in range(len(strategy.getParaFactor()[0])):
            self.getFactorManagement().getFactorData(strategy.getParaFactor()[0][i])
        # 实例化标签管理模块，每一个切片来后都会在标签管理模块中实例化一个标签，里面可以储存及计算所有想要的东西
        self.__tagManagement = TagManagement(strategy.getParaTag(), self.__factorManagement)
        self.__factorName = []
        self.__strategy.setFactorName(self.__factorManagement.getFactorNameNeedSave())

    def onMarketData(self, sliceData):
        self.__factorManagement.calculate(sliceData)
        self.__tagManagement.calculate(sliceData)

    def saveOutput(self):
        # 保存因子、非因子、标签和时间戳
        self.__strategy.addOutputFactor(self.__factorManagement.getFactorsNeedSave(), self.__iTradingUnderlyingCode)
        self.__strategy.addOutputTimeStamp(self.__tagManagement.getLastTimeStamp(), self.__iTradingUnderlyingCode)
        self.__strategy.addOutputTag(self.__tagManagement.getLastTag(), self.__iTradingUnderlyingCode)

    def getFactorManagement(self):
        return self.__factorManagement

    def getFactorName(self):
        return self.__factorName

    def setPreDayticks(self, value):
        self.__factorManagement.setPreDayTicks(value)
    
