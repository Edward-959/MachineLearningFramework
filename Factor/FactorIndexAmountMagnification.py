"""
@author: 011672

计算指数放量倍数
"""
from System.Factor import Factor


class FactorIndexAmountMagnification(Factor):
    def __init__(self, para, factorManagement):
        Factor.__init__(self, para, factorManagement)
        self.__paraFastLag = para['paraFastLag']
        self.__paraSlowLag = para['paraSlowLag']

        self.__data = self.getFactorUnderlyingData(self.getIndexFactorUnderlying()[0])
        paraEmaAmount = {"name": "emaAmount", "className": "Ema",
                         "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                         "indexFactorUnderlying": self.getIndexFactorUnderlying(),
                         "paraLag": self.__paraFastLag,
                         "paraOriginalData": {"name": "indexAmount", "className": "IndexAmount",
                                              "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                              "indexFactorUnderlying": self.getIndexFactorUnderlying()}}
        self.__emaAmountFast = self.getFactorData(paraEmaAmount)
        paraEmaAmount = {"name": "emaAmount", "className": "Ema",
                         "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                         "indexFactorUnderlying": self.getIndexFactorUnderlying(),
                         "paraLag": self.__paraSlowLag,
                         "paraOriginalData": {"name": "indexAmount", "className": "IndexAmount",
                                              "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                              "indexFactorUnderlying": self.getIndexFactorUnderlying()}}
        self.__emaAmountSlow = self.getFactorData(paraEmaAmount)
        factorManagement.registerFactor(self, para)

    def calculate(self):
        if self.__emaAmountSlow.getLastContent() != 0:
            factorValue = self.__emaAmountFast.getLastContent() / self.__emaAmountSlow.getLastContent()
        else:
            factorValue = 0.
        self.addData(factorValue, self.__data.getLastTimeStamp())
