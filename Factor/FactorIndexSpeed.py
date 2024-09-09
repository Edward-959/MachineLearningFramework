"""
@author: 011672

计算指数的涨跌速
"""
from System.Factor import Factor


class FactorIndexSpeed(Factor):
    def __init__(self, para, factorManagement):
        Factor.__init__(self, para, factorManagement)
        # 因子参数
        self.__paraEmaIndexPriceLag = para['paraEmaIndexPriceLag']
        self.__paraIndexSpeedLag = para['paraIndexSpeedLag']

        paraEmaIndexPrice = {"name": "emaMidPrice", "className": "Ema",
                             "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                             "indexFactorUnderlying": self.getIndexFactorUnderlying(),
                             "paraLag": self.__paraEmaIndexPriceLag,
                             "paraOriginalData": {"name": "indexPrice", "className": "IndexPrice",
                                                  "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                                  "indexFactorUnderlying": self.getIndexFactorUnderlying()}}
        self.__emaIndexPrice = self.getFactorData(paraEmaIndexPrice)
        factorManagement.registerFactor(self, para)
        self.__data = self.getFactorUnderlyingData(self.getIndexFactorUnderlying()[0])

    def calculate(self):
        lastIndexSpeed = 0
        if len(self.__emaIndexPrice.getContent()) > self.__paraIndexSpeedLag:
            lastIndexSpeed = (self.__emaIndexPrice.getLastContent() / self.__emaIndexPrice.getContent()[
                int(-1 - self.__paraIndexSpeedLag)] - 1) / (self.__paraIndexSpeedLag / 60)
        self.addData(lastIndexSpeed, self.__data.getLastTimeStamp())
