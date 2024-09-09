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
TradingUnderlyingCode = [
                          ["000025.SZ"],
                          ["000049.SZ"],
                          ["000732.SZ"],
                          ["002038.SZ"],
                          ["002268.SZ"],
                          ["002745.SZ"],
                          ["002815.SZ"],
                          ["002818.SZ"],
                          ["300413.SZ"],
                          ["600161.SH"],
                          ["600201.SH"],
                          ["600258.SH"],
                          ["600259.SH"],
                          ["600260.SH"],
                          ["600298.SH"],
                          ["600338.SH"]],
                          # ["600511.SH"],
                          # ["600694.SH"],
                          # ["600699.SH"],
                          # ["600729.SH"],
                          # ["600754.SH"],
                          # ["601100.SH"],
                          # ["603025.SH"],
                          # ["603355.SH"],
                          # ["603377.SH"],
                          # ["603556.SH"],
                          # ["603806.SH"]],
# 建立策略设置策略参数
for stock in TradingUnderlyingCode[0]:
    strategyManagement = StrategyManagement()
    with open(factorSetJsonFile, 'r') as file:
        para = json.load(file)
        strategyinst = Strategy()
        strategyinst.setStrategyName(para["StrategyName"])
        strategyinst.setTradingUnderlyingCode([stock])
        strategyinst.setFactorUnderlyingCode(para["FactorUnderlyingCode"])
        factorSet = \
            [
                {"name": "factorVolumeMagnification", "className": "FactorVolumeMagnification",
                 "indexTradingUnderlying": [0],
                 "indexFactorUnderlying": [], "paraFastLag": 10, "paraSlowLag": None, "save": True},
                #
                {"name": "factorBreakHugeAskOrder", "className": "FactorBreakHugeAskOrder", "indexTradingUnderlying": [0],
                 "indexFactorUnderlying": [], "paraOldTargetVolumeShrink": 0.5, "paraOldTargetPriceSpace": 0.003,
                 "paraMinPressureRate": 4, "paraEmaAveOrderVolumeLag": None,
                 "paraMinPressureAmount": 15, "paraTargetVolumeLeft": 0.5, "paraNumOrderMax": 10, "paraNumOrderMin": 1,
                 "save": True},
                #
                {"name": "factorBreakHugeBidOrder", "className": "FactorBreakHugeBidOrder", "indexTradingUnderlying": [0],
                 "indexFactorUnderlying": [], "paraOldTargetVolumeShrink": 0.5, "paraOldTargetPriceSpace": 0.003,
                 "paraMinPressureRate": 4, "paraEmaAveOrderVolumeLag": None,
                 "paraMinPressureAmount": 15, "paraTargetVolumeLeft": 0.5, "paraNumOrderMax": 10, "paraNumOrderMin": 1,
                 "save": True},

                # {"name": "factorPierceNum", "className": "FactorPierceNum", "indexTradingUnderlying": [0],
                #  "indexFactorUnderlying": [], "paraMinSupportRate": 2, "paraMinSupportAmount": 20,
                #  "paraFastLag": 10, "paraSlowLag": 20, "save": True},

                {"name": "factorPriceChangeRatio", "className": "FactorPriceChangeRatio",
                 "indexTradingUnderlying": [0], "indexFactorUnderlying": [], "paraFastLag": 10, "paraSlowLag": 20,
                 "save": True},

                {"name": "factorPriceChangeSpeed", "className": "FactorPriceChangeSpeed",
                 "indexTradingUnderlying": [0], "indexFactorUnderlying": [], "paraFastLag": 10, "paraSlowLag": 20,
                 "save": True},

                {"name": "factorBreakUpShape", "className": "FactorBreakUpShape", "indexTradingUnderlying": [0],
                 "indexFactorUnderlying": [], "paraLowestRatio": 0.5, "paraFastLag": 10, "paraSlowLag": 20, "save": True},

                {"name": "factorBreakDownShape", "className": "FactorBreakDownShape", "indexTradingUnderlying": [0],
                 "indexFactorUnderlying": [], "paraHighestRatio": 0.5, "paraFastLag": 10, "paraSlowLag": 20, "save": True},

                {"name": "factorDistanceToBreakUpPrice", "className": "FactorDistanceToBreakUpPrice",
                 "indexTradingUnderlying": [0],
                 "indexFactorUnderlying": [], "paraLowestRatio": 0.5, "paraFastLag": 10, "paraSlowLag": 20, "save": True},
                #
                {"name": "factorDistanceToBreakDownPrice", "className": "FactorDistanceToBreakDownPrice",
                 "indexTradingUnderlying": [0], "indexFactorUnderlying": [], "paraHighestRatio": 0.5, "paraFastLag": 10,
                 "paraSlowLag": 20, "save": True},

                {"name": "factorSpeed", "className": "FactorSpeed", "indexTradingUnderlying": [0],
                 "indexFactorUnderlying": [],
                 "paraLag": 10.0, "paraEmaMidPriceLag": 4, "save": True},

                {"name": "factorEmaSlicePressure", "className": "FactorEmaSlicePressure", "indexTradingUnderlying": [0],
                 "indexFactorUnderlying": [], "paraNumOrderMax": 5, "paraNumOrderMin": 1, "paraEmaSlicePressureLag": 8,
                 "save": True},

                {"name": "factorAveAmplitude", "className": "FactorAveAmplitude", "indexTradingUnderlying": [0],
                 "indexFactorUnderlying": [], "paraAmplitudeLag": 5, "paraFastLag": 10, "paraSlowLag": 20, "save": True},

                {"name": "factorAvePriceAmplitude", "className": "FactorAvePriceAmplitude", "indexTradingUnderlying": [0],
                 "indexFactorUnderlying": [], "paraPriceAmplitudeLag": 5, "paraFastLag": 10, "paraSlowLag": 20,
                 "save": True},

                {"name": "factorOrderPressure", "className": "FactorOrderPressure", "indexTradingUnderlying": [0],
                 "indexFactorUnderlying": [], "paraOrderPressureLag": 4, "save": True},

                {"name": "factorEmaOrderPressureBuy", "className": "FactorEmaOrderPressureBuy",
                 "indexTradingUnderlying": [0],
                 "indexFactorUnderlying": [], "paraOrderPressureLag": 4, "save": True},

                {"name": "factorEmaOrderPressureSell", "className": "FactorEmaOrderPressureSell",
                 "indexTradingUnderlying": [0],
                 "indexFactorUnderlying": [], "paraOrderPressureLag": 4, "save": True},
                #
                {"name": "factorOrderPressureDuration", "className": "FactorOrderPressureDuration",
                 "indexTradingUnderlying": [0],
                 "indexFactorUnderlying": [], "paraOrderPressureLag": 4, "paraHorizon": 0, "save": True},

                {"name": "factorEmaBidHugeOrderMultiple1", "className": "FactorEmaBidHugeOrderMultiple",
                 "indexTradingUnderlying": [0], "indexFactorUnderlying": [],
                 "paraLag": 2, "paraNumOrderMax": 3, "paraNumOrderMin": 1, "paraNumOrderMaxForAveOrderVolume": 10,
                 "paraNumOrderMinForAveOrderVolume": 1, "paraEmaAveOrderVolumeLag": None, "save": True},

                {"name": "factorEmaAskHugeOrderMultiple1", "className": "FactorEmaAskHugeOrderMultiple",
                 "indexTradingUnderlying": [0], "indexFactorUnderlying": [],
                 "paraLag": 2, "paraNumOrderMax": 3, "paraNumOrderMin": 1, "paraNumOrderMaxForAveOrderVolume": 10,
                 "paraNumOrderMinForAveOrderVolume": 1, "paraEmaAveOrderVolumeLag": None, "save": True},

                {"name": "factorEmaBidHugeOrderMultiple2", "className": "FactorEmaBidHugeOrderMultiple",
                 "indexTradingUnderlying": [0], "indexFactorUnderlying": [],
                 "paraLag": 2, "paraNumOrderMax": 7, "paraNumOrderMin": 4, "paraNumOrderMaxForAveOrderVolume": 10,
                 "paraNumOrderMinForAveOrderVolume": 1, "paraEmaAveOrderVolumeLag": None, "save": True},

                {"name": "factorEmaAskHugeOrderMultiple2", "className": "FactorEmaAskHugeOrderMultiple",
                 "indexTradingUnderlying": [0], "indexFactorUnderlying": [],
                 "paraLag": 2, "paraNumOrderMax": 7, "paraNumOrderMin": 4, "paraNumOrderMaxForAveOrderVolume": 10,
                 "paraNumOrderMinForAveOrderVolume": 1, "paraEmaAveOrderVolumeLag": None, "save": True},

                {"name": "factorEmaBidHugeOrderMultiple3", "className": "FactorEmaBidHugeOrderMultiple",
                 "indexTradingUnderlying": [0], "indexFactorUnderlying": [],
                 "paraLag": 2, "paraNumOrderMax": 10, "paraNumOrderMin": 8, "paraNumOrderMaxForAveOrderVolume": 10,
                 "paraNumOrderMinForAveOrderVolume": 1, "paraEmaAveOrderVolumeLag": None, "save": True},

                {"name": "factorEmaAskHugeOrderMultiple3", "className": "FactorEmaAskHugeOrderMultiple",
                 "indexTradingUnderlying": [0], "indexFactorUnderlying": [],
                 "paraLag": 2, "paraNumOrderMax": 10, "paraNumOrderMin": 8, "paraNumOrderMaxForAveOrderVolume": 10,
                 "paraNumOrderMinForAveOrderVolume": 1, "paraEmaAveOrderVolumeLag": None, "save": True},

                {"name": "factorEmaBidHugeOrderMultipleDuration", "className": "FactorEmaBidHugeOrderMultipleDuration",
                 "indexTradingUnderlying": [0], "indexFactorUnderlying": [],
                 "paraLag": 2, "paraNumOrderMax": 3, "paraNumOrderMin": 1, "paraNumOrderMaxForAveOrderVolume": 10,
                 "paraNumOrderMinForAveOrderVolume": 1, "paraEmaAveOrderVolumeLag": None,
                 "paraHorizon": 2, "save": True},

                {"name": "factorEmaAskHugeOrderMultipleDuration", "className": "FactorEmaAskHugeOrderMultipleDuration",
                 "indexTradingUnderlying": [0], "indexFactorUnderlying": [],
                 "paraLag": 2, "paraNumOrderMax": 3, "paraNumOrderMin": 1, "paraNumOrderMaxForAveOrderVolume": 10,
                 "paraNumOrderMinForAveOrderVolume": 1, "paraEmaAveOrderVolumeLag": None,
                 "paraHorizon": 2, "save": True},

                {"name": "factorEmaBidOrderBookMultiple1", "className": "FactorEmaBidOrderBookMultiple",
                 "indexTradingUnderlying": [0], "indexFactorUnderlying": [],
                 "paraLag": 2, "paraNumOrderMax": 3, "paraNumOrderMin": 1, "paraNumOrderMaxForAveOrderVolume": 10,
                 "paraNumOrderMinForAveOrderVolume": 1, "paraEmaAveOrderVolumeLag": None, "save": True},

                {"name": "factorEmaAskOrderBookMultiple1", "className": "FactorEmaAskOrderBookMultiple",
                 "indexTradingUnderlying": [0], "indexFactorUnderlying": [],
                 "paraLag": 2, "paraNumOrderMax": 3, "paraNumOrderMin": 1, "paraNumOrderMaxForAveOrderVolume": 10,
                 "paraNumOrderMinForAveOrderVolume": 1, "paraEmaAveOrderVolumeLag": None, "save": True},

                {"name": "factorEmaBidOrderBookMultiple2", "className": "FactorEmaBidOrderBookMultiple",
                 "indexTradingUnderlying": [0], "indexFactorUnderlying": [],
                 "paraLag": 2, "paraNumOrderMax": 7, "paraNumOrderMin": 4, "paraNumOrderMaxForAveOrderVolume": 10,
                 "paraNumOrderMinForAveOrderVolume": 1, "paraEmaAveOrderVolumeLag": None, "save": True},

                {"name": "factorEmaAskOrderBookMultiple2", "className": "FactorEmaAskOrderBookMultiple",
                 "indexTradingUnderlying": [0], "indexFactorUnderlying": [],
                 "paraLag": 2, "paraNumOrderMax": 7, "paraNumOrderMin": 4, "paraNumOrderMaxForAveOrderVolume": 10,
                 "paraNumOrderMinForAveOrderVolume": 1, "paraEmaAveOrderVolumeLag": None, "save": True},

                {"name": "factorEmaBidOrderBookMultiple3", "className": "FactorEmaBidOrderBookMultiple",
                 "indexTradingUnderlying": [0], "indexFactorUnderlying": [],
                 "paraLag": 2, "paraNumOrderMax": 10, "paraNumOrderMin": 8, "paraNumOrderMaxForAveOrderVolume": 10,
                 "paraNumOrderMinForAveOrderVolume": 1, "paraEmaAveOrderVolumeLag": None, "save": True},

                {"name": "factorEmaAskOrderBookMultiple3", "className": "FactorEmaAskOrderBookMultiple",
                 "indexTradingUnderlying": [0], "indexFactorUnderlying": [],
                 "paraLag": 2, "paraNumOrderMax": 10, "paraNumOrderMin": 8, "paraNumOrderMaxForAveOrderVolume": 10,
                 "paraNumOrderMinForAveOrderVolume": 1, "paraEmaAveOrderVolumeLag": None, "save": True},

                {"name": "factorLast1Change", "className": "FactorLastNChange", "indexTradingUnderlying": [0],
                 "indexFactorUnderlying": [], "paraLastN": 1, "paraFastLag": 10, "paraSlowLag": 20, "save": True},

                {"name": "factorLast2Change", "className": "FactorLastNChange", "indexTradingUnderlying": [0],
                 "indexFactorUnderlying": [], "paraLastN": 2, "paraFastLag": 10, "paraSlowLag": 20, "save": True},

                {"name": "factorLast3Change", "className": "FactorLastNChange", "indexTradingUnderlying": [0],
                 "indexFactorUnderlying": [], "paraLastN": 3, "paraFastLag": 10, "paraSlowLag": 20, "save": True},

                {"name": "factorLast1VolumeMagnification", "className": "FactorLastNVolumeMagnification",
                 "indexTradingUnderlying": [0], "indexFactorUnderlying": [], "paraLastN": 1, "paraFastLag": 10,
                 "paraSlowLag": 20, "save": True},

                {"name": "factorLast2VolumeMagnification", "className": "FactorLastNVolumeMagnification",
                 "indexTradingUnderlying": [0], "indexFactorUnderlying": [], "paraLastN": 2, "paraFastLag": 10,
                 "paraSlowLag": 20, "save": True},

                {"name": "factorLast3VolumeMagnification", "className": "FactorLastNVolumeMagnification",
                 "indexTradingUnderlying": [0], "indexFactorUnderlying": [], "paraLastN": 3, "paraFastLag": 10,
                 "paraSlowLag": 20, "save": True},

                {"name": "factorDistanceToAvePrice", "className": "FactorDistanceToAvePrice", "indexTradingUnderlying": [0],
                 "indexFactorUnderlying": [], "save": True},

                {"name": "factorSpeedMA", "className": "FactorSpeedMA", "indexTradingUnderlying": [0],
                 "indexFactorUnderlying": [],
                 "paraLag": 10.0, "paraMALag": 120, "save": True},

                {"name": "factorDistanceToMAPrice", "className": "FactorDistanceToMAPrice", "indexTradingUnderlying": [0],
                 "indexFactorUnderlying": [], "paraMALag": 120, "save": True},

                {"name": "factorMaAmount", "className": "FactorMaAmount", "indexTradingUnderlying": [0],
                 "indexFactorUnderlying": [], "paraLag": 150, "save": True}
            ],
        strategyinst.setParaFactor(factorSet)
        strategyinst.setParaTag(para["Tag"])
        strategyinst.setStartDateTime(para["StartDateTime"])
        strategyinst.setEndDateTime(para["EndDateTime"])
        strategyinst.setOutputDir(para["outputDir"])

        strategyManagement.registerStrategy(strategyinst)
        # %%
        # 载入数据
        strategyManagement.loadData()
        # %%
        # 运行策略
        strategyManagement.start()
        # %%
        # 将因子输出到Excel
        # Tools.exportExecl(strategyinst)
        # 把因子的数据结构存下来
        DumpLoad.dumpOutput(strategyinst)

        # 读取方法：
        # outputFactor, outputSubTag, tradingUnderlyingCode, factorName = DumpLoad.loadOutput(strategy1.getStrategyName())

        print("This line is for setting breakpoint")
