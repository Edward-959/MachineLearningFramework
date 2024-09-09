# -*- coding: utf-8 -*-
"""
Created on 2017/9/13 22:47

@author: 006547
"""
import numpy as np


class Model:
    def __init__(self, paraModel, name, tagName, modelManagement):
        self.paraModel = paraModel
        self.name = name
        self.tagName = tagName
        self.modelManagement = modelManagement
        self.modelInput = modelManagement.factorIndex
        self.backTestUnderlying = modelManagement.backTestUnderlying
        self.outputByWindow = None
        self.outputByUnderlying = None
        self.tradingUnderlyingCode = None

    def createOutputByUnderlying(self):
        for i in range(self.outputByWindow.__len__()):
            predictLabel = self.outputByWindow[i][0]["predictLabel"]
            trainLabel = self.outputByWindow[i][0]["trainLabel"]
            outSamplePredict = self.outputByWindow[i][0]["outSamplePredict"]
            inSamplePredict = self.outputByWindow[i][0]["inSamplePredict"]
            outSampleSubTag = []  # reference, otherwise source will be affected
            outSampleSubTag += self.outputByWindow[i][0]["outSampleSubTag"]
            numTrainData = [self.outputByWindow[i][0]["numTrainData"]]
            self.outputByUnderlying[i] = {}
            if self.outputByWindow[i].__len__() > 1:
                for j in range(1, self.outputByWindow[i].__len__()):
                    predictLabel = np.vstack((predictLabel, self.outputByWindow[i][j]["predictLabel"]))
                    trainLabel = np.vstack((trainLabel, self.outputByWindow[i][j]["trainLabel"]))
                    outSamplePredict = np.vstack((outSamplePredict, self.outputByWindow[i][j]["outSamplePredict"]))
                    inSamplePredict = np.vstack((inSamplePredict, self.outputByWindow[i][j]["inSamplePredict"]))
                    outSampleSubTag += self.outputByWindow[i][j]["outSampleSubTag"]
                    numTrainData.append(self.outputByWindow[i][j]["numTrainData"])

            self.outputByUnderlying[i].update({"predictLabel": predictLabel})
            self.outputByUnderlying[i].update({"trainLabel": trainLabel})
            self.outputByUnderlying[i].update({"outSamplePredict": outSamplePredict})
            self.outputByUnderlying[i].update({"inSamplePredict": inSamplePredict})
            self.outputByUnderlying[i].update({"outSampleSubTag": outSampleSubTag})
            self.outputByUnderlying[i].update({"numTrainData": int(np.mean(numTrainData))})
            self.outputByUnderlying[i].update(self.evaluateModel(inSamplePredict, trainLabel, "inSample",
                                                                 self.paraModel["evaluateModel"]))
            self.outputByUnderlying[i].update(self.evaluateModel(outSamplePredict, predictLabel, "outSample",
                                                                 self.paraModel["evaluateModel"]))

    @staticmethod
    def evaluateModel(predict, label, head, para):
        SSR = np.sum((predict - np.mean(label)) ** 2)
        SST = np.sum((label - np.mean(label)) ** 2)
        SSE = np.sum((label - predict) ** 2)
        MSE = SSE / predict.__len__()
        RMSE = np.sqrt(MSE)
        RSquare = SSR / SST
        Error = label - predict
        AverageError = np.mean(Error)
        AverageStd = np.std(Error)
        percentileErrorRatio = para["percentileErrorRatio"]
        PercentileError = np.percentile(Error, percentileErrorRatio)

        return {head + "SSR": SSR,
                head + "SST": SST,
                head + "SSE": SSE,
                head + "MSE": MSE,
                head + "RMSE": RMSE,
                head + "RSquare": RSquare,
                head + "Error": Error,
                head + "AverageError": AverageError,
                head + "AverageStd": AverageStd,
                head + "PercentileError": PercentileError}
