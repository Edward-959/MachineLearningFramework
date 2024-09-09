from System.Factor import Factor
import numpy as np


class TimeWindow(Factor):
    def __init__(self, para, factorManagement):
        Factor.__init__(self, para, factorManagement)
        # 因子参数：ticks in the window
        self.__paraWindowSpan = para['paraWindowSpan']
        factorManagement.registerFactor(self, para)
        self.__data = self.getTradingUnderlyingData(self.getIndexTradingUnderlying()[0])
        self.timeWindow = []

    def calculate(self):
        length = min(len(self.__data.getContent()), self.__paraWindowSpan)
        dataWindow = self.__data.getContent()[-length:]
        price = []
        volume = []
        amount = []
        time = []
        for i in range(0, length):
            price.append(dataWindow[i].lastPrice)
            volume.append(dataWindow[i].volume)
            amount.append(dataWindow[i].amount)
            time.append(dataWindow[i].time)

        self.timeWindow.append(
            {"open": price[0], "close": price[-1], "high": max(price), "low": min(price),
             "volume": sum(volume), "amount": sum(amount), "initialTime": time[0], "endTime": time[-1],
             "midPrice": (price[0] + price[-1]) / 2}
        )

        residual = np.arange(0, len(self.__data.getContent())) % self.__paraWindowSpan
        group = np.argwhere(residual == residual[-1])
        timeWindowSeries = {"open": [], "close": [], "high": [], "low": [], "volume": [], "amount": [],
                                 "initialTime": [], "endTime": [], "midPrice": []}
        for i in range(0, len(group)):
            timeWindowSeries["open"].append(self.timeWindow[group[i][0]]["open"])
            timeWindowSeries["close"].append(self.timeWindow[group[i][0]]["close"])
            timeWindowSeries["high"].append(self.timeWindow[group[i][0]]["high"])
            timeWindowSeries["low"].append(self.timeWindow[group[i][0]]["low"])
            timeWindowSeries["volume"].append(self.timeWindow[group[i][0]]["volume"])
            timeWindowSeries["amount"].append(self.timeWindow[group[i][0]]["amount"])
            timeWindowSeries["initialTime"].append(self.timeWindow[group[i][0]]["initialTime"])
            timeWindowSeries["endTime"].append(self.timeWindow[group[i][0]]["endTime"])
            timeWindowSeries["midPrice"].append(self.timeWindow[group[i][0]]["midPrice"])

        self.addData(timeWindowSeries, self.__data.getLastTimeStamp())
