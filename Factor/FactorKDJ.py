"""
@author: 011672
@revise: 006688

计算中间价序列的KDJ值，输出结果为J值，同时提供了取K值和D值的接口
N个切片的RSV=（Cn－Ln）/（Hn－Ln）×100
公式中，Cn为第n个切片价格；Ln为前n个切片内的最低价；Hn为前n个切片内的最高价。
其次，计算K值、D值与J值：
当日K值=2/3×前一K值+1/3×当前RSV
当日D值=2/3×前一D值+1/3×当前K值
当日J值=3*当日K值-2*当日D值
"""
from System.Factor import Factor


class FactorKDJ(Factor):
    def __init__(self, para, factorManagement):
        Factor.__init__(self, para, factorManagement)

        self.__paraKDJLag = para["paraKDJLag"]

        self.__midPrice = self.getFactorData({"name": "midPrice", "className": "MidPrice",
                                              "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                              "indexFactorUnderlying": self.getIndexFactorUnderlying()})

        self.__KValue = []
        self.__DValue = []
        factorManagement.registerFactor(self, para)

    def calculate(self):
        midPrice = self.__midPrice.getContent()
        lastMidPrice = self.__midPrice.getLastContent()
        # 计算区间最高价和最低价
        if len(midPrice) <= self.__paraKDJLag:
            priceList = midPrice
        else:
            priceList = midPrice[-self.__paraKDJLag:]
        H = max(priceList)
        L = min(priceList)
        # 计算RSV、K、D、J值
        if len(midPrice) == 1:  # 第一个切片以50代替
            K = 50
            D = 50
        else:
            lastK = self.__KValue[-1]
            lastD = self.__DValue[-1]
            if H == L:
                RSV = 50  # 如果期间价格保持不变，RSV值以50代替
            else:
                RSV = (lastMidPrice - L) / (H - L) * 100
            K = 2 * lastK / 3 + RSV / 3
            D = 2 * lastD / 3 + RSV / 3
        J = 3 * K - 2 * D
        self.__KValue.append(K)
        self.__DValue.append(D)
        self.addData(J, self.__midPrice.getLastTimeStamp())

    def getKValue(self):
        return self.__KValue

    def getDValue(self):
        return self.__DValue
