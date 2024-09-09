{
    "outputDir": "output",
    "StrategyName": "AlgoShaolin",
    "TradingUnderlyingCode": [
                            ["601318.SH"]
                            ],
    "FactorUnderlyingCode": [],
    "StartDateTime": 20170615093000,
    "EndDateTime": 20170615145659,
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

            {"name": "factorEmaSlicePressure", "className": "FactorEmaSlicePressure", "indexTradingUnderlying": [0],
             "indexFactorUnderlying": [], "paraNumOrderMax": 5, "paraNumOrderMin": 1, "paraEmaSlicePressureLag": 1,
             "save": true},

            {"name": "factorAveAmplitude", "className": "FactorAveAmplitude", "indexTradingUnderlying": [0],
             "indexFactorUnderlying": [], "paraAmplitudeLag": 5, "paraFastLag": 10, "paraSlowLag": 20, "save": true},

            {"name": "factorOrderPressure", "className": "FactorOrderPressure", "indexTradingUnderlying": [0],
             "indexFactorUnderlying": [], "paraOrderPressureLag": 1, "save": true},

            {"name": "factorEmaOrderPressureBuy", "className": "FactorEmaOrderPressureBuy",
             "indexTradingUnderlying": [0],
             "indexFactorUnderlying": [], "paraOrderPressureLag": 1, "save": true},

            {"name": "factorEmaOrderPressureSell", "className": "FactorEmaOrderPressureSell",
             "indexTradingUnderlying": [0],
             "indexFactorUnderlying": [], "paraOrderPressureLag": 1, "save": true},

            {"name": "factorOrderPressureTransaction", "className": "FactorOrderPressureTransaction", "indexTradingUnderlying": [0],
             "indexFactorUnderlying": [], "paraOrderPressureTransactionLag": 1, "save": true},

            {"name": "factorEmaOrderPressureTransactionBuy", "className": "FactorEmaOrderPressureTransactionBuy",
             "indexTradingUnderlying": [0],
             "indexFactorUnderlying": [], "paraOrderPressureTransactionLag": 1, "save": true},

            {"name": "factorEmaOrderPressureTransactionSell", "className": "FactorEmaOrderPressureTransactionSell",
             "indexTradingUnderlying": [0],
             "indexFactorUnderlying": [], "paraOrderPressureTransactionLag": 1, "save": true},

            {"name": "factorEmaBidHugeOrderMultiple1", "className": "FactorEmaBidHugeOrderMultiple",
             "indexTradingUnderlying": [0], "indexFactorUnderlying": [],
             "paraLag": 1, "paraNumOrderMax": 3, "paraNumOrderMin": 1, "paraNumOrderMaxForAveOrderVolume": 10,
             "paraNumOrderMinForAveOrderVolume": 1, "paraEmaAveOrderVolumeLag": null, "save": true},

            {"name": "factorEmaAskHugeOrderMultiple1", "className": "FactorEmaAskHugeOrderMultiple",
             "indexTradingUnderlying": [0], "indexFactorUnderlying": [],
             "paraLag": 1, "paraNumOrderMax": 3, "paraNumOrderMin": 1, "paraNumOrderMaxForAveOrderVolume": 10,
             "paraNumOrderMinForAveOrderVolume": 1, "paraEmaAveOrderVolumeLag": null, "save": true},

            {"name": "factorEmaBidOrderBookMultiple1", "className": "FactorEmaBidOrderBookMultiple",
             "indexTradingUnderlying": [0], "indexFactorUnderlying": [],
             "paraLag": 1, "paraNumOrderMax": 3, "paraNumOrderMin": 1, "paraNumOrderMaxForAveOrderVolume": 10,
             "paraNumOrderMinForAveOrderVolume": 1, "paraEmaAveOrderVolumeLag": null, "save": true},

            {"name": "factorEmaAskOrderBookMultiple1", "className": "FactorEmaAskOrderBookMultiple",
             "indexTradingUnderlying": [0], "indexFactorUnderlying": [],
             "paraLag": 1, "paraNumOrderMax": 3, "paraNumOrderMin": 1, "paraNumOrderMaxForAveOrderVolume": 10,
             "paraNumOrderMinForAveOrderVolume": 1, "paraEmaAveOrderVolumeLag": null, "save": true},

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