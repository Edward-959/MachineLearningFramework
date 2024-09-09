{
  "outputDir": "output",
  "StrategyName":"AlgoShaolin",
  "TradingUnderlyingCode":[["601318.SH"]],
  "FactorUnderlyingCode":[],
  "StartDateTime":20180704093015,
  "EndDateTime":20180705145659,
  "FactorSet":
    [
        {"name": "factorDistanceToAvePrice", "className": "FactorDistanceToAvePrice", "indexTradingUnderlying": [0],
         "indexFactorUnderlying": [], "save": true},

        {"name": "factorAskHugeOrderMultiple", "className": "FactorAskHugeOrderMultiple",
         "indexTradingUnderlying": [0], "indexFactorUnderlying": [],
         "paraNumOrderMax": 2, "paraNumOrderMin": 1, "paraNumOrderMaxForAveOrderVolume": 10,
         "paraNumOrderMinForAveOrderVolume": 1, "paraEmaAveOrderVolumeLag": null, "save": true},

        {"name": "factorSpeed", "className": "FactorSpeed", "indexTradingUnderlying": [0], "indexFactorUnderlying": [],
         "paraLag": 5.0, "paraEmaMidPriceLag": 10, "save": true},

        {"name": "factorBidHugeOrderMultiple", "className": "FactorBidHugeOrderMultiple",
         "indexTradingUnderlying": [0], "indexFactorUnderlying": [],
         "paraNumOrderMax": 2, "paraNumOrderMin": 1, "paraNumOrderMaxForAveOrderVolume": 10,
         "paraNumOrderMinForAveOrderVolume": 1, "paraEmaAveOrderVolumeLag": null, "save": true},

        {"name": "factorDistanceBetweenVWAPPrice20", "className": "FactorDistanceBetweenVWAPPrice",
         "indexTradingUnderlying": [0],
         "indexFactorUnderlying": [], "paraFastLag": 3, "paraSlowLag": 20, "save": true},

        {"name": "factorDistanceBetweenVWAPPrice40", "className": "FactorDistanceBetweenVWAPPrice",
         "indexTradingUnderlying": [0],
         "indexFactorUnderlying": [], "paraFastLag": 3, "paraSlowLag": 40, "save": true},

        {"name": "factorDistanceBetweenVWAPPrice100", "className": "FactorDistanceBetweenVWAPPrice",
         "indexTradingUnderlying": [0],
         "indexFactorUnderlying": [], "paraFastLag": 3, "paraSlowLag": 100, "save": true},

        {"name": "factorDistanceBetweenVWAPPrice200", "className": "FactorDistanceBetweenVWAPPrice",
         "indexTradingUnderlying": [0],
         "indexFactorUnderlying": [], "paraFastLag": 3, "paraSlowLag": 200, "save": true},

        {"name": "factorCrossPriceChangeRatio", "className": "FactorCrossPriceChangeRatio",
         "indexTradingUnderlying": [0], "indexFactorUnderlying": [], "paraFastLag": 30, "paraSlowLag": 60,
         "save": true},

        {"name": "factorCrossPriceChangeSpeed", "className": "FactorCrossPriceChangeSpeed",
         "indexTradingUnderlying": [0], "indexFactorUnderlying": [], "paraFastLag": 30, "paraSlowLag": 60,
         "save": true},

        {"name": "factorCrossPriceAveAmplitude", "className": "FactorCrossPriceAveAmplitude",
         "indexTradingUnderlying": [0], "indexFactorUnderlying": [], "paraFastLag": 30, "paraSlowLag": 60,
         "save": true},

        {"name": "factorMAVolumeDistance3", "className": "FactorMAVolumeDistance", "indexTradingUnderlying": [0],
         "indexFactorUnderlying": [], "paraMAFastLag": 3, "paraMASlowLag": 4730, "save": true},

        {"name": "factorMAVolumeDistance20", "className": "FactorMAVolumeDistance", "indexTradingUnderlying": [0],
         "indexFactorUnderlying": [], "paraMAFastLag": 20, "paraMASlowLag": 4730, "save": true},

        {"name": "factorMAVolumeDistance40", "className": "FactorMAVolumeDistance", "indexTradingUnderlying": [0],
         "indexFactorUnderlying": [], "paraMAFastLag": 40, "paraMASlowLag": 4730, "save": true},

        {"name": "factorMAVolumeDistance100", "className": "FactorMAVolumeDistance", "indexTradingUnderlying": [0],
         "indexFactorUnderlying": [], "paraMAFastLag": 100, "paraMASlowLag": 4730, "save": true},

        {"name": "factorMAVolumeDistance200", "className": "FactorMAVolumeDistance", "indexTradingUnderlying": [0],
         "indexFactorUnderlying": [], "paraMAFastLag": 200, "paraMASlowLag": 4730, "save": true},

        {"name": "factorEmaSlicePressure", "className": "FactorEmaSlicePressure", "indexTradingUnderlying": [0],
         "indexFactorUnderlying": [], "paraNumOrderMax": 10, "paraNumOrderMin": 1, "paraEmaSlicePressureLag": 10,
         "save": true},

        {"name": "factorOrderPressure", "className": "FactorOrderPressure", "indexTradingUnderlying": [0],
         "indexFactorUnderlying": [], "paraOrderPressureLag": 15, "save": true},

        {"name": "factorVolumeMagnification", "className": "FactorVolumeMagnification", "indexTradingUnderlying": [0],
         "indexFactorUnderlying": [], "paraFastLag": 10, "paraSlowLag": null, "save": true},

        {"name": "factorAccumBuyPower", "className": "FactorAccumBuyPower", "indexTradingUnderlying": [0],
         "indexFactorUnderlying": [], "paraMAVolumeLag": 4730, "save": true},

        {"name": "factorAccumSellPower", "className": "FactorAccumSellPower", "indexTradingUnderlying": [0],
         "indexFactorUnderlying": [], "paraMAVolumeLag": 4730, "save": true},

        {"name": "factorTransPressure", "className": "FactorTransPressure", "indexTradingUnderlying": [0],
         "indexFactorUnderlying": [], "paraMALag": 40, "paraDecayNum": 15, "save": true},

        {"name": "factorTransPressureVol", "className": "FactorTransPressureVol", "indexTradingUnderlying": [0],
         "indexFactorUnderlying": [], "paraMALag": 40, "paraDecayNum": 15, "save": true},

        {"name": "factorTransAskPressureVol", "className": "FactorTransAskPressureVol", "indexTradingUnderlying": [0],
         "indexFactorUnderlying": [], "paraMALag": 40, "paraDecayNum": 15, "save": true},

        {"name": "factorTransBidPressureVol", "className": "FactorTransBidPressureVol", "indexTradingUnderlying": [0],
         "indexFactorUnderlying": [], "paraMALag": 40, "paraDecayNum": 15, "save": true},

        {"name": "factorTransAskPressure", "className": "FactorTransAskPressure", "indexTradingUnderlying": [0],
         "indexFactorUnderlying": [], "paraMALag": 40, "paraDecayNum": 15, "save": true},

        {"name": "factorTransBidPressure", "className": "FactorTransBidPressure", "indexTradingUnderlying": [0],
         "indexFactorUnderlying": [], "paraMALag": 40, "paraDecayNum": 15, "save": true}
    ],
"Tag":
    {"indexTradingUnderlying": [0], "indexFactorUnderlying": [], "paraMaxDropHorizon": 0.002,
                          "paraEmaMidPriceLag": 4, "paraOrderPressureLag": 4, "paraNumOrderMax": 5, "paraNumOrderMin": 1,
                          "paraEmaSlicePressureLag": 8, "paraMaxLose": 0.004, "paraFastLag": 10, "paraSlowLag": 20}

}
