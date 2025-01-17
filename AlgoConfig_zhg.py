{
  "StrategyName":"AlgoShaolin",   
  "TradingUnderlyingCode":[ ["000002.SZ"], 
                            ["000028.SZ"], 
                            ["000063.SZ"], 
                            ["000333.SZ"], 
                            ["000400.SZ"], 
                            ["000530.SZ"], 
                            ["000568.SZ"], 
                            ["000571.SZ"], 
                            ["000581.SZ"], 
                            ["000651.SZ"], 
                            ["000786.SZ"], 
                            ["000826.SZ"], 
                            ["000858.SZ"], 
                            ["000895.SZ"], 
                            ["000910.SZ"], 
                            ["000977.SZ"], 
                            ["001979.SZ"], 
                            ["002008.SZ"], 
                            ["002033.SZ"], 
                            ["002043.SZ"], 
                            ["002128.SZ"], 
                            ["002179.SZ"], 
                            ["002185.SZ"], 
                            ["002236.SZ"], 
                            ["002241.SZ"], 
                            ["002267.SZ"], 
                            ["002294.SZ"], 
                            ["002299.SZ"], 
                            ["002304.SZ"], 
                            ["002311.SZ"], 
                            ["002384.SZ"], 
                            ["002396.SZ"], 
                            ["002456.SZ"], 
                            ["002466.SZ"], 
                            ["002475.SZ"], 
                            ["002508.SZ"], 
                            ["002572.SZ"], 
                            ["002589.SZ"], 
                            ["002594.SZ"], 
                            ["002624.SZ"], 
                            ["002672.SZ"], 
                            ["300015.SZ"], 
                            ["300070.SZ"], 
                            ["300115.SZ"], 
                            ["300197.SZ"], 
                            ["300323.SZ"], 
                            ["300408.SZ"], 
                            ["300418.SZ"], 
                            ["300477.SZ"], 
                            ["600004.SH"], 
                            ["600009.SH"], 
                            ["600029.SH"], 
                            ["600036.SH"], 
                            ["600057.SH"], 
                            ["600110.SH"], 
                            ["600201.SH"], 
                            ["600219.SH"], 
                            ["600236.SH"], 
                            ["600276.SH"], 
                            ["600418.SH"], 
                            ["600498.SH"], 
                            ["600521.SH"], 
                            ["600570.SH"], 
                            ["600589.SH"], 
                            ["600703.SH"], 
                            ["600782.SH"], 
                            ["600805.SH"], 
                            ["600867.SH"], 
                            ["601012.SH"], 
                            ["601021.SH"], 
                            ["601088.SH"], 
                            ["601288.SH"], 
                            ["601318.SH"], 
                            ["601398.SH"], 
                            ["601601.SH"], 
                            ["601939.SH"], 
                            ["601988.SH"], 
                            ["603108.SH"], 
                            ["002056.SZ"], 
                            ["600516.SH"]
                            ],
  "FactorUnderlyingCode":[],
  "StartDateTime":20170430093000,
  "EndDateTime":20180430145659,
  "FactorSet":
    [
        {"name": "factorBuyPower", "className": "FactorBuyPower",
         "indexTradingUnderlying": [0], "indexFactorUnderlying": [],
         "paraNumOrderMax": 2, "paraNumOrderMin": 1,
         "paraLag": 3, "save": true},
        {"name": "factorMomentum_1", "className": "FactorMomentum",
         "indexTradingUnderlying": [0], "indexFactorUnderlying": [],
         "paraLag": 3, "paraEmaMidPriceLag": 5, "save": true},
        
        {"name": "factorMomentum_2", "className": "FactorMomentum",
         "indexTradingUnderlying": [0], "indexFactorUnderlying": [],
         "paraLag": 10, "paraEmaMidPriceLag": 5, "save": true},

        {"name": "factorSpeed_1", "className": "FactorSpeed",
         "indexTradingUnderlying": [0], "indexFactorUnderlying": [],
         "paraLag": 3, "paraEmaMidPriceLag": 5, "save": true},
        
        {"name": "factorSpeed_2", "className": "FactorSpeed",
         "indexTradingUnderlying": [0], "indexFactorUnderlying": [],
         "paraLag": 5, "paraEmaMidPriceLag": 5, "save": true},

        {"name": "factorSpeed_3", "className": "FactorSpeed",
         "indexTradingUnderlying": [0], "indexFactorUnderlying": [],
         "paraLag": 3, "paraEmaMidPriceLag": 10, "save": true},

        {"name": "factorVolumeMagnification_1", "className": "FactorVolumeMagnification", "indexTradingUnderlying": [0],
         "indexFactorUnderlying": [], "paraFastLag": 5, "paraSlowLag": 15, "save": true},
        {"name": "factorVolumeMagnification_2", "className": "FactorVolumeMagnification", "indexTradingUnderlying": [0],
         "indexFactorUnderlying": [], "paraFastLag": 10, "paraSlowLag": 30, "save": true},

        {"name": "factorDistanceToMAPrice_1", "className": "FactorDistanceToMAPrice", "indexTradingUnderlying": [0],
         "indexFactorUnderlying": [], "paraMALag": 60, "save": true},
        {"name": "factorDistanceToMAPrice_2", "className": "FactorDistanceToMAPrice", "indexTradingUnderlying": [0],
         "indexFactorUnderlying": [], "paraMALag": 100, "save": true},
        {"name": "factorDistanceToMAPrice_3", "className": "FactorDistanceToMAPrice", "indexTradingUnderlying": [0],
         "indexFactorUnderlying": [], "paraMALag": 20, "save": true},

        {"name": "factorKDJ", "className": "FactorKDJ", "indexTradingUnderlying": [0],
         "indexFactorUnderlying": [], "paraKDJLag": 9, "save": true},


        {"name": "factorEmaSlicePressure_1", "className": "FactorEmaSlicePressure", "indexTradingUnderlying": [0],
         "indexFactorUnderlying": [], "paraNumOrderMax": 5, "paraNumOrderMin": 1, "paraEmaSlicePressureLag": 3,
         "save": true},

        {"name": "factorEmaSlicePressure_2", "className": "FactorEmaSlicePressure", "indexTradingUnderlying": [0],
         "indexFactorUnderlying": [], "paraNumOrderMax": 5, "paraNumOrderMin": 1, "paraEmaSlicePressureLag": 10,
         "save": true},

        {"name": "factorEmaActiveOrder", "className": "FactorEmaActiveOrder", "indexTradingUnderlying": [0],
         "indexFactorUnderlying": [],  "paraEmaActiveOrderLag": 3,
         "save": true},


        {"name": "factorDistanceToHigh", "className": "FactorDistanceToHigh", "indexTradingUnderlying": [0],
         "indexFactorUnderlying": [], "paraLag": 20, "save": true},

        {"name": "factorDistanceToLow", "className": "FactorDistanceToLow", "indexTradingUnderlying": [0],
         "indexFactorUnderlying": [], "paraLag": 20, "save": true},

        {"name": "factorDistanceToVwap", "className": "FactorDistanceToVwap", "indexTradingUnderlying": [0],
         "indexFactorUnderlying": [], "paraLag": 20, "save": true},

       
        {"name": "factorEntrustRatio_1", "className": "FactorEntrustRatio", "indexTradingUnderlying": [0],
         "indexFactorUnderlying": [], "paraLag": 5, "save": true},
        {"name": "factorEntrustRatio_2", "className": "FactorEntrustRatio", "indexTradingUnderlying": [0],
         "indexFactorUnderlying": [], "paraLag": 10, "save": true},

        {"name": "factorRiseCoordination_1", "className": "FactorRiseCoordination", "indexTradingUnderlying": [0],
         "indexFactorUnderlying": [], "paraLag": 5, "save": true},
        {"name": "factorRiseCoordination_2", "className": "FactorRiseCoordination", "indexTradingUnderlying": [0],
         "indexFactorUnderlying": [], "paraLag": 10, "save": true},
        {"name": "factorRiseCoordination_3", "className": "FactorRiseCoordination", "indexTradingUnderlying": [0],
         "indexFactorUnderlying": [], "paraLag": 15, "save": true},

        {"name": "factorDistanceToPreClose", "className": "FactorDistanceToPreClose", "indexTradingUnderlying": [0],
         "indexFactorUnderlying": [], "save": true},
        
        {"name": "factorRiseCorMulRoc", "className": "FactorRiseCorMulRoc", "indexTradingUnderlying": [0],
         "indexFactorUnderlying": [], "paraLag": 10, "save": true},
        {"name": "factorEntrustRatioMulRoc", "className": "FactorEntrustRatioMulRoc", "indexTradingUnderlying": [0],
         "indexFactorUnderlying": [], "paraLag": 10, "save": true}
            
                
                           
        ],
  "Tag":
    {"indexTradingUnderlying": [0], "indexFactorUnderlying": [], "paraMaxDropHorizon": 0.002,
                          "paraEmaMidPriceLag": 4, "paraOrderPressureLag": 4, "paraNumOrderMax": 5, "paraNumOrderMin": 1,
                          "paraEmaSlicePressureLag": 8, "paraMaxLose": 0.004, "paraFastLag": 10, "paraSlowLag": 20}
}