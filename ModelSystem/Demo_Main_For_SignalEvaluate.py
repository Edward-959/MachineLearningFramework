 # -*- coding: utf-8 -*-
#
# Created on Thu Aug 10 16:37:11 2017
#
# @author: 006547

import tensorflow as tf
with tf.device('/cpu:2'):
    import sys
    import os
    # sys.path.append(os.path.abspath(os.path.abspath(__file__) + "/../.."))
    # from xquant.pyfile import Pyfile
    sys.path.append("../")
    from ModelSystem.ModelManagement import ModelManagement
    from tfModel.ModelCNNRNN import ModelCNNRNN
    from System import DumpLoad
    from ModelSystem.SignalEvaluate import SignalEvaluate
    from ModelSystem.Util.SignalDataSet import generateSignalDataSet
    from ModelSystem.Util.FactorForSignalToPickle import FactorsToPickleEase
    import numpy as np

    sys.path.append("Factor")
    sys.path.append("NonFactor")
    sys.path.append("Tag")
    sys.path.append("System")

    # code = ["000002-20170126-20180126-31-10min",  # 0
    #         "000063-20170126-20180126-31-10min",  # 1
    #         "000568-20170126-20180126-31-10min",  # 2
    #         "000786-20170126-20180126-31-10min",  # 3
    #         "000858-20170126-20180126-31-10min",  # 4
    #         "000977-20170126-20180126-31-10min",  # 5
    #         "002008-20170126-20180126-31-10min",  # 6
    #         "002056-20170126-20180126-31-10min",  # 7
    #         "002128-20170126-20180126-31-10min",  # 8
    #         "002185-20170126-20180126-31-10min",  # 9
    #         "002236-20170126-20180126-31-10min",  # 10
    #         "002241-20170126-20180126-31-10min",  # 11
    #         "002384-20170126-20180126-31-10min",  # 12
    #         "002396-20170126-20180126-31-10min",  # 13
    #         "002407-20170126-20180126-31-10min",  # 14
    #         "002439-20170126-20180126-31-10min",  # 15
    #         "002456-20170126-20180126-31-10min",  # 16
    #         "002460-20170126-20180126-31-10min",  # 17
    #         "002466-20170126-20180126-31-10min",  # 18
    #         "002594-20170126-20180126-31-10min",  # 19
    #         "300101-20170126-20180126-31-10min",  # 20
    #         "300136-20170126-20180126-31-10min",  # 21
    #         "300418-20170126-20180126-31-10min",  # 22
    #         "600498-20170126-20180126-31-10min",  # 23
    #         "600516-20170126-20180126-31-10min",  # 24
    #         "600570-20170126-20180126-31-10min",  # 25
    #         "600703-20170126-20180126-31-10min",  # 26
    #         "600782-20170126-20180126-31-10min",  # 27
    #         "601012-20170126-20180126-31-10min",  # 28
    #         "601231-20170126-20180126-31-10min",  # 29
    #         "000651-20170126-20180126-31-10min",  # 30
    #         "000333-20170126-20180126-31-10min",  # 31
    #         "601318-20170126-20180126-31-10min",  # 32
    #         "001979-20170126-20180126-31-10min",  # 33
    #         "601088-20170126-20180126-31-10min",  # 34
    #         "600004-20170126-20180126-31-10min",  # 35
    #         ]

    code = ["AlgoShaolin-000002.SZ-20180223093000-20180323145659"]


    # 读取数据：
    GPUID = 0
    for i in range(len(code)):
        backTestUnderlying = code[i]
        print(backTestUnderlying)
        factorAddress = '/home/gudh/'
        # py = Pyfile()
        # if not py.exists(factorAddress + backTestUnderlying + '.pickle'):
        if not os.path.exists(factorAddress + backTestUnderlying + '.pickle'):
            print('Not FactorData')
        else:
            outputFactor, outputSubTag, tradingUnderlyingCode, factorName = DumpLoad.loadOutput(factorAddress, backTestUnderlying)
            factorIndex = [0, 4, 5, 10, 11, 12, 14, 15, 16, 18, 19, 20, 21, 22, 23, 26, 27, 28, 29, 30, 31, 38, 40]
            # New: deprecated. 之后将删除此变量。现在保留此数值，方便在mode = False时，老pickle文件能load和使用。
            factorMaAmountIndex = 41
            # New: 建议使用list，并一起加入上面的因子序号，在ModelManagement中会生成一个新的字典，字典的具体格式如下：
            # factorForSignalDict = {key = symbol, value = {key = timestamp, value = {factorName, value}}}
            # please make sure that the factor name is unique
            factorIndexForSignal = [41, 0, 23]  # 0, 23 are just examples
            factorIndexForSignalToPickle = [41, 0, 23]  # 单独导出数据，方便交易小组测试

            for j in [150]:
                for k in [0.2, 0.01]:
                    absolutePath = ""
                    tagName = "1min"
                    predictRollingWindow = k
                    sliceLag = j
                    conv_len = 3
                    # 建立模型管理模块
                    # New: 在ModelManagement新加入了tagName
                    modelManagement = ModelManagement(trainRollingWindow=1 - predictRollingWindow,
                                                      predictRollingWindow=predictRollingWindow,
                                                      outputFactor=outputFactor,
                                                      outputSubTag=outputSubTag,
                                                      tradingUnderlyingCode=tradingUnderlyingCode,
                                                      factorName=factorName, factorIndex=factorIndex,
                                                      factorMaAmountIndex=factorMaAmountIndex,
                                                      factorIndexForSignal=factorIndexForSignal,
                                                      backTestUnderlying=backTestUnderlying, tagName=tagName)
                    # 设置模型参数
                    # 规范modelName
                    paraModel = {"absolutePath": absolutePath, "GPUID": GPUID, "validationNum": 40000, 'sliceLag': sliceLag, 'conv_len': conv_len,
                                 "evaluateModel": {"percentileErrorRatio": 70, "triggerRatio": 0.002}}
                    modelName = "modelCNNRNN" + tagName + "Pred" + str(predictRollingWindow) + 'SliceLag' + str(sliceLag)
                    modelCNNRNN = ModelCNNRNN(paraModel=paraModel, name=modelName, tagName=tagName, modelManagement=modelManagement)

                    # 把要传到SignalEvaluate的因子导出成pickle文件，可以放在mode判断外
                    dir_path = "ModelSaved/" + backTestUnderlying + '_' + modelName + '_SavedModelBuilder' + "/FactorForSignal.pickle"
                    FactorsToPickleEase(outputFactor, outputSubTag, tagName, factorName, factorIndexForSignalToPickle,
                                        tradingUnderlyingCode, predictRollingWindow, dir_path)

                    # 训练模型
                    modelManagement.train()
                    # 分析信号产生交易
                    signalTagPara = {"longTriggerRatioPercentile": 80, "shortTriggerRatioPercentile": 20, "closeRatio": 0,
                                     "longMinTriggerRatio": 0.0002, "shortMinTriggerRatio": -0.0002, "maxLose": -0.1}

                    # 生成signalDataSet，以便拆分数据，多进程操作
                    signalDataSet = generateSignalDataSet(modelName, modelManagement)
                    # 从pickle文件导入因子值，并融合进SignalDataSet
                    signalDataSet = signalDataSet.combineFromFactorForSignalPickle(dir_path)

                    # 说明如何使用：
                    # 定义一个变量字典，放入以下所需的变量，具体变量含义可以参考SignalEvaluate的__init__的注释
                    mockTradePara = {"initAmount": 100000, "maxTurnoverPerOrder": 1000000, "maxRatePerOrder": 0.25,
                                     "maAmountRate": 1, "openWithdrawSeconds": 2.5, "closeWithdrawSeconds": 3,
                                     "buyLevel": 1, "sellLevel": 1, "buyDeviation": 0, "sellDeviation": -0.01,
                                     "MIN_ORDER_QTY": 500}

                    # 实例一个SignalEvaluate
                    signalEvaluate = SignalEvaluate(signalDataSet, signalTagPara, mockTradePara,
                                                    "SignalExecutorSignalTag", absolutePath, tickData=None,
                                                    transactionData=None)
                    # 执行
                    rollingTradingOrder1, combineTradingOrder1 = signalEvaluate.evaluate()
