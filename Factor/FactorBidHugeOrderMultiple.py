# -*- coding: utf-8 -*-
"""
Created on 2018/7/12 18:06

@author: 011672
"""
from System.Factor import Factor


class FactorBidHugeOrderMultiple(Factor):  # 盘口numOrder档新增单相对于平均挂单量的倍数
    def __init__(self, para, factorManagement):  # 传入因子参数,归属的因子管理模块，需要用到的其他因子或非因子
        Factor.__init__(self, para, factorManagement)
        # 因子参数
        self.__paraNumOrderMax = para['paraNumOrderMax']
        self.__paraNumOrderMin = para['paraNumOrderMin']
        self.__paraNumOrderMaxForAveOrderVolume = para["paraNumOrderMaxForAveOrderVolume"]
        self.__paraNumOrderMinForAveOrderVolume = para["paraNumOrderMinForAveOrderVolume"]
        self.__paraEmaAveOrderVolumeLag = para['paraEmaAveOrderVolumeLag']

        # 因子计算会用到的中间变量,取数据时候要注意会不会出现取出的因子还没有计算出值
        # 如果需要实例化因子作为中间变量，则name不要以factor开头，否则会输出到最终的结果中
        # 如果需要实例化因子或者非因子，需要考虑注册因子的先后顺序，即factorManagement.registerFactor(self)
        self.__data = self.getTradingUnderlyingData(self.getIndexTradingUnderlying()[0])
        paraHugeOrderMultiple = {"name": "hugeOrderMultiple", "className": "HugeOrderMultiple",
                                     "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                     "indexFactorUnderlying": self.getIndexFactorUnderlying(),
                                     "paraNumOrderMax": self.__paraNumOrderMax,
                                     "paraNumOrderMin": self.__paraNumOrderMin,
                                     "paraNumOrderMaxForAveOrderVolume":
                                         self.__paraNumOrderMaxForAveOrderVolume,
                                     "paraNumOrderMinForAveOrderVolume":
                                         self.__paraNumOrderMinForAveOrderVolume,
                                     "paraEmaAveOrderVolumeLag": self.__paraEmaAveOrderVolumeLag}
        self.__HugeOrderMultiple = self.getFactorData(paraHugeOrderMultiple)
        factorManagement.registerFactor(self, para)

    def calculate(self):
        factorValue = self.__HugeOrderMultiple.getLastContent()[0]
        self.addData(factorValue, self.__data.getLastTimeStamp())
