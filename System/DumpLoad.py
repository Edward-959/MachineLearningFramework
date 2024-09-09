# -*- coding: utf-8 -*-
"""
Created on 2017/9/14 14:20

@author: 006547
"""
import pickle
import datetime as dt
from System import Codec
import os


def dumpOutput(strategy):
    datadir = strategy.getOutputDir()
    startTimeStamp = dt.datetime.timestamp(dt.datetime.now())
    codes = strategy.getTradingUnderlyingCode()
    tags = strategy.getOutputTag()
    subname = str(strategy.getStartDateTime())+"-"+str(strategy.getEndDateTime())
    prename = datadir
    if not os.path.exists(prename):
        os.makedirs(prename)
    prename += "/"+ strategy.getStrategyName()
    for index in range(codes.__len__()):
        with open(prename +"-" +str(codes[index][0])+"-"+subname+ '.pickle', 'wb') as f:
            subTag = []
            for j in range(tags[index].__len__()):
                subTag.append(tags[index][j].subTag)
            pickle.dump((strategy.getOutputFactor()[index], subTag, codes[index],
                         strategy.getFactorName()), f)
    endTimeStamp = dt.datetime.timestamp(dt.datetime.now())
    print("Dump time: " + str(round((endTimeStamp - startTimeStamp) / 60, 2)) + " min")


def loadOutput(factorAddress, strategyName):
    startTimeStamp = dt.datetime.timestamp(dt.datetime.now())
    try:
        with open(factorAddress + strategyName + '.pickle', 'rb') as f:
            print('Use local open')
            try:
                outputFactor = []
                outputSubTag = []
                outputFactor2, outputSubTag2, tradingUnderlyingCode, factorName = pickle.load(f)
                outputFactor.append(outputFactor2)
                outputSubTag.append(outputSubTag2)
                print('Use local pickle')
            except Exception:
                outputFactor = []
                outputSubTag = []
                outputFactor2, outputSubTag2, tradingUnderlyingCode, factorName = Codec.decode(f)
                outputFactor.append(outputFactor2)
                outputSubTag.append(outputSubTag2)
                print('Use Xquant pickle')
    except Exception:
        from xquant.pyfile import Pyfile
        py = Pyfile()
        with py.open(factorAddress + strategyName + '.pickle') as f:
            print('Use Xquant open')
            outputFactor = []
            outputSubTag = []
            outputFactor2, outputSubTag2, tradingUnderlyingCode, factorName = Codec.decode(f)
            outputFactor.append(outputFactor2)
            outputSubTag.append(outputSubTag2)
            print('Use Xquant pickle')

    endTimeStamp = dt.datetime.timestamp(dt.datetime.now())
    print("Load time: " + str(round((endTimeStamp - startTimeStamp) / 60, 2)) + " min")
    return outputFactor, outputSubTag, tradingUnderlyingCode, factorName
