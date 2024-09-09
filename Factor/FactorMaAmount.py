"""
@author: 011672

成交额的MA均值，返回成交量，去掉前Lag个Tick的值
"""

from System.Factor import Factor


class FactorMaAmount(Factor):
    def __init__(self, para, factorManagement):
        Factor.__init__(self, para, factorManagement)
        self.__paraLag = para['paraLag']
        self.__data = self.getTradingUnderlyingData(self.getIndexTradingUnderlying()[0])

        self.__AFTERNOON_START_LOCAL = 130015000
        self.__AFTERNOON_START_GLOBAL = 130000000

        self.__preTurnover = 0  # amount是两个turnover的差，所以要记录上一个的turnover
        self.__maAmount = 0  # 上一个tick的maAmount
        self.__accAmount = 0  # 累计的maAmount
        self.__validAmountCounts = 0  # 次数，用作除数
        self.__invalidTicks = 0  # 刚开盘的成交量不考虑
        self.__isValid = False  # 是否开始计算MA

        factorManagement.registerFactor(self, para)

    def calculate(self):
        curr_data = self.__data.getLastContent()
        if self.__isValid:
            if self.isValidTime(curr_data):
                count = self.__validAmountCounts
                count += 1
                amount = curr_data.totalAmount - self.__preTurnover
                accAmountValue = self.__accAmount + amount
                value = accAmountValue / count

                self.__accAmount = accAmountValue
                self.__validAmountCounts = count
                self.__maAmount = value
        else:
            self.__invalidTicks += 1
            if self.__invalidTicks + 1 == self.__paraLag:  # 确保第Lag个tick时，进行了MA计算
                self.__isValid = True

        self.__preTurnover = curr_data.totalAmount
        self.addData(self.__maAmount, self.__data.getLastTimeStamp())

    def isValidTime(self, curr_data):
        time = curr_data.time
        return time <= self.__AFTERNOON_START_GLOBAL or time >= self.__AFTERNOON_START_LOCAL



