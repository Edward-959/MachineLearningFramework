# -*- coding: utf-8 -*-
"""
Created on 2017/9/13 13:08

@author: 006547
"""
import xgboost as xgb
from ModelSystem.Model import Model
import math


class ModelXgBoost(Model):
    def __init__(self, paraModel, name, tagName, modelManagement):
        Model.__init__(self, paraModel, name, tagName, modelManagement)
        modelManagement.register(self)

    def train(self, rollingData, outputDict):  # 数据集都是np.array格式
        trainData = rollingData["trainData"]
        trainLabel = rollingData["trainLabel"][self.tagName]
        predictData = rollingData["predictData"]
        predictLabel = rollingData["predictLabel"][self.tagName]
        validationRatio = self.paraModel["validationRatio"]
        index = math.floor(trainData.__len__() * (1 - validationRatio))
        dTrain = xgb.DMatrix(trainData[0:index], label=trainLabel[0:index])
        dTest = xgb.DMatrix(trainData[index:], label=trainLabel[index:])
        evalList = [(dTrain, 'train'), (dTest, 'eval')]

        model = xgb.train(self.paraModel["para"], dtrain=dTrain, num_boost_round=self.paraModel["numRound"],
                          evals=evalList, early_stopping_rounds=self.paraModel["earlyStoppingRounds"])
        inSamplePredict = model.predict(xgb.DMatrix(trainData), ntree_limit=model.best_iteration)
        outSamplePredict = model.predict(xgb.DMatrix(predictData), ntree_limit=model.best_iteration)

        outputDict.update({"model": model})
        outputDict.update({"trainData": trainData})
        outputDict.update({"trainLabel": trainLabel})
        outputDict.update({"predictData": predictData})
        outputDict.update({"predictLabel": predictLabel})
        outputDict.update({"inSamplePredict": inSamplePredict})
        outputDict.update({"outSamplePredict": outSamplePredict})
        outputDict.update({"outSampleSubTag": rollingData["predictSubTag"]})
        outputDict.update({"numTrainData": index})

        outputDict.update(self.evaluateModel(inSamplePredict, trainLabel, "inSample",
                                             self.paraModel["evaluateModel"]))
        outputDict.update(self.evaluateModel(outSamplePredict, predictLabel, "outSample",
                                             self.paraModel["evaluateModel"]))
