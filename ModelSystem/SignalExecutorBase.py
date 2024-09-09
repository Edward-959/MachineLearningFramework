"""
The base class of signal executors
define some interfaces in this dummy class

Please note:
isOpenLong, isOpenShort, isCloseLong, isCloseShort can return 3 types of value:
1. bool: True, False. If True, then processSignal will be called.
2. None: False. ProcessSignal will not be called
3. dict: True. key = "price", "volume". ProcessSignal will be called and the returned value is the order value.

FYI, the outSamplePredict argument is the type of nd array.
It may contains multiple predicts in the parameter.

by 011478
"""


class SignalExecutorBase:
    def __init__(self, positionMgr, riskMgr):
        self._positionMgr = positionMgr
        self._riskMgr = riskMgr

    def generateTriggerRatio(self, symbol, backTestUnderlying, para, inSamplePredict, lastPx, absolutePath, modelName, tickData):
        pass

    def resetNewDay(self):
        pass

    def updatePredictInfo(self, outSamplePredict, tagInfo):
        pass

    def isOpenLong(self, outSamplePredict, tagInfo):
        pass

    def isOpenShort(self, outSamplePredict, tagInfo):
        pass

    def isCloseLong(self, outSamplePredict, tagInfo):
        pass

    def isCloseShort(self, outSamplePredict, tagInfo):
        pass

    def getLongTriggerRatio(self):
        pass

    def getShortTriggerRatio(self):
        pass