# -*- coding: utf-8 -*-
"""
Created on 2017/10/19 9:27

@author: 006547
"""
import sys
import os
# sys.path.append(os.path.abspath(os.path.abspath(__file__) + "/../.."))
# from xquant.pyfile import Pyfile
sys.path.append("../")
from ModelSystem.ModelManagement import ModelManagement
from xgModel.ModelXgBoost import ModelXgBoost
from System import DumpLoad
from ModelSystem import SignalEvaluate


sys.path.append("Factor")
sys.path.append("NonFactor")
sys.path.append("Tag")
sys.path.append("System")

code = ["000002-20170126-20180126-31-10min",  # 0
        "000063-20170126-20180126-31-10min",  # 1
        "000568-20170126-20180126-31-10min",  # 2
        "000786-20170126-20180126-31-10min",  # 3
        "000858-20170126-20180126-31-10min",  # 4
        "000977-20170126-20180126-31-10min",  # 5
        "002008-20170126-20180126-31-10min",  # 6
        "002056-20170126-20180126-31-10min",  # 7
        "002128-20170126-20180126-31-10min",  # 8
        "002185-20170126-20180126-31-10min",  # 9
        "002236-20170126-20180126-31-10min",  # 10
        "002241-20170126-20180126-31-10min",  # 11
        "002384-20170126-20180126-31-10min",  # 12
        "002396-20170126-20180126-31-10min",  # 13
        "002407-20170126-20180126-31-10min",  # 14
        "002439-20170126-20180126-31-10min",  # 15
        "002456-20170126-20180126-31-10min",  # 16
        "002460-20170126-20180126-31-10min",  # 17
        "002466-20170126-20180126-31-10min",  # 18
        "002594-20170126-20180126-31-10min",  # 19
        "300101-20170126-20180126-31-10min",  # 20
        "300136-20170126-20180126-31-10min",  # 21
        "300418-20170126-20180126-31-10min",  # 22
        "600498-20170126-20180126-31-10min",  # 23
        "600516-20170126-20180126-31-10min",  # 24
        "600570-20170126-20180126-31-10min",  # 25
        "600703-20170126-20180126-31-10min",  # 26
        "600782-20170126-20180126-31-10min",  # 27
        "601012-20170126-20180126-31-10min",  # 28
        "601231-20170126-20180126-31-10min",  # 29
        "000651-20170126-20180126-31-10min",  # 30
        "000333-20170126-20180126-31-10min",  # 31
        "601318-20170126-20180126-31-10min",  # 32
        "001979-20170126-20180126-31-10min",  # 33
        "601088-20170126-20180126-31-10min",  # 34
        "600004-20170126-20180126-31-10min",  # 35
        ]


# 读取数据：
for i in range(24, 25):
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
        # factorIndex = [0, 6, 10, 11, 12, 14, 15, 16, 17, 18, 19, 21, 22, 23, 24, 25, 26, 33, 36, 37, 38, 40]
        # factorIndex = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 25, 28]
        factorIndex = [0, 4, 5, 10, 11, 12, 14, 15, 16, 18, 19, 28]
        absolutePath = ""
        # 建立模型管理模块
        predictRollingWindow = 0.2
        modelManagement = ModelManagement(trainRollingWindow=1 - predictRollingWindow,
                                          predictRollingWindow=predictRollingWindow, outputFactor=outputFactor,
                                          outputSubTag=outputSubTag, tradingUnderlyingCode=tradingUnderlyingCode,
                                          factorName=factorName, factorIndex=factorIndex,
                                          backTestUnderlying=backTestUnderlying)
        # 设置模型参数
        paraModel = {"para": {'bst:max_depth': 6, 'bst:eta': 0.005, 'gamma': 0.0015, 'silent': 0, 'objective': 'reg:linear', 'eval_metric': "rmse"},
                     "numRound": 500, "validationRatio": 0.2, "earlyStoppingRounds": 20,
                     "evaluateModel": {"percentileErrorRatio": 70, "triggerRatio": 0.0015}}

        modelXgBoost1 = ModelXgBoost(paraModel=paraModel, name="modelXgBoostBreakLongShort", tagName="breakLongShort",
                                     modelManagement=modelManagement)
        modelXgBoost2 = ModelXgBoost(paraModel=paraModel, name="modelXgBoostReversalLongShort", tagName="reversalLongShort",
                                     modelManagement=modelManagement)
        modelXgBoost3 = ModelXgBoost(paraModel=paraModel, name="modelXgBoost1min", tagName="1min",
                                     modelManagement=modelManagement)

        # 训练模型
        modelManagement.train()
        # 设置用于处理信号的参数
        tradingTagPara = {"longTriggerRatioPercentile": 99.5, "shortTriggerRatioPercentile": 0.5,
                          "longMinTriggerRatio": 0.0015, "shortMinTriggerRatio": -0.0015, "maxLose": -0.1}
        signalTagPara = {"longTriggerRatioPercentile": 99.5, "shortTriggerRatioPercentile": 0.5,
                         "longMinTriggerRatio": 0.0015, "shortMinTriggerRatio": -0.0015, "maxLose": -0.1}
        # 分析信号产生交易
        rollingTradingOrder1, combineTradingOrder1 = SignalEvaluate.evaluate(
            tradingTagPara, "tradingTag", absolutePath, "modelXgBoostBreakLongShort", modelManagement)
        rollingTradingOrder2, combineTradingOrder2 = SignalEvaluate.evaluate(
            tradingTagPara, "tradingTag", absolutePath, "modelXgBoostReversalLongShort", modelManagement)
        rollingTradingOrder3, combineTradingOrder3 = SignalEvaluate.evaluate(
            signalTagPara, "signalTag", absolutePath, "modelXgBoost1min", modelManagement)
        print("This line is for setting breakpoint")

