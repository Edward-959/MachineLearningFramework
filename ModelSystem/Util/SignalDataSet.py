# -*- coding: utf-8 -*-
"""
create the data set for Signal Evaluate
input the model and the model management
output the necessary data info

by 011478
"""
import pickle
import os


class SignalDataSet:
    """
    store the necessary data info for Signal Evaluate for multi processing
    """

    def __init__(self, backTestUnderlying, tagName, modelName, tradingUnderlyingCode, customFactorDict,
                 factorForSignalDict, outputByWindow, outputByUnderlying, windowRollingSize):
        self.__backTestUnderlying = backTestUnderlying
        self.__tagName = tagName
        self.__modelName = modelName
        self.__tradingUnderlyingCode = tradingUnderlyingCode
        self.__customFactorDict = customFactorDict
        self.__factorForSignalDict = factorForSignalDict
        self.__outputByWindow = outputByWindow
        self.__outputByUnderlying = outputByUnderlying
        self.__windowRollingSize = windowRollingSize

    def backTestUnderlying(self):
        return self.__backTestUnderlying

    def tagName(self):
        return self.__tagName

    def modelName(self):
        return self.__modelName

    def tradingUnderlyingCode(self):
        return self.__tradingUnderlyingCode

    def customFactorDict(self):
        return self.__customFactorDict

    def factorForSignalDict(self):
        if hasattr(self, "_SignalDataSet__factorForSignalDict"):
            return self.__factorForSignalDict
        else:
            return None

    def outputByWindow(self):
        return self.__outputByWindow

    def outputByUnderlying(self):
        return self.__outputByUnderlying

    def combineFromFactorForSignalPickle(self, dirPath):
        """
        This method is used to combine the factors from FactorForSignal.pickle, if there is,
        to the existing SignalDataSet, which will be used in SignalEvaluate
        :param dirPath: where FactorForSignal.pickle lies
        :return:  SignalDataSet
        """
        if os.path.exists(dirPath):
            with open(dirPath, "rb") as f:
                factorForSignalDict = pickle.load(f)
        else:
            return self

        if not hasattr(self, "_SignalDataSet__factorForSignalDict"):
            self.__factorForSignalDict = factorForSignalDict
            return self
        else:
            for symbol in factorForSignalDict.keys():
                if symbol not in self.__factorForSignalDict.keys():
                    self.__factorForSignalDict.update({symbol: factorForSignalDict.get(symbol)})
                else:
                    for timestamp in factorForSignalDict.get(symbol).keys():
                        if timestamp not in self.__factorForSignalDict.get(symbol).keys():
                            self.__factorForSignalDict.get(symbol).update(
                                {timestamp: factorForSignalDict.get(symbol).get(timestamp)})
                        else:
                            for factor in factorForSignalDict.get(symbol).get(timestamp).keys():
                                if factor not in self.__factorForSignalDict.get(symbol).get(timestamp).keys():
                                    self.__factorForSignalDict.get(symbol).get(timestamp).update(
                                        {factor: factorForSignalDict.get(symbol).get(timestamp).get(factor)})
            return self


def generateSignalDataSet(modelName, modelManagement):
    keyNameUnder = ["outSamplePredict", "inSamplePredict", "outSampleRMSE", "numTrainData", "outSampleSubTag"]
    keyNameWindow = ["inSamplePredict", "outSampleRMSE", "numTrainData", "outSampleSubTag", "outSamplePredict"]
    model = modelManagement.model[modelName]
    backTestUnderlying = model.backTestUnderlying
    tagName = modelManagement.tagName
    tradingUnderlyingCode = model.tradingUnderlyingCode
    customFactorDict = modelManagement.getCustomFactorDict()
    factorForSignalDict = modelManagement.getFactorForSignalDict()
    outputByWindow = []
    windowRollingSize = []
    outputByUnderlying = []
    # pick the very necessary info
    for i in range(len(model.outputByWindow)):
        outputByWindow.append([])
        windowRollingSize.append([])
        for j in range(len(model.outputByWindow[i])):
            outputByWindow[i].append([])
            windowRollingSize[i].append([])
            tempDict = {}
            for k in range(len(keyNameWindow)):
                tempDict.update({keyNameWindow[k]: model.outputByWindow[i][j][keyNameWindow[k]]})
            outputByWindow[i][j] = tempDict
            windowRollingSize[i][j] = len(model.outputByWindow[i][j]["outSampleSubTag"])

    for i in range(len(model.outputByUnderlying)):
        outputByUnderlying.append([])
        tempDict = {}
        for k in range(len(keyNameUnder)):
            tempDict.update({keyNameUnder[k]: model.outputByUnderlying[i][keyNameUnder[k]]})
        outputByUnderlying[i] = tempDict

    # compare
    # n = 0
    # for i in range(len(outputByWindow)):
    #     for j in range(len(outputByWindow[i])):
    #         for k in range(len(outputByWindow[i][j]["outSampleSubTag"])):
    #             try:
    #                 win = outputByWindow[i][j]["outSampleSubTag"][k]
    #                 under = outputByUnderlying[i]["outSampleSubTag"][n]
    #                 result = op.eq(win, under)
    #                 if not result:
    #                     print(str(i) + " " + str(j) + " " + str(k) + " not equal!")
    #                 n += 1
    #             except Exception as e:
    #                 print(str(i) + " " + str(j) + " " + str(k) + " error!")
    #                 print(str(e))

    return SignalDataSet(backTestUnderlying, tagName, modelName, tradingUnderlyingCode, customFactorDict,
                         factorForSignalDict, outputByWindow, outputByUnderlying, windowRollingSize)
