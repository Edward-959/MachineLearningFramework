# -*- coding: utf-8 -*-
"""
Created on 2017/9/13 13:07

@author: 006547
"""
import numpy as np
import math as math
from System.ProgressBar import ProgressBar
import datetime as dt


class ModelManagement:
    def __init__(self, trainRollingWindow, predictRollingWindow, outputFactor, outputSubTag,
                 tradingUnderlyingCode, factorName, factorIndex, factorMaAmountIndex,
                 factorIndexForSignal, backTestUnderlying, tagName):
        self.trainRollingWindow = trainRollingWindow
        self.predictRollingWindow = predictRollingWindow
        self.outputFactor = outputFactor
        self.outputSubTag = outputSubTag
        self.tradingUnderlyingCode = tradingUnderlyingCode
        self.factorName = factorName
        self.factorIndex = factorIndex
        self.factorMaAmountIndex = factorMaAmountIndex
        self.factorIndexForSignal = factorIndexForSignal
        self.factorNameTrained = np.array(factorName)[factorIndex].tolist()
        self.model = {}
        self.rollingData = []
        self.combineSubTag = []
        self.backTestUnderlying = backTestUnderlying
        self.tagName = tagName
        # self.__predictIndex_window = []  # must be called before prepareData()!
        self.__customFactorDict = {}  # key = symbol, value = dict{timestamp: maAmount}
        self.__factorForSignalDict = {}  # {key = symbol, value = {key = timestamp, value = {factorName, value}}}
        self.prepareData()

    def register(self, model):
        self.model.update({model.name: model})
        model.outputByWindow = []
        model.outputByUnderlying = []
        model.tradingUnderlyingCode = self.tradingUnderlyingCode
        for i in range(self.rollingData.__len__()):
            model.outputByWindow.append([])
            model.outputByUnderlying.append({})
            for j in range(self.rollingData[i].__len__()):
                model.outputByWindow[i].append({})

    # 将之前得到的Factor和Tag数据整理成类似于矩阵的格式
    def prepareData(self):
        self.rollingData = []
        for i in range(self.tradingUnderlyingCode.__len__()):
            self.rollingData.append([])  # 每个代码对应rollingData的第一层
            if self.outputFactor[i].__len__() > 0:  # 防止有标的没有数据
                tempFactor = np.array(self.outputFactor[i])[:, self.factorIndex]
                tempTag = {}
                tagKey = list(self.outputSubTag[i][0].keys())
                for j in range(tagKey.__len__()):
                    tempTag.update({tagKey[j]: []})
                    for kTag in self.outputSubTag[i]:
                        tempTag[tagKey[j]].append(kTag[tagKey[j]].returnRate)
                    tempTag[tagKey[j]] = np.array(tempTag[tagKey[j]])
                length = len(tempFactor)
                trainLength = math.floor(length * self.trainRollingWindow)
                predictLength = math.floor(length * self.predictRollingWindow)
                num = trainLength + predictLength
                while num <= length:  # rollingData第二层对应于不同的训练和预测窗口（如果存在）
                    self.rollingData[i].append({})
                    self.rollingData[i][-1].update({
                        "trainData": tempFactor[(num - trainLength - predictLength):(num - predictLength), :]})
                    self.rollingData[i][-1].update({"predictData": tempFactor[(num - predictLength):num, :]})
                    self.rollingData[i][-1].update({
                        "trainSubTag": self.outputSubTag[i][(num - trainLength - predictLength):(num - predictLength)]})
                    self.rollingData[i][-1].update({"predictSubTag": self.outputSubTag[i][(num - predictLength):num]})
                    tempTrainLabel = {}
                    tempPredictLabel = {}
                    for j in range(tagKey.__len__()):
                        tempTrainLabel.update({
                            tagKey[j]: tempTag[tagKey[j]][(num - trainLength - predictLength):(num - predictLength)]})
                        tempPredictLabel.update({tagKey[j]: tempTag[tagKey[j]][(num - predictLength):num]})
                    self.rollingData[i][-1].update({"trainLabel": tempTrainLabel})
                    self.rollingData[i][-1].update({"predictLabel": tempPredictLabel})
                    self.__addPredictIndex(i, num - predictLength, num)  # 将测试样本的index记录下来，方便对应outputSample
                    num += predictLength
        self.combineSubTag = []
        for i in range(self.rollingData.__len__()):
            predictSubTag = []
            trainSubTag = []
            self.combineSubTag.append({})
            for j in range(self.rollingData[i].__len__()):
                predictSubTag += self.rollingData[i][j]["predictSubTag"]
                trainSubTag += self.rollingData[i][j]["trainSubTag"]

            self.combineSubTag[i].update({"predictSubTag": predictSubTag})
            self.combineSubTag[i].update({"trainSubTag": trainSubTag})

    def train(self):
        startTimeStamp = dt.datetime.timestamp(dt.datetime.now())
        bar = ProgressBar()
        for model in self.model.values():
            for i in range(self.tradingUnderlyingCode.__len__()):
                if self.rollingData[i].__len__() > 0:
                    for j in range(self.rollingData[i].__len__()):
                        model.outputByWindow[i][j] = {}
                        model.train(self.rollingData[i][j], model.outputByWindow[i][j])
                bar.move(len(self.model) * self.tradingUnderlyingCode.__len__())
                bar.log()
            model.createOutputByUnderlying()
        endTimeStamp = dt.datetime.timestamp(dt.datetime.now())
        print("Training time: " + str(round((endTimeStamp - startTimeStamp) / 60, 2)) + " min")

    def __addPredictIndex(self, symbolIndex, startIndex, endIndex):
        symbol = self.tradingUnderlyingCode[symbolIndex]
        if symbol not in self.__customFactorDict:
            self.__customFactorDict.update({symbol: {}})

        if symbol not in self.__factorForSignalDict:
            self.__factorForSignalDict.update({symbol: {}})

        for i in range(startIndex, endIndex):
            timeStamp = self.outputSubTag[symbolIndex][i][self.tagName].startTimeStamp
            self.__customFactorDict.get(symbol).update(
                {timeStamp: self.outputFactor[symbolIndex][i][self.factorMaAmountIndex]})

            factorDict = {}
            for j in range(len(self.factorIndexForSignal)):
                factorDict.update({self.factorName[self.factorIndexForSignal[j]]: self.outputFactor[symbolIndex][i][
                    self.factorIndexForSignal[j]]})
            self.__factorForSignalDict.get(symbol).update({timeStamp: factorDict})

    def getCustomFactorDictBySymbol(self, symbol):
        return self.__customFactorDict.get(symbol)

    def getCustomFactorDict(self):
        return self.__customFactorDict

    def getFactorForSignalDict(self):
        return self.__factorForSignalDict
