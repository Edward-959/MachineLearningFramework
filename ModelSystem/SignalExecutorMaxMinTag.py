"""
the signal executor designed for max min tag

The outSamplePredict has two elements.

by 011478
"""
from ModelSystem.SignalExecutorBase import SignalExecutorBase
import numpy as np
import os
import json


class SignalExecutorMaxMinTag(SignalExecutorBase):
    def __init__(self, positionMgr, riskMgr):
        SignalExecutorBase.__init__(self, positionMgr, riskMgr)
        self.__longTriggerRatio = 0
        self.__shortTriggerRatio = 0
        self.__longRiskRatio = 0
        self.__shortRiskRatio = 0
        self.__longCloseRatio = 0
        self.__shortCloseRatio = 0

        self.__isFirstClose = True

    def generateTriggerRatio(self, symbol, backTestUnderlying, para, inSamplePredict, lastPx, absolutePath, modelName, tickData):
        self.__longTriggerRatio = max([para["longMinTriggerRatio"], 0.01 / lastPx,
                                       np.percentile((inSamplePredict[:, 0] + inSamplePredict[:, 1]) / 2,
                                                     para["longTriggerRatioPercentile"])])
        self.__shortTriggerRatio = min([para["shortMinTriggerRatio"], -0.01 / lastPx,
                                        np.percentile((inSamplePredict[:, 0] + inSamplePredict[:, 1]) / 2,
                                                      para["shortTriggerRatioPercentile"])])
        self.__longRiskRatio = para["riskRatio"]
        self.__shortRiskRatio = -para["riskRatio"]
        self.__longCloseRatio = para["closeRatio"]
        self.__shortCloseRatio = -para["closeRatio"]
        self.__writeJsonFile(backTestUnderlying, absolutePath, modelName)

    def __writeJsonFile(self, backTestUnderlying, absolutePath, modelName):
        if os.path.exists(absolutePath+'ModelSaved/' + backTestUnderlying + '_' + modelName + '_SavedModelBuilder'):
            with open(absolutePath+'ModelSaved/' + backTestUnderlying + '_' + modelName + '_SavedModelBuilder' + "/triggerRatio.json", "w") as f:
                triggerRatio = {'longTriggerRatio': self.__longTriggerRatio, 'shortTriggerRatio': self.__shortTriggerRatio,
                                'longRiskRatio': self.__longRiskRatio, 'shortRiskRatio': self.__shortRiskRatio,
                                'longCloseRatio': self.__longCloseRatio, 'shortCloseRatio': self.__shortCloseRatio}
                json.dump(triggerRatio, f)
        else:
            with open("triggerRatio.json", "w") as f:
                triggerRatio = {'longTriggerRatio': self.__longTriggerRatio, 'shortTriggerRatio': self.__shortTriggerRatio,
                                'longRiskRatio': self.__longRiskRatio, 'shortRiskRatio': self.__shortRiskRatio,
                                'longCloseRatio': self.__longCloseRatio, 'shortCloseRatio': self.__shortCloseRatio}
                json.dump(triggerRatio, f)

    # 提供隔日初始化操作
    def resetNewDay(self):
        pass

    # 新tick来必调用
    def updatePredictInfo(self, outSamplePredict, tagInfo):
        pass

    def isOpenLong(self, outSamplePredict, tagInfo):
        if (outSamplePredict[0] + outSamplePredict[1]) / 2 > self.__longTriggerRatio \
               and outSamplePredict[1] > self.__longRiskRatio:
            self.__isFirstClose = True
            return True
        else:
            return False

    def isOpenShort(self, outSamplePredict, tagInfo):
        if (outSamplePredict[0] + outSamplePredict[1]) / 2 < self.__shortTriggerRatio \
               and outSamplePredict[0] < self.__shortRiskRatio:
            self.__isFirstClose = True
            return True
        else:
            return False

    def isCloseLong(self, outSamplePredict, tagInfo):
        if self.__isFirstClose:
            if (outSamplePredict[0] + outSamplePredict[1]) / 2 <= self.__longCloseRatio:
                self.__isFirstClose = False
                return True
            else:
                return False
        else:
            if (outSamplePredict[0] + outSamplePredict[1]) / 2 <= 0:
                return True
            else:
                return False

    def isCloseShort(self, outSamplePredict, tagInfo):
        if self.__isFirstClose:
            if (outSamplePredict[0] + outSamplePredict[1]) / 2 >= self.__shortCloseRatio:
                self.__isFirstClose = False
                return True
            else:
                return False
        else:
            if (outSamplePredict[0] + outSamplePredict[1]) / 2 >= 0:
                return True
            else:
                return False

    def getLongTriggerRatio(self):
        return self.__longTriggerRatio

    def getShortTriggerRatio(self):
        return self.__shortTriggerRatio



