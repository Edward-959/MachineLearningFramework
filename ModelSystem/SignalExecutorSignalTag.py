"""
the signal executor designed for one-label trading tag

The outSamplePredict has only one element.

by 011478
"""
from ModelSystem.SignalExecutorBase import SignalExecutorBase
import numpy as np
import json
import os


class SignalExecutorSignalTag(SignalExecutorBase):
    def __init__(self, positionMgr, riskMgr):
        SignalExecutorBase.__init__(self, positionMgr, riskMgr)
        self.__longTriggerRatio = 0
        self.__shortTriggerRatio = 0
        self.__longCloseRatio = 0
        self.__shortCloseRatio = 0

    def generateTriggerRatio(self, symbol, backTestUnderlying, para, inSamplePredict, lastPx, absolutePath, modelName, tickData):
        self.__longTriggerRatio = max([para["longMinTriggerRatio"], 0.02 / lastPx,
                                       np.percentile(inSamplePredict, para["longTriggerRatioPercentile"])])
        self.__shortTriggerRatio = min([para["shortMinTriggerRatio"], -0.02 / lastPx,
                                        np.percentile(inSamplePredict, para["shortTriggerRatioPercentile"])])
        self.__longCloseRatio = para["closeRatio"]
        self.__shortCloseRatio = -para["closeRatio"]
        if os.path.exists(absolutePath + 'ModelSaved/' + backTestUnderlying + '_' + modelName + '_SavedModelBuilder'):
            with open(
                    absolutePath + 'ModelSaved/' + backTestUnderlying + '_' + modelName + '_SavedModelBuilder' + "/triggerRatio.json",
                    "w") as f:
                triggerRatio = {'longTriggerRatio': self.__longTriggerRatio,
                                'shortTriggerRatio': self.__shortTriggerRatio,
                                'longCloseRatio': self.__longCloseRatio, 'shortCloseRatio': self.__shortCloseRatio}
                json.dump(triggerRatio, f)
        else:
            with open("triggerRatio.json", "w") as f:
                triggerRatio = {'longTriggerRatio': self.__longTriggerRatio,
                                'shortTriggerRatio': self.__shortTriggerRatio,
                                'longCloseRatio': 0, 'shortCloseRatio': 0}
                json.dump(triggerRatio, f)

    def isOpenLong(self, outSamplePredict, tagInfo):
        if outSamplePredict > self.__longTriggerRatio:
            return True
        else:
            return False

    def isOpenShort(self, outSamplePredict, tagInfo):
        if outSamplePredict < self.__shortTriggerRatio:
            return True
        else:
            return False

    def isCloseLong(self, outSamplePredict, tagInfo):
        if outSamplePredict <= self.__longCloseRatio:
            return True
        else:
            return False

    def isCloseShort(self, outSamplePredict, tagInfo):
        if outSamplePredict >= self.__shortCloseRatio:
            return True
        else:
            return False

    def getLongTriggerRatio(self):
        return self.__longTriggerRatio

    def getShortTriggerRatio(self):
        return self.__shortTriggerRatio
