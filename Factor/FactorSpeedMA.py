"""
@author: 011672

计算移动平均价的涨跌速
计算方式为当前移动平均价/过去某个切片的移动平均价，并进行分钟化
"""
from System.Factor import Factor


class FactorSpeedMA(Factor):  # 因子类
    def __init__(self, para, factorManagement):  # 传入因子参数,归属的因子管理模块，需要用到的其他因子或非因子
        Factor.__init__(self, para, factorManagement)
        # 因子参数
        self.__paraMALag = para['paraMALag']  # 计算移动平均的阶数
        self.__paraLag = para['paraLag']  # 计算速度的阶数
        paraMAPrice = {"name": "MAPrice", "className": "MA",
                       "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                       "indexFactorUnderlying": self.getIndexFactorUnderlying(),
                       "paraLag": self.__paraMALag,
                       "paraOriginalData": {"name": "midPrice", "className": "MidPrice",
                                            "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                            "indexFactorUnderlying": self.getIndexFactorUnderlying()}}
        self.__MAPrice = self.getFactorData(paraMAPrice)
        factorManagement.registerFactor(self, para)
        self.__data = self.getTradingUnderlyingData(self.getIndexTradingUnderlying()[0])

    def calculate(self):
        lastFactorSpeed = 0
        if len(self.__MAPrice.getContent()) > self.__paraLag:
            lastFactorSpeed = (self.__MAPrice.getLastContent() / self.__MAPrice.getContent()[
                int(-1 - self.__paraLag)] - 1) / (self.__paraLag / 20)
        self.addData(lastFactorSpeed, self.__data.getLastTimeStamp())
