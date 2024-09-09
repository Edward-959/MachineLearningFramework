"""
@author: 011672

计算指数在当前波段的涨跌幅
"""
from System.Factor import Factor


class FactorIndexPriceChangeRatio(Factor):
    def __init__(self, para, factorManagement):
        Factor.__init__(self, para, factorManagement)
        # 因子参数
        self.__paraFastLag = para['paraFastLag']
        self.__paraSlowLag = para['paraSlowLag']

        self.__data = self.getFactorUnderlyingData(self.getIndexFactorUnderlying()[0])
        self.__extremePoint = self.getFactorData({"name": "indexExtremePoint", "className": "IndexExtremePoint",
                                                  "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                                  "indexFactorUnderlying": self.getIndexFactorUnderlying(),
                                                  "paraFastLag": self.__paraFastLag, "paraSlowLag": self.__paraSlowLag})
        factorManagement.registerFactor(self, para)

    def calculate(self):
        factorValue = self.__extremePoint.getLastContent()[3]
        self.addData(factorValue, self.__data.getLastTimeStamp())
