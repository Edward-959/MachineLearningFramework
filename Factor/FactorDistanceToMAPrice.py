"""
@author: 011672

计算当前中间价相对于移动平均价的相对距离
计算方式为:(中间价-移动平均价)/移动平均价
"""

from System.Factor import Factor


class FactorDistanceToMAPrice(Factor):
    def __init__(self, para, factorManagement):
        Factor.__init__(self, para, factorManagement)
        self.__paraMALag = para["paraMALag"]

        self.__midPrice = self.getFactorData({"name": "midPrice", "className": "MidPrice",
                                              "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                              "indexFactorUnderlying": self.getIndexFactorUnderlying()})
        paraMAPrice = {"name": "MAPrice", "className": "MA",
                       "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                       "indexFactorUnderlying": self.getIndexFactorUnderlying(),
                       "paraLag": self.__paraMALag,
                       "paraOriginalData": {"name": "midPrice", "className": "MidPrice",
                                            "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                            "indexFactorUnderlying": self.getIndexFactorUnderlying()}}
        self.__MAPrice = self.getFactorData(paraMAPrice)

        factorManagement.registerFactor(self, para)

    def calculate(self):
        midPrice = self.__midPrice.getLastContent()
        maPrice = self.__MAPrice.getLastContent()
        self.addData(midPrice / maPrice - 1, self.__midPrice.getLastTimeStamp())
