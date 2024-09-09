# -*- coding: utf-8 -*-
"""
This utility is used for test purpose, for informal calls only.
You can use the functions to dump the pickles you want.
Then load the pickle and be combined to SignalDataSet for SignalEvaluate

by 011478
"""


import math
import pickle


def FactorsToPickleEase(outputFactor, outputSubTag, tagName, factorName, factorIndexForSignalToPickle,
                        tradingUnderlyingCode, predictRollingWindow, dirPath):
    dict = {}
    for i in range(len(tradingUnderlyingCode)):
        dict.update({tradingUnderlyingCode[i]: {}})
        if len(outputFactor[i]) > 0:
            length = len(outputFactor[i])
            trainLength = math.floor(length * (1 - predictRollingWindow))
            predictLength = math.floor(length * predictRollingWindow)
            num = trainLength + predictLength
            PredictFactor = outputFactor[i][(num - predictLength):]
            PredictSubTag = outputSubTag[i][(num - predictLength):]

            for j in range(len(PredictFactor)):
                factorDict = {}
                for k in range(len(factorIndexForSignalToPickle)):
                    factorDict.update({factorName[factorIndexForSignalToPickle[k]]: PredictFactor[j][
                        factorIndexForSignalToPickle[k]]})
                dict.get(tradingUnderlyingCode[i]).update({PredictSubTag[j][tagName].startTimeStamp: factorDict})

    with open(dirPath, "wb") as f:
        pickle.dump(dict, f)
    print("done")
