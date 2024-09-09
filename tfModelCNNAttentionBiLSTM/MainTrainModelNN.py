# -*- coding: utf-8 -*-
"""
Created on Thu Aug 10 16:37:11 2017

@author: 006547
"""
import sys
import os
# sys.path.append(os.path.abspath(os.path.abspath(__file__) + "/../.."))
# from xquant.pyfile import Pyfile
sys.path.append("../")
from ModelSystem.ModelManagement import ModelManagement
from tfModelCNNAttentionBiLSTM.ModelCNNAttentionBiLSTM import ModelCNNAttentionBiLSTM
from System import DumpLoad
from ModelSystem import SignalEvaluate

sys.path.append("Factor")
sys.path.append("NonFactor")
sys.path.append("Tag")
sys.path.append("System")

code = ["000002-20170202-20180202-31-10min",  # 0
        "000063-20170202-20180202-31-10min",  # 1
        "000568-20170202-20180202-31-10min",  # 2
        "000786-20170202-20180202-31-10min",  # 3
        "000858-20170202-20180202-31-10min",  # 4
        "000977-20170202-20180202-31-10min",  # 5
        "002008-20170202-20180202-31-10min",  # 6
        "002056-20170202-20180202-31-10min",  # 7
        "002128-20170202-20180202-31-10min",  # 8
        "002185-20170202-20180202-31-10min",  # 9
        "002236-20170202-20180202-31-10min",  # 10
        "002241-20170202-20180202-31-10min",  # 11
        "002384-20170202-20180202-31-10min",  # 12
        "002396-20170202-20180202-31-10min",  # 13
        "002407-20170202-20180202-31-10min",  # 14
        "002439-20170202-20180202-31-10min",  # 15
        "002456-20170202-20180202-31-10min",  # 16
        "002460-20170202-20180202-31-10min",  # 17
        "002466-20170202-20180202-31-10min",  # 18
        "002594-20170202-20180202-31-10min",  # 19
        "300101-20170202-20180202-31-10min",  # 20
        "300136-20170202-20180202-31-10min",  # 21
        "300418-20170202-20180202-31-10min",  # 22
        "600498-20170202-20180202-31-10min",  # 23
        "600516-20170202-20180202-31-10min",  # 24
        "600570-20170202-20180202-31-10min",  # 25
        "600703-20170202-20180202-31-10min",  # 26
        "600782-20170202-20180202-31-10min",  # 27
        "601012-20170202-20180202-31-10min",  # 28
        "601231-20170202-20180202-31-10min",  # 29
        "000651-20170202-20180202-31-10min",  # 30
        "000333-20170202-20180202-31-10min",  # 31
        "601318-20170202-20180202-31-10min",  # 32
        "001979-20170202-20180202-31-10min",  # 33
        "601088-20170202-20180202-31-10min",  # 34
        "600004-20170202-20180202-31-10min",  # 35
        "AlgoShaolin-000002.SZ-20170323093000-20180323145659"
        ]


# 读取数据：
GPUID = 0
for i in range(36, 37):
    backTestUnderlying = code[i]
    print(backTestUnderlying)
    factorAddress = '/app/chibh/MachineLearningFactorData/'
    # py = Pyfile()
    # if not py.exists(factorAddress + backTestUnderlying + '.pickle'):
    if not os.path.exists(factorAddress + backTestUnderlying + '.pickle'):
        print('Not FactorData')
    else:
        outputFactor, outputSubTag, tradingUnderlyingCode, factorName = DumpLoad.loadOutput(factorAddress, backTestUnderlying)
        # 设置需要训练的因子
        # factorIndex = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        factorIndex = [0, 4, 5, 10, 11, 12, 14, 15, 16, 18, 19, 20, 21, 22, 23, 26, 27, 28, 29, 30, 31, 38, 40]
        # factorIndex = [0, 6, 10, 11, 12]
        # factorIndex = [0, 4, 5, 10, 11, 12, 14, 15, 16, 18, 19, 28]
        for j in [100]:
            for k in [0.2]:
                absolutePath = ""
                tagName = "1min"
                predictRollingWindow = k
                sliceLag = j
                conv_len = 3
                # 建立模型管理模块
                modelManagement = ModelManagement(trainRollingWindow=1 - predictRollingWindow,
                                                  predictRollingWindow=predictRollingWindow, outputFactor=outputFactor,
                                                  outputSubTag=outputSubTag, tradingUnderlyingCode=tradingUnderlyingCode,
                                                  factorName=factorName, factorIndex=factorIndex,
                                                  backTestUnderlying=backTestUnderlying)
                # 设置模型参数

                paraModel = {"absolutePath": absolutePath, "GPUID": GPUID, "validationNum": 40000, 'sliceLag': sliceLag, 'conv_len': conv_len,
                             "evaluateModel": {"percentileErrorRatio": 70, "triggerRatio": 0.002}}
                modelCNNRNN = ModelCNNAttentionBiLSTM(paraModel=paraModel, name="modelCNNRNN" + tagName + "Pred" + str(
                    predictRollingWindow) + 'SliceLag' + str(sliceLag), tagName=tagName, modelManagement=modelManagement)

                # 训练模型
                modelManagement.train()
                signalTagPara = {"longTriggerRatioPercentile": 99.5, "shortTriggerRatioPercentile": 0.5,
                                 "longMinTriggerRatio": 0.0025, "shortMinTriggerRatio": -0.0025, "maxLose": -0.1}
                # 分析信号产生交易
                rollingTradingOrder1, combineTradingOrder1 = SignalEvaluate.evaluate(
                    signalTagPara, "signalTag", absolutePath,
                    "modelCNNRNN" + tagName + "Pred" + str(predictRollingWindow) + 'SliceLag' + str(sliceLag),
                    modelManagement, transaction=False)
