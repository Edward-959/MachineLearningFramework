"""
@author: 011672011672
@revise: 006688

计算中间价序列的MACD值
并提供DIFF和DEA的取值接口
其中DEA为DIFF的移动平均，MACD = (DEA - DIFF) * 2
"""
from System.Factor import Factor


class FactorMACD(Factor):
    def __init__(self, para, factorManagement):
        Factor.__init__(self, para, factorManagement)

        self.__paraFastLag = para["paraFastLag"]
        self.__paraSlowLag = para["paraSlowLag"]
        self.__paraDiffLag = para["paraDiffLag"]  # 计算DEA的周期

        paraDIFF = {"name": "factorDIFF", "className": "FactorDIFF",
                    "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                    "indexFactorUnderlying": self.getIndexFactorUnderlying(),
                    "paraFastLag": self.__paraFastLag, "paraSlowLag": self.__paraSlowLag}
        self.__DIFF = self.getFactorData(paraDIFF)
        paraDEA = {"name": "emaDIFF", "className": "Ema",
                   "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                   "indexFactorUnderlying": self.getIndexFactorUnderlying(),
                   "paraLag": self.__paraDiffLag, "paraOriginalData": paraDIFF}
        self.__DEA = self.getFactorData(paraDEA)

        factorManagement.registerFactor(self, para)

    def calculate(self):
        MACD = (self.__DIFF.getLastContent() - self.__DEA.getLastContent()) * 2
        self.addData(MACD, self.__DIFF.getLastTimeStamp())

    def getDIFF(self):
        return self.__DIFF

    def getDEA(self):
        return self.__DEA
