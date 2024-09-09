"""
@author: 011672

当前波段序号记为0，依据界点，往前的波段依次计为第1、2、...波，指定波段的序号，给出对应波段的放量倍数
放量倍数定义为该波段秒均成交量/开盘到该波段结束时的秒均成交量
波段序号参数为单个数值
"""

from System.Factor import Factor


class FactorLastNVolumeMagnification(Factor):
    def __init__(self, para, factorManagement):
        Factor.__init__(self, para, factorManagement)
        self.__paraLastN = para['paraLastN']
        self.__paraFastLag = para['paraFastLag']
        self.__paraSlowLag = para['paraSlowLag']

        self.__LastNVolMag = self.getFactorData({"name": "lastNVolMag", "className": "LastNVolumeMagnification",
                                                 "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                                 "indexFactorUnderlying": self.getIndexFactorUnderlying(),
                                                 "paraLastN": [self.__paraLastN],
                                                 "paraFastLag": self.__paraFastLag, "paraSlowLag": self.__paraSlowLag})
        factorManagement.registerFactor(self, para)

    def calculate(self):
        factorValue = self.__LastNVolMag.getLastContent()[0]
        self.addData(factorValue, self.__LastNVolMag.getLastTimeStamp())
