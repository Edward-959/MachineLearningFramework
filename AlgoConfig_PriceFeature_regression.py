{
    "outputDir": "output",
    "StrategyName": "AlgoShaolin",
    "TradingUnderlyingCode": [
                            ["601318.SH"]
                            ],
    "FactorUnderlyingCode": [],
    "StartDateTime": 20180615093000,
    "EndDateTime": 20180615145659,
    "FactorSet":
        [
            {"name": "factorVolumeMagnification", "className": "FactorVolumeMagnification",
             "indexTradingUnderlying": [0],
             "indexFactorUnderlying": [], "paraFastLag": 10, "paraSlowLag": null, "save": true},

            {"name": "factorPriceChangeRatio", "className": "FactorPriceChangeRatio",
             "indexTradingUnderlying": [0], "indexFactorUnderlying": [], "paraFastLag": 10, "paraSlowLag": 20,
             "save": true},

            {"name": "factorPriceChangeSpeed", "className": "FactorPriceChangeSpeed",
             "indexTradingUnderlying": [0], "indexFactorUnderlying": [], "paraFastLag": 10, "paraSlowLag": 20,
             "save": true},

            {"name": "factorSpeed", "className": "FactorSpeed", "indexTradingUnderlying": [0],
             "indexFactorUnderlying": [],
             "paraLag": 10.0, "paraEmaMidPriceLag": 4, "save": true},

            {"name": "factorLREmaSlicePressure", "className": "FactorLREmaSlicePressure", "indexTradingUnderlying": [0],
             "indexFactorUnderlying": [], "paraNumOrderMax": 5, "paraNumOrderMin": 1, "paraEmaSlicePressureLag": 1, "returnLag": 5, "factorLag": 20, "factorNum": 3,
             "save": true},

            {"name": "factorAveAmplitude", "className": "FactorAveAmplitude", "indexTradingUnderlying": [0],
             "indexFactorUnderlying": [], "paraAmplitudeLag": 5, "paraFastLag": 10, "paraSlowLag": 20, "save": true},

            {"name": "factorLROrderPressure", "className": "FactorLROrderPressure", "indexTradingUnderlying": [0],
             "indexFactorUnderlying": [], "paraOrderPressureLag": 1, "returnLag": 5, "factorLag": 20, "factorNum": 3, "save": true},

            {"name": "factorLREmaOrderPressureBuy", "className": "FactorLREmaOrderPressureBuy",
             "indexTradingUnderlying": [0],
             "indexFactorUnderlying": [], "paraOrderPressureLag": 1, "returnLag": 5, "factorLag": 20, "factorNum": 3, "save": true},

            {"name": "factorLREmaOrderPressureSell", "className": "FactorLREmaOrderPressureSell",
             "indexTradingUnderlying": [0],
             "indexFactorUnderlying": [], "paraOrderPressureLag": 1, "returnLag": 5, "factorLag": 20, "factorNum": 3, "save": true},

            {"name": "factorLREmaBidHugeOrderMultiple1", "className": "FactorLREmaBidHugeOrderMultiple",
             "indexTradingUnderlying": [0], "indexFactorUnderlying": [],
             "paraLag": 1, "paraNumOrderMax": 3, "paraNumOrderMin": 1, "paraNumOrderMaxForAveOrderVolume": 10,
             "paraNumOrderMinForAveOrderVolume": 1, "paraEmaAveOrderVolumeLag": null, "returnLag": 5, "factorLag": 20, "factorNum": 3, "save": true},

            {"name": "factorLREmaAskHugeOrderMultiple1", "className": "FactorLREmaAskHugeOrderMultiple",
             "indexTradingUnderlying": [0], "indexFactorUnderlying": [],
             "paraLag": 1, "paraNumOrderMax": 3, "paraNumOrderMin": 1, "paraNumOrderMaxForAveOrderVolume": 10,
             "paraNumOrderMinForAveOrderVolume": 1, "paraEmaAveOrderVolumeLag": null, "returnLag": 5, "factorLag": 20, "factorNum": 3, "save": true},

            {"name": "factorLREmaBidOrderBookMultiple1", "className": "FactorLREmaBidOrderBookMultiple",
             "indexTradingUnderlying": [0], "indexFactorUnderlying": [],
             "paraLag": 1, "paraNumOrderMax": 3, "paraNumOrderMin": 1, "paraNumOrderMaxForAveOrderVolume": 10,
             "paraNumOrderMinForAveOrderVolume": 1, "paraEmaAveOrderVolumeLag": null, "returnLag": 5, "factorLag": 20, "factorNum": 3, "save": true},

            {"name": "factorLREmaAskOrderBookMultiple1", "className": "FactorLREmaAskOrderBookMultiple",
             "indexTradingUnderlying": [0], "indexFactorUnderlying": [],
             "paraLag": 1, "paraNumOrderMax": 3, "paraNumOrderMin": 1, "paraNumOrderMaxForAveOrderVolume": 10,
             "paraNumOrderMinForAveOrderVolume": 1, "paraEmaAveOrderVolumeLag": null, "returnLag": 5, "factorLag": 20, "factorNum": 3, "save": true},

            {"name": "factorDistanceToAvePrice", "className": "FactorDistanceToAvePrice", "indexTradingUnderlying": [0],
             "indexFactorUnderlying": [], "save": true},

            {"name": "factorDistanceToMAPrice", "className": "FactorDistanceToMAPrice", "indexTradingUnderlying": [0],
             "indexFactorUnderlying": [], "paraMALag": 120, "save": true},

            {"name": "factorDistanceToMAPrice", "className": "FactorDistanceToMAPrice", "indexTradingUnderlying": [0],
             "indexFactorUnderlying": [], "paraMALag": 60, "save": true},

            {"name": "factorMomentum", "className": "FactorMomentum",
             "indexTradingUnderlying": [0], "indexFactorUnderlying": [],
             "paraLag": 3, "paraEmaMidPriceLag": 5, "save": true},

            {"name": "factorMomentum", "className": "FactorMomentum",
             "indexTradingUnderlying": [0], "indexFactorUnderlying": [],
             "paraLag": 10, "paraEmaMidPriceLag": 5, "save": true},

            {"name": "factorEmaActiveOrder", "className": "FactorEmaActiveOrder", "indexTradingUnderlying": [0],
             "indexFactorUnderlying": [], "paraEmaActiveOrderLag": 3,
             "save": true},

            {"name": "factorDistanceToVwap", "className": "FactorDistanceToVwap", "indexTradingUnderlying": [0],
             "indexFactorUnderlying": [], "paraLag": 20, "save": true},

            {"name": "factorMaAmount", "className": "FactorMaAmount", "indexTradingUnderlying": [0],
             "indexFactorUnderlying": [], "paraLag": 2, "save": true}
        ],
    "Tag":
        {"indexTradingUnderlying": [0], "indexFactorUnderlying": [], "paraMaxDropHorizon": 0.002,
         "paraEmaMidPriceLag": 4, "paraOrderPressureLag": 4, "paraNumOrderMax": 5, "paraNumOrderMin": 1,
         "paraEmaSlicePressureLag": 8, "paraMaxLose": 0.004, "paraFastLag": 10, "paraSlowLag": 20}
}