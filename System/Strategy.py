# -*- coding: utf-8 -*-
"""
Created on Thu Aug 10 17:24:47 2017

@author: 006547
"""
import time

class Strategy:
    def __init__(self):
        self.__strategyName = ""
        self.__tradingUnderlyingCode = []
        self.__factorUnderlyingCode = []
        self.__paraFactor = []
        self.__paraTag = []
        self.__startDateTime = None
        self.__endDateTime = None
        self.__outputFactor = []
        self.__outputTag = []
        self.__outputTimeStamp = []
        self.__executeStrategy = []
        self.__factorName = []

    def getStrategyName(self):
        return self.__strategyName

    def getTradingUnderlyingCode(self):
        return self.__tradingUnderlyingCode

    def getFactorUnderlyingCode(self):
        return self.__factorUnderlyingCode

    def getParaFactor(self):
        return self.__paraFactor

    def getParaTag(self):
        return self.__paraTag

    def getStartDateTime(self):
        return self.__startDateTime

    def getEndDateTime(self):
        return self.__endDateTime

    def getOutputFactor(self):
        return self.__outputFactor

    def getOutputTag(self):
        return self.__outputTag

    def getOutputTimeStamp(self):
        return self.__outputTimeStamp

    def getExecuteStrategy(self):
        return self.__executeStrategy

    def getFactorName(self):
        return self.__factorName

    def setStrategyName(self, strategyName):
        self.__strategyName = strategyName

    def setTradingUnderlyingCode(self, tradingUnderlyingCode):
        self.__tradingUnderlyingCode = tradingUnderlyingCode
        self.__outputFactor = []
        self.__outputTag = []
        self.__outputTimeStamp = []
        self.__executeStrategy = []
        for j in range(len(self.__tradingUnderlyingCode)):
            self.__outputFactor.append([])
            self.__outputTag.append([])
            self.__outputTimeStamp.append([])
            self.__executeStrategy.append([])

    def setFactorUnderlyingCode(self, factorUnderlyingCode):
        self.__factorUnderlyingCode = factorUnderlyingCode

    def setParaFactor(self, paraFactor):
        self.__paraFactor = paraFactor

    def setFactorName(self, factorName):
        if len(self.__factorName) == 0 and len(factorName) > 0:
            self.__factorName = factorName

    def setParaTag(self, paraTag):
        self.__paraTag = paraTag

    def setStartDateTime(self, startDateTime):
        self.__startDateTime = startDateTime

    def setEndDateTime(self, endDateTime):
        self.__endDateTime = endDateTime

    def addOutputFactor(self, outputFactor, iTradingUnderlyingCode):
        self.__outputFactor[iTradingUnderlyingCode].append(outputFactor)

    def addOutputTag(self, outputTag, iTradingUnderlyingCode):
        self.__outputTag[iTradingUnderlyingCode].append(outputTag)

    def addOutputTimeStamp(self, outputTimeStamp, iTradingUnderlyingCode):
        self.__outputTimeStamp[iTradingUnderlyingCode].append(outputTimeStamp)

    def setOutputDir(self, dir):
        if not dir.endswith("/"):
            dir = dir + "/"
        self.__outputDir = dir + time.strftime("%Y%m%d%H%M%S", time.localtime())

    def getOutputDir(self):
        return self.__outputDir