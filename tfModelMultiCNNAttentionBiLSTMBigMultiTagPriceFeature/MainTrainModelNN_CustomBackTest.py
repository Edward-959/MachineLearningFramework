# -*- coding: utf-8 -*-
"""
Created on Thu Aug 10 16:37:11 2017

@author: 006547
"""
import sys
import os

sys.path.append(os.path.abspath(os.path.abspath(__file__) + "/../.."))
# from xquant.pyfile import Pyfile
sys.path.append("../")
from ModelSystem.ModelManagement import ModelManagement
from tfModelMultiCNNAttentionBiLSTMBigMultiTagPriceFeature.ModelMultiCNNAttentionBiLSTM import ModelMultiCNNAttentionBiLSTM
from System import DumpLoad
from ModelSystem.SignalEvaluate import SignalEvaluate
from ModelSystem.Util.SignalDataSet import generateSignalDataSet
import System.ReadDataFile as GD
# import System.GetInsightData as GD
import math
import datetime as dt
import gc
# from multiprocessing import Pool
# import multiprocessing
import pickle


def multiProcessFunction(paraInProcess, paraFixed, absolutePath, backTestUnderlying, modelName):
    # print("start")
    with open(absolutePath + 'ModelSignalDataSet/' + backTestUnderlying + '_' + modelName + '/signalDataSet.pickle', 'rb') as f:
        signalDataSet = pickle.load(f)
    with open(absolutePath + 'ModelSignalDataSet/' + backTestUnderlying + '_' + modelName + '/Data.pickle', 'rb') as f:
        tickData, transactionData = pickle.load(f)
    analysisMat = []
    for para in paraInProcess:
        signalTagPara = {"longTriggerRatioPercentile": 0,
                         "shortTriggerRatioPercentile": 100,
                         "longMinTriggerRatio": para[0],
                         "shortMinTriggerRatio": -para[0],
                         "riskRatio": paraFixed['riskRatio'], "maxLose": paraFixed['maxLose'],
                         "closeRatio": -para[0] / 2}

        # 说明如何使用：
        # 定义一个变量字典，放入以下所需的变量，具体变量含义可以参考SignalEvaluate的__init__的注释
        mockTradePara = {"initAmount": para[1], "maxTurnoverPerOrder": paraFixed['maxTurnoverPerOrder'], "maxRatePerOrder": 0.25,
                         "maAmountRate": paraFixed['maAmountRate'], "openWithdrawSeconds": 2.5, "closeWithdrawSeconds": 3,
                         "buyLevel": 1, "sellLevel": 1, "buyDeviation": 0, "sellDeviation": -0.01,
                         "MIN_ORDER_QTY": 100}

        # 实例一个SignalEvaluate，第一个参数为信号变量，第二个为回测变量，第三个用String以类名定义信号分析器
        # 其余不变
        signalEvaluate = SignalEvaluate(signalDataSet, signalTagPara, mockTradePara, "SignalExecutorMaxMinTag", absolutePath,
                                        tickData, transactionData)
        # 执行
        rollingCombineTradingOrder = signalEvaluate.evaluate(funStr=None, show=False)

        analysisMat.append([para[0], para[1], rollingCombineTradingOrder[1][0]['winRate'],
                            rollingCombineTradingOrder[1][0]['averageReturnRate'],
                            rollingCombineTradingOrder[1][0]['averagePositionTime'],
                            rollingCombineTradingOrder[1][0]['timesPerDay'],
                            rollingCombineTradingOrder[1][0]['afterCostProfit'],
                            rollingCombineTradingOrder[1][0]['annualReturnMV']])

        # return rollingCombineTradingOrder, signalTagPara
    # print("end")
    return analysisMat


def paraGroup(paraMat, processNum):
    def multiFor(paraMat2, paraAll2, paraTemp3, index2=0):
        if index2 < paraMat2.__len__() - 1:
            for i in range(paraMat2[index2].__len__()):
                paraTemp2 = paraTemp3[:]
                paraTemp2.append(paraMat2[index2][i])
                multiFor(paraMat2, paraAll2, paraTemp2, index2 + 1)
        else:
            for i in range(paraMat2[index2].__len__()):
                paraTemp2 = paraTemp3[:]
                paraTemp2.append(paraMat2[index2][i])
                paraAll2.append(paraTemp2)

    paraAll = []
    paraTemp = []
    multiFor(paraMat, paraAll, paraTemp, index2=0)

    taskNumPerProcess = math.ceil(paraAll.__len__() / processNum)

    index = 0

    paraInProcess = []
    while index < paraAll.__len__():
        paraInProcess.append(paraAll[index:index + taskNumPerProcess])
        index += taskNumPerProcess
    processNum = paraInProcess.__len__()
    return paraInProcess, processNum


def main():
    sys.path.append("Factor")
    sys.path.append("NonFactor")
    sys.path.append("Tag")
    sys.path.append("System")

    code = ["AlgoShaolin-000002.SZ-20170413093000-20180413145659",  # 0
            "AlgoShaolin-000028.SZ-20170413093000-20180413145659",  # 1
            "AlgoShaolin-000063.SZ-20170413093000-20180413145659",  # 2
            "AlgoShaolin-000333.SZ-20170413093000-20180413145659",  # 3
            "AlgoShaolin-000400.SZ-20170413093000-20180413145659",  # 4
            "AlgoShaolin-000530.SZ-20170413093000-20180413145659",  # 5
            "AlgoShaolin-000568.SZ-20170413093000-20180413145659",  # 6
            "AlgoShaolin-000571.SZ-20170413093000-20180413145659",  # 7
            "AlgoShaolin-000581.SZ-20170413093000-20180413145659",  # 8
            "AlgoShaolin-000651.SZ-20170413093000-20180413145659",  # 9
            "AlgoShaolin-000786.SZ-20170413093000-20180413145659",  # 10
            "AlgoShaolin-000826.SZ-20170413093000-20180413145659",  # 11
            "AlgoShaolin-000858.SZ-20170413093000-20180413145659",  # 12
            "AlgoShaolin-000895.SZ-20170413093000-20180413145659",  # 13
            "AlgoShaolin-000910.SZ-20170413093000-20180413145659",  # 14
            "AlgoShaolin-000977.SZ-20170413093000-20180413145659",  # 15
            "AlgoShaolin-001979.SZ-20170413093000-20180413145659",  # 16
            "AlgoShaolin-002008.SZ-20170413093000-20180413145659",  # 17
            "AlgoShaolin-002033.SZ-20170413093000-20180413145659",  # 18
            "AlgoShaolin-002043.SZ-20170413093000-20180413145659",  # 19
            "AlgoShaolin-002128.SZ-20170413093000-20180413145659",  # 20
            "AlgoShaolin-002179.SZ-20170413093000-20180413145659",  # 21
            "AlgoShaolin-002185.SZ-20170413093000-20180413145659",  # 22
            "AlgoShaolin-002236.SZ-20170413093000-20180413145659",  # 23
            "AlgoShaolin-002241.SZ-20170413093000-20180413145659",  # 24
            "AlgoShaolin-002267.SZ-20170413093000-20180413145659",  # 25
            "AlgoShaolin-002294.SZ-20170413093000-20180413145659",  # 26
            "AlgoShaolin-002299.SZ-20170413093000-20180413145659",  # 27
            "AlgoShaolin-002304.SZ-20170413093000-20180413145659",  # 28
            "AlgoShaolin-002311.SZ-20170413093000-20180413145659",  # 29
            "AlgoShaolin-002384.SZ-20170413093000-20180413145659",  # 30
            "AlgoShaolin-002396.SZ-20170413093000-20180413145659",  # 31
            "AlgoShaolin-002456.SZ-20170413093000-20180413145659",  # 32
            "AlgoShaolin-002466.SZ-20170413093000-20180413145659",  # 33
            "AlgoShaolin-002475.SZ-20170413093000-20180413145659",  # 34
            "AlgoShaolin-002508.SZ-20170413093000-20180413145659",  # 35
            "AlgoShaolin-002572.SZ-20170413093000-20180413145659",  # 36
            "AlgoShaolin-002589.SZ-20170413093000-20180413145659",  # 37
            "AlgoShaolin-002594.SZ-20170413093000-20180413145659",  # 38
            "AlgoShaolin-002624.SZ-20170413093000-20180413145659",  # 39
            "AlgoShaolin-002672.SZ-20170413093000-20180413145659",  # 40
            "AlgoShaolin-300015.SZ-20170413093000-20180413145659",  # 41
            "AlgoShaolin-300070.SZ-20170413093000-20180413145659",  # 42
            "AlgoShaolin-300115.SZ-20170413093000-20180413145659",  # 43
            "AlgoShaolin-300197.SZ-20170413093000-20180413145659",  # 44
            "AlgoShaolin-300323.SZ-20170413093000-20180413145659",  # 45
            "AlgoShaolin-300408.SZ-20170413093000-20180413145659",  # 46
            "AlgoShaolin-300418.SZ-20170413093000-20180413145659",  # 47
            "AlgoShaolin-300477.SZ-20170413093000-20180413145659",  # 48
            "AlgoShaolin-600004.SH-20170413093000-20180413145659",  # 49
            "AlgoShaolin-600009.SH-20170413093000-20180413145659",  # 50
            "AlgoShaolin-600029.SH-20170413093000-20180413145659",  # 51
            "AlgoShaolin-600036.SH-20170413093000-20180413145659",  # 52
            "AlgoShaolin-600057.SH-20170413093000-20180413145659",  # 53
            "AlgoShaolin-600110.SH-20170413093000-20180413145659",  # 54
            "AlgoShaolin-600201.SH-20170413093000-20180413145659",  # 55
            "AlgoShaolin-600219.SH-20170413093000-20180413145659",  # 56
            "AlgoShaolin-600236.SH-20170413093000-20180413145659",  # 57
            "AlgoShaolin-600276.SH-20170413093000-20180413145659",  # 58
            "AlgoShaolin-600418.SH-20170413093000-20180413145659",  # 59
            "AlgoShaolin-600498.SH-20170413093000-20180413145659",  # 60
            "AlgoShaolin-600521.SH-20170413093000-20180413145659",  # 61
            "AlgoShaolin-600570.SH-20170413093000-20180413145659",  # 62
            "AlgoShaolin-600589.SH-20170413093000-20180413145659",  # 63
            "AlgoShaolin-600703.SH-20170413093000-20180413145659",  # 64
            "AlgoShaolin-600782.SH-20170413093000-20180413145659",  # 65
            "AlgoShaolin-600805.SH-20170413093000-20180413145659",  # 66
            "AlgoShaolin-600867.SH-20170413093000-20180413145659",  # 67
            "AlgoShaolin-601012.SH-20170413093000-20180413145659",  # 68
            "AlgoShaolin-601021.SH-20170413093000-20180413145659",  # 69
            "AlgoShaolin-601088.SH-20170413093000-20180413145659",  # 70
            "AlgoShaolin-601288.SH-20170413093000-20180413145659",  # 71
            "AlgoShaolin-601318.SH-20170413093000-20180413145659",  # 72
            "AlgoShaolin-601398.SH-20170413093000-20180413145659",  # 73
            "AlgoShaolin-601601.SH-20170413093000-20180413145659",  # 74
            "AlgoShaolin-601939.SH-20170413093000-20180413145659",  # 75
            "AlgoShaolin-601988.SH-20170413093000-20180413145659",  # 76
            "AlgoShaolin-603108.SH-20170413093000-20180413145659",  # 77
            "AlgoShaolin-002056.SZ-20170413093000-20180413145659",  # 78
            "AlgoShaolin-600516.SH-20170413093000-20180413145659",  # 79
            "AlgoShaolin-600362.SH-20170413093000-20180413145659",  # 80
            "AlgoShaolin-600549.SH-20170413093000-20180413145659",  # 81
            "AlgoShaolin-600176.SH-20170413093000-20180413145659",  # 82
            "AlgoShaolin-600519.SH-20170413093000-20180413145659",  # 83
            ]

    # 读取数据：
    GPUID = 0
    # 设置是否需要加载因子去计算预测值
    mode = True
    absolutePath = ""
    factorAddress = ''
    tagName = ["2minMaxMin"]
    conv_len = 3
    sliceLagMat = [150]
    predictRollingWindowMat = [0.2]
    # processNum = 36
    paraFixed = {'riskRatio': -0.001, 'maxLose': -0.01, 'maxTurnoverPerOrder': 5000000, 'maAmountRate': 2}
    paraMat = [[0.001, 0.0011, 0.0012, 0.0013, 0.0014, 0.0015],
               [1000000]]
    # 设置需要训练的因子
    # factorIndex = [0, 4, 5, 10, 11, 12, 14, 15, 16, 18, 19, 20, 21, 22, 23, 26, 27, 28, 29, 30, 31, 38, 40]
    # factorIndex = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18,19,20,21,22,23,24,25]
    # factorIndex = list(range(39))
    factorIndex = [4, 6, 7, 8, 9, 10, 11, 12, 0, 1, 2, 3, 5, 13, 14, 15, 16, 17, 18, 19]
    # factorMaAmountIndex = 41
    # factorMaAmountIndex = 26
    factorMaAmountIndex = 20
    factorGroup = [[0, 8],
                   [8, 12]]
    priceVolumeFactorIndex = [2, 3]
    for i in [15]:
        backTestUnderlying = code[i]
        print(backTestUnderlying)

        # py = Pyfile()
        # if (not py.exists(factorAddress + backTestUnderlying + '.pickle')) and mode:
        if not os.path.exists(factorAddress + backTestUnderlying + '.pickle'):
            print('Not FactorData')
        else:
            outputFactor = []
            outputSubTag = []
            tradingUnderlyingCode = []
            factorName = []
            if mode:
                outputFactor, outputSubTag, tradingUnderlyingCode, factorName = DumpLoad.loadOutput(factorAddress, backTestUnderlying)

            for j in sliceLagMat:
                for k in predictRollingWindowMat:
                    predictRollingWindow = k
                    sliceLag = j
                    # 建立模型管理模块
                    modelManagement = []
                    if mode:
                        modelManagement = ModelManagement(trainRollingWindow=1 - predictRollingWindow,
                                                          predictRollingWindow=predictRollingWindow,
                                                          outputFactor=outputFactor,
                                                          outputSubTag=outputSubTag,
                                                          tradingUnderlyingCode=tradingUnderlyingCode,
                                                          factorName=factorName, factorIndex=factorIndex,
                                                          factorMaAmountIndex=factorMaAmountIndex,
                                                          backTestUnderlying=backTestUnderlying, tagName=tagName[0], factorIndexForSignal=[])
                    # 设置模型参数
                    paraModel = {"absolutePath": absolutePath, "GPUID": GPUID, "validationNum": 40000, 'predictRollingWindow': predictRollingWindow,
                                 'sliceLag': sliceLag, 'conv_len': conv_len, 'factorGroup': factorGroup, 'priceVolumeFactorIndex': priceVolumeFactorIndex,
                                 "evaluateModel": {"percentileErrorRatio": 70, "triggerRatio": 0.002, "riskRatio": -0.001}}
                    modelName = "modelCNNRNN" + tagName[0] + "Pred" + str(predictRollingWindow) + 'SliceLag' + str(sliceLag)
                    if mode:
                        ModelMultiCNNAttentionBiLSTM(paraModel=paraModel, name=modelName, tagName=tagName,
                                                     modelManagement=modelManagement)
                        # 训练模型
                        modelManagement.train()
                        signalDataSet = generateSignalDataSet(modelName, modelManagement)
                        if not os.path.exists(absolutePath + 'ModelSignalDataSet/' + backTestUnderlying + '_' + modelName):
                            os.makedirs(absolutePath + 'ModelSignalDataSet/' + backTestUnderlying + '_' + modelName)
                        with open(
                                absolutePath + 'ModelSignalDataSet/' + backTestUnderlying + '_' + modelName + '/signalDataSet.pickle',
                                'wb') as f:
                            pickle.dump(signalDataSet, f)
                    else:
                        with open(
                                absolutePath + 'ModelSignalDataSet/' + backTestUnderlying + '_' + modelName + '/signalDataSet.pickle',
                                'rb') as f:
                            signalDataSet = pickle.load(f)

                    # 获取计算该股票需要的数据
                    time1 = dt.datetime.now()
                    if not os.path.exists(
                            absolutePath + 'ModelSignalDataSet/' + backTestUnderlying + '_' + modelName + '/Data.pickle'):
                        print("Loading Tick and Transaction Data")
                        Code = signalDataSet.tradingUnderlyingCode()[0]
                        startTime = dt.datetime.fromtimestamp(
                            signalDataSet.outputByUnderlying()[0]['outSampleSubTag'][0][tagName[0]].startTimeStamp)
                        endTime = dt.datetime.fromtimestamp(
                            signalDataSet.outputByUnderlying()[0]['outSampleSubTag'][-1][tagName[0]].startTimeStamp)
                        startTime = dt.datetime(startTime.year, startTime.month, startTime.day, 9, 30, 0)
                        endTime = dt.datetime(endTime.year, endTime.month, endTime.day, 15, 0, 0)
                        print(startTime)
                        print(endTime)
                        # tickData = GD.getData(Code, startTime, endTime, timeMode=2)
                        # transactionData = GD.getTransactionData(Code, startTime, endTime, timeMode=2)
                        tickData = GD.getInsightTickData(Code, startTime, endTime, timeMode=2)
                        transactionData = GD.getInsightTransactionData(Code, startTime, endTime, True, True, timeMode=2)
                        print("Finish Loading")
                        with open(absolutePath + 'ModelSignalDataSet/' + backTestUnderlying + '_' + modelName + '/Data.pickle', 'wb') as f:
                            pickle.dump((tickData, transactionData), f)
                    else:
                        with open(absolutePath + 'ModelSignalDataSet/' + backTestUnderlying + '_' + modelName + '/Data.pickle', 'rb') as f:
                            tickData, transactionData = pickle.load(f)
                    time2 = dt.datetime.now()
                    print(time2 - time1)

                    # 分析信号产生交易
                    analysisMat = []

                    time1 = dt.datetime.now()
                    for ii in paraMat[0]:
                        for jj in paraMat[1]:
                            signalTagPara = {"longTriggerRatioPercentile": 0,
                                             "shortTriggerRatioPercentile": 100,
                                             "longMinTriggerRatio": ii,
                                             "shortMinTriggerRatio": -ii,
                                             "riskRatio": paraFixed['riskRatio'], "maxLose": paraFixed['maxLose'],
                                             "closeRatio": -ii / 2}

                            # 说明如何使用：
                            # 定义一个变量字典，放入以下所需的变量，具体变量含义可以参考SignalEvaluate的__init__的注释
                            mockTradePara = {"initAmount": jj,
                                             "maxTurnoverPerOrder": paraFixed['maxTurnoverPerOrder'],
                                             "maxRatePerOrder": 0.25,
                                             "maAmountRate": paraFixed['maAmountRate'], "openWithdrawSeconds": 2.5,
                                             "closeWithdrawSeconds": 3,
                                             "buyLevel": 1, "sellLevel": 1, "buyDeviation": 0, "sellDeviation": -0.01,
                                             "MIN_ORDER_QTY": 100}

                            # 实例一个SignalEvaluate，第一个参数为信号变量，第二个为回测变量，第三个用String以类名定义信号分析器
                            # 其余不变
                            signalEvaluate = SignalEvaluate(signalDataSet, signalTagPara, mockTradePara,
                                                            "SignalExecutorMaxMinTag", absolutePath, tickData, transactionData)
                            # 执行
                            rollingCombineTradingOrder = signalEvaluate.evaluate(funStr="signalMaxMinTag", show=False)
                            analysisMat.append([ii, jj, rollingCombineTradingOrder[1][0]['winRate'],
                                                rollingCombineTradingOrder[1][0]['averageReturnRate'],
                                                rollingCombineTradingOrder[1][0]['averagePositionTime'],
                                                rollingCombineTradingOrder[1][0]['timesPerDay']])
                    time2 = dt.datetime.now()
                    print(time2 - time1)
                    bestLine = SignalEvaluate.triggerOptimization(analysisMat)

                    signalTagPara = {"longTriggerRatioPercentile": 0,
                                     "shortTriggerRatioPercentile": 100,
                                     "longMinTriggerRatio": analysisMat[bestLine][0],
                                     "shortMinTriggerRatio": -analysisMat[bestLine][0],
                                     "riskRatio": paraFixed['riskRatio'], "maxLose": paraFixed['maxLose'],
                                     "closeRatio": -analysisMat[bestLine][0] / 2}

                    # 说明如何使用：
                    # 定义一个变量字典，放入以下所需的变量，具体变量含义可以参考SignalEvaluate的__init__的注释
                    mockTradePara = {"initAmount": analysisMat[bestLine][1],
                                     "maxTurnoverPerOrder": paraFixed['maxTurnoverPerOrder'],
                                     "maxRatePerOrder": 0.25,
                                     "maAmountRate": paraFixed['maAmountRate'], "openWithdrawSeconds": 2.5,
                                     "closeWithdrawSeconds": 3,
                                     "buyLevel": 1, "sellLevel": 1, "buyDeviation": 0, "sellDeviation": -0.01,
                                     "MIN_ORDER_QTY": 500}

                    signalEvaluate = SignalEvaluate(signalDataSet, signalTagPara, mockTradePara,
                                                    "SignalExecutorMaxMinTag", absolutePath, tickData, transactionData)
                    # 执行
                    signalEvaluate.evaluate(funStr="signalMaxMinTag", show=True)

                    print('bestLine: ' + str(bestLine))
                    print('TriggerRatio: ' + str(analysisMat[bestLine][0]))
                    print('closeRatio: ' + str(analysisMat[bestLine][1]))
                    # del signalEvaluate
                    del tickData
                    del transactionData
                    gc.collect()


if __name__ == "__main__":
    main()
