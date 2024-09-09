# -*- coding: utf-8 -*-
"""
Created on Thu Aug 10 16:37:11 2017

@author: 006547
"""
import sys


from System import DumpLoad
from System import Tools
from System.Strategy import Strategy
from System.StrategyManagement import StrategyManagement
import json


sys.path.append("Factor")
sys.path.append("NonFactor")
sys.path.append("Tag")
sys.path.append("System")


factorSetJsonFile = "AlgoConfig.py"
# 建立策略管理模块用于存放策略
strategyManagement = StrategyManagement()
# 建立策略设置策略参数
with open(factorSetJsonFile, 'r') as file:
    para = json.load(file)
    strategyinst = Strategy()
    strategyinst.setStrategyName(para["StrategyName"])
    # strategyinst.setTradingUnderlyingCode(para["TradingUnderlyingCode"])
    strategyinst.setFactorUnderlyingCode(para["FactorUnderlyingCode"])
    strategyinst.setTradingUnderlyingCode([['TA.CZC']])
    # strategyinst.setParaFactor(para["FactorSet"])
    FactorSet = [
                {"name": "factorVolumeMagnification", "className": "FactorVolumeMagnification", "indexTradingUnderlying": [0],# 0
                 "indexFactorUnderlying": [], "paraFastLag": 40, "paraSlowLag": None, "save": True},

                {"name": "factorPriceChangeRatio", "className": "FactorPriceChangeRatio",
                 "indexTradingUnderlying": [0], "indexFactorUnderlying": [], "paraFastLag": 40, "paraSlowLag": 80,
                 "save": True},  # 1

                {"name": "factorPriceChangeSpeed", "className": "FactorPriceChangeSpeed",  # 2
                 "indexTradingUnderlying": [0], "indexFactorUnderlying": [], "paraFastLag": 40, "paraSlowLag": 80,
                 "save": True},

                {"name": "factorSpeed", "className": "FactorSpeed", "indexTradingUnderlying": [0], "indexFactorUnderlying": [],
                 # 3
                 "paraLag": 40.0, "paraEmaMidPriceLag": 16, "save": True},

                {"name": "factorEmaSlicePressure", "className": "FactorEmaSlicePressure", "indexTradingUnderlying": [0],
                 "indexFactorUnderlying": [], "paraNumOrderMax": 5, "paraNumOrderMin": 1, "paraEmaSlicePressureLag": 32,
                 "save": True},  # 4

                {"name": "factorAveAmplitude", "className": "FactorAveAmplitude", "indexTradingUnderlying": [0],  # 5
                 "indexFactorUnderlying": [], "paraAmplitudeLag": 20, "paraFastLag": 40, "paraSlowLag": 80, "save": True},

                {"name": "factorOrderPressure", "className": "FactorOrderPressure", "indexTradingUnderlying": [0],  # 6
                 "indexFactorUnderlying": [], "paraOrderPressureLag": 16, "save": True},

                {"name": "factorEmaOrderPressureBuy", "className": "FactorEmaOrderPressureBuy", "indexTradingUnderlying": [0],# 7
                 "indexFactorUnderlying": [], "paraOrderPressureLag": 16, "save": True},

                {"name": "factorEmaOrderPressureSell", "className": "FactorEmaOrderPressureSell", "indexTradingUnderlying": [0],# 8
                 "indexFactorUnderlying": [], "paraOrderPressureLag": 16, "save": True},

                {"name": "factorEmaBidHugeOrderMultiple1", "className": "FactorEmaBidHugeOrderMultiple",
                 "indexTradingUnderlying": [0], "indexFactorUnderlying": [],
                 "paraLag": 2, "paraNumOrderMax": 3, "paraNumOrderMin": 1, "paraNumOrderMaxForAveOrderVolume": 5,
                 "paraNumOrderMinForAveOrderVolume": 1, "paraEmaAveOrderVolumeLag": None, "save": True},                    # 9

                {"name": "factorEmaAskHugeOrderMultiple1", "className": "FactorEmaAskHugeOrderMultiple",
                 "indexTradingUnderlying": [0], "indexFactorUnderlying": [],
                 "paraLag": 2, "paraNumOrderMax": 3, "paraNumOrderMin": 1, "paraNumOrderMaxForAveOrderVolume": 5,
                 "paraNumOrderMinForAveOrderVolume": 1, "paraEmaAveOrderVolumeLag": None, "save": True},  # 10

                {"name": "factorEmaBidHugeOrderMultiple2", "className": "FactorEmaBidHugeOrderMultiple",  # 11
                 "indexTradingUnderlying": [0], "indexFactorUnderlying": [],
                 "paraLag": 2, "paraNumOrderMax": 4, "paraNumOrderMin": 2, "paraNumOrderMaxForAveOrderVolume": 5,
                 "paraNumOrderMinForAveOrderVolume": 1, "paraEmaAveOrderVolumeLag": None, "save": True},

                {"name": "factorEmaAskHugeOrderMultiple2", "className": "FactorEmaAskHugeOrderMultiple",  # 12
                 "indexTradingUnderlying": [0], "indexFactorUnderlying": [],
                 "paraLag": 2, "paraNumOrderMax": 4, "paraNumOrderMin": 2, "paraNumOrderMaxForAveOrderVolume": 5,
                 "paraNumOrderMinForAveOrderVolume": 1, "paraEmaAveOrderVolumeLag": None, "save": True},

                {"name": "factorEmaBidHugeOrderMultiple3", "className": "FactorEmaBidHugeOrderMultiple",  # 13
                 "indexTradingUnderlying": [0], "indexFactorUnderlying": [],
                 "paraLag": 2, "paraNumOrderMax": 5, "paraNumOrderMin": 3, "paraNumOrderMaxForAveOrderVolume": 5,
                 "paraNumOrderMinForAveOrderVolume": 1, "paraEmaAveOrderVolumeLag": None, "save": True},

                {"name": "factorEmaAskHugeOrderMultiple3", "className": "FactorEmaAskHugeOrderMultiple",  # 14
                 "indexTradingUnderlying": [0], "indexFactorUnderlying": [],
                 "paraLag": 2, "paraNumOrderMax": 5, "paraNumOrderMin": 3, "paraNumOrderMaxForAveOrderVolume": 5,
                 "paraNumOrderMinForAveOrderVolume": 1, "paraEmaAveOrderVolumeLag": None, "save": True},

                {"name": "factorEmaBidOrderBookMultiple1", "className": "FactorEmaBidOrderBookMultiple",  # 15
                 "indexTradingUnderlying": [0], "indexFactorUnderlying": [],
                 "paraLag": 2, "paraNumOrderMax": 3, "paraNumOrderMin": 1, "paraNumOrderMaxForAveOrderVolume": 5,
                 "paraNumOrderMinForAveOrderVolume": 1, "paraEmaAveOrderVolumeLag": None, "save": True},

                {"name": "factorEmaAskOrderBookMultiple1", "className": "FactorEmaAskOrderBookMultiple",  # 16
                 "indexTradingUnderlying": [0], "indexFactorUnderlying": [],
                 "paraLag": 2, "paraNumOrderMax": 3, "paraNumOrderMin": 1, "paraNumOrderMaxForAveOrderVolume": 5,
                 "paraNumOrderMinForAveOrderVolume": 1, "paraEmaAveOrderVolumeLag": None, "save": True},

                {"name": "factorEmaBidOrderBookMultiple2", "className": "FactorEmaBidOrderBookMultiple",  # 17
                 "indexTradingUnderlying": [0], "indexFactorUnderlying": [],
                 "paraLag": 2, "paraNumOrderMax": 4, "paraNumOrderMin":2, "paraNumOrderMaxForAveOrderVolume": 5,
                 "paraNumOrderMinForAveOrderVolume": 1, "paraEmaAveOrderVolumeLag": None, "save": True},

                {"name": "factorEmaAskOrderBookMultiple2", "className": "FactorEmaAskOrderBookMultiple",  # 18
                 "indexTradingUnderlying": [0], "indexFactorUnderlying": [],
                 "paraLag": 2, "paraNumOrderMax": 4, "paraNumOrderMin": 2, "paraNumOrderMaxForAveOrderVolume": 5,
                 "paraNumOrderMinForAveOrderVolume": 1, "paraEmaAveOrderVolumeLag": None, "save": True},

                {"name": "factorEmaBidOrderBookMultiple3", "className": "FactorEmaBidOrderBookMultiple",  # 19
                 "indexTradingUnderlying": [0], "indexFactorUnderlying": [],
                 "paraLag": 2, "paraNumOrderMax": 5, "paraNumOrderMin": 3, "paraNumOrderMaxForAveOrderVolume": 5,
                 "paraNumOrderMinForAveOrderVolume": 1, "paraEmaAveOrderVolumeLag": None, "save": True},

                {"name": "factorEmaAskOrderBookMultiple3", "className": "FactorEmaAskOrderBookMultiple",  # 20
                 "indexTradingUnderlying": [0], "indexFactorUnderlying": [],
                 "paraLag": 2, "paraNumOrderMax": 5, "paraNumOrderMin": 3, "paraNumOrderMaxForAveOrderVolume": 5,
                 "paraNumOrderMinForAveOrderVolume": 1, "paraEmaAveOrderVolumeLag": None, "save": True},

                {"name": "factorDistanceToAvePrice", "className": "FactorDistanceToAvePrice", "indexTradingUnderlying": [0],# 21
                 "indexFactorUnderlying": [], "save": True},

                {"name": "factorDistanceToMAPrice", "className": "FactorDistanceToMAPrice", "indexTradingUnderlying": [0],  # 22
                 "indexFactorUnderlying": [], "paraMALag": 480, "save": True},
                #
                {"name": "factorDistanceBetweenVWAPPrice40", "className": "FactorDistanceBetweenVWAPPrice",                       # 23新
                 "indexTradingUnderlying": [0], "indexFactorUnderlying": [], "paraFastLag": 3, "paraSlowLag": 40, "save": True},

                {"name": "factorDistanceBetweenVWAPPrice20", "className": "FactorDistanceBetweenVWAPPrice",                       # 24新
                 "indexTradingUnderlying": [0], "indexFactorUnderlying": [], "paraFastLag": 3, "paraSlowLag": 20, "save": True},

                {"name": "factorDistanceBetweenVWAPPrice100", "className": "FactorDistanceBetweenVWAPPrice",                       # 25新
                 "indexTradingUnderlying": [0], "indexFactorUnderlying": [], "paraFastLag": 3, "paraSlowLag": 100, "save": True},

                {"name": "factorDistanceBetweenVWAPPrice200", "className": "FactorDistanceBetweenVWAPPrice",                       # 26新
                 "indexTradingUnderlying": [0], "indexFactorUnderlying": [], "paraFastLag": 3, "paraSlowLag": 200, "save": True},

                {"name": "factorAccumSellPower", "className": "FactorAccumSellPower", "indexTradingUnderlying": [0],  # 28新
                 "indexFactorUnderlying": [], "paraMAVolumeLag": 30000, "save": True},

                {"name": "factorAccumBuyPower", "className": "FactorAccumBuyPower", "indexTradingUnderlying": [0],  # 29新
                 "indexFactorUnderlying": [], "paraMAVolumeLag": 30000, "save": True},

                {"name": "factorMAVolumeDistance100", "className": "FactorMAVolumeDistance", "indexTradingUnderlying": [0], # 27新
                 "indexFactorUnderlying": [], "paraMAFastLag": 100, "paraMASlowLag": 30000, "save": True},

                {"name": "factorMAVolumeDistance3", "className": "FactorMAVolumeDistance", "indexTradingUnderlying": [0],   # 28新
                 "indexFactorUnderlying": [], "paraMAFastLag": 3, "paraMASlowLag": 30000, "save": True},

                {"name": "factorMAVolumeDistance20", "className": "FactorMAVolumeDistance", "indexTradingUnderlying": [0],    # 29新
                 "indexFactorUnderlying": [], "paraMAFastLag": 20, "paraMASlowLag": 30000, "save": True},

                {"name": "factorMAVolumeDistance200", "className": "FactorMAVolumeDistance",
                 "indexTradingUnderlying": [0],
                 "indexFactorUnderlying": [], "paraMAFastLag": 200, "paraMASlowLag": 30000, "save": True},                  # 30新

                {"name": "factorMaAmount", "className": "FactorMaAmount", "indexTradingUnderlying": [0],                  # 31新
                 "indexFactorUnderlying": [], "paraLag": 2, "save": True}
        ]

    strategyinst.setParaFactor(FactorSet)
    strategyinst.setParaTag(para["Tag"])
    strategyinst.setStartDateTime(20180101093000)
    strategyinst.setEndDateTime(20180131145659)
    strategyinst.setOutputDir(para["outputDir"])

    strategyManagement.registerStrategy(strategyinst)
    # %%
    # 载入数据
    strategyManagement.loadData()
    # %%
    # 运行策略
    strategyManagement.start()
    # 将因子输出到Excel
    # Tools.exportExecl(strategyinst)
    # 把因子的数据结构存下来
    DumpLoad.dumpOutput(strategyinst)

    # 读取方法：
    # outputFactor, outputSubTag, tradingUnderlyingCode, factorName = DumpLoad.loadOutput(strategy1.getStrategyName())

    print("This line is for setting breakpoint")
