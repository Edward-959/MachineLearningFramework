# -*- coding: utf-8 -*-
"""
Created on Thu Aug 10 19:48:51 2017

@author: 池彬汉 & 郑润泽
"""
import datetime as dt
import System.ReadDataFile

from System.SliceData import SliceData


class DataBroadcast:
    def __init__(self):
        self.__tradingUnderlyingCode = []
        self.__factorUnderlyingCode = []
        self.__startDateTime = None
        self.__endDateTime = None
        self.__tradingDays = None
        self.__dictData = None
        self.__prepareData = None
        self.__lenForLoop = None
        self.__iterList = []
        self.__indexForPrepare = []

    def getTradingUnderlyingCode(self):
        return self.__tradingUnderlyingCode

    def getFactorUnderlyingCode(self):
        return self.__factorUnderlyingCode

    def getStartDateTime(self):
        return self.__startDateTime

    def getEndDateTime(self):
        return self.__endDateTime

    def getTradingDays(self):
        return self.__tradingDays

    def getDictData(self):
        return self.__dictData

    def getLenForLoop(self):
        return self.__lenForLoop

    def setTradingUnderlyingCode(self, tradingUnderlyingCode):
        self.__tradingUnderlyingCode = tradingUnderlyingCode

    def setFactorUnderlyingCode(self, factorUnderlyingCode):
        self.__factorUnderlyingCode = factorUnderlyingCode

    def setStartDateTime(self, startDateTime):
        self.__startDateTime = startDateTime

    def setEndDateTime(self, endDateTime):
        self.__endDateTime = endDateTime

    def loadData(self):
        print("Loading Data......")

        tradeDatesFile = 'D:\FutureTickData\TradeDates.txt'
        # 读入记录日期的文本文件，这个文件中每一行是一个交易日，目前存了2013年初至2017年底的数据；读入后得到一个内容是字符串list
        tradeDatesStr = open(tradeDatesFile).read().splitlines()
        tradeDatesDT = [dt.datetime.strptime(tradeDatesStr[i], '%Y/%m/%d').date() for i in range(tradeDatesStr.__len__())]    # 将list中字符串类型的日期转为datetime类型的日期

        paraStartDateYear = self.getStartDateTime() // 10000000000
        paraStartDateMonth = (self.getStartDateTime() - paraStartDateYear * 10000000000) // 100000000
        paraStartDateDay = (self.getStartDateTime() - paraStartDateYear * 10000000000 - paraStartDateMonth * 100000000) // 1000000
        paraStartDateHour = (self.getStartDateTime() - paraStartDateYear * 10000000000 - paraStartDateMonth * 100000000 - paraStartDateDay * 1000000) // 10000
        paraStartDateMin = (self.getStartDateTime() - paraStartDateYear * 10000000000 - paraStartDateMonth * 100000000 - paraStartDateDay * 1000000 - paraStartDateHour * 10000) // 100
        paraStartDateSec = self.getStartDateTime() - paraStartDateYear * 10000000000 - paraStartDateMonth * 100000000 - paraStartDateDay * 1000000 - paraStartDateHour * 10000 - paraStartDateMin * 100

        paraEndDateYear = self.getEndDateTime() // 10000000000
        paraEndDateMonth = (self.getEndDateTime() - paraEndDateYear * 10000000000) // 100000000
        paraEndDateDay = (self.getEndDateTime() - paraEndDateYear * 10000000000 - paraEndDateMonth * 100000000) // 1000000
        paraEndDateHour = (self.getEndDateTime() - paraEndDateYear * 10000000000 - paraEndDateMonth * 100000000 - paraEndDateDay * 1000000) // 10000
        paraEndDateMin = (self.getEndDateTime() - paraEndDateYear * 10000000000 - paraEndDateMonth * 100000000 - paraEndDateDay * 1000000 - paraEndDateHour * 10000) // 100
        paraEndDateSec = self.getEndDateTime() - paraEndDateYear * 10000000000 - paraEndDateMonth * 100000000 - paraEndDateDay * 1000000 - paraEndDateHour * 10000 - paraEndDateMin * 100

        paraStartDate = dt.date(paraStartDateYear, paraStartDateMonth, paraStartDateDay)
        paraEndDate = dt.date(paraEndDateYear, paraEndDateMonth, paraEndDateDay)
        paraStartDateTime = dt.datetime(paraStartDateYear, paraStartDateMonth, paraStartDateDay, paraStartDateHour, paraStartDateMin, paraStartDateSec)
        paraEndDateTime = dt.datetime(paraEndDateYear, paraEndDateMonth, paraEndDateDay, paraEndDateHour, paraEndDateMin, paraEndDateSec)

        self.__tradingDays = [t for t in tradeDatesDT if (t >= paraStartDate) and (t <= paraEndDate)]   # 获取回测时间内的交易日

        dictKey = []
        for i in range(len(self.__tradingUnderlyingCode)):
            dictKey = list(set(dictKey + self.__tradingUnderlyingCode[i]))
        dictKey = list(set(dictKey + self.__factorUnderlyingCode))

        self.__dictData = {}
        for i in range(len(dictKey)):
            emptyList = []
            for j in range(len(self.__tradingDays)):
                emptyList.append([])
            self.__dictData.update({dictKey[i]: emptyList[:]})
        for iDictKey in dictKey:
            try:
                iDictStockData = System.ReadDataFile.getData(iDictKey, paraStartDateTime, paraEndDateTime, self.__tradingDays)
            # 获得iDict这只股票（或指数）指定时间段内连续竞价期间的数据
            # iDictStockData是一个list, 长度等于交易日的天数，list中的每个元素即是每个交易日的数据，每个元素的类型都为字典
            except IOError:
                print(iDictKey, "数据不足")   # 若这只股票无数据，则跳过
                continue

            if (iDictKey[0] == "0" and iDictKey[-1] == "H") or (iDictKey[:2] == "39" and iDictKey[-1] == "Z"):  # 如果是指数，则在指数文件夹下读取文档
                for ii in range(iDictStockData.__len__()):
                    stockData = iDictStockData[ii]  # iDict股票每天的数据
                    if stockData is None:
                        continue
                    for i in range(len(stockData['Price'])):
                        lastPrice = stockData['Price'][i]
                        volume = stockData['Volume'][i]
                        amount = stockData['Turover'][i]
                        totalVolume = stockData['AccVolume'][i]
                        totalAmt = stockData['AccTurover'][i]
                        preClose = stockData['PreClose'][i]
                        timeStamp = stockData['TimeStamp'][i]
                        time = stockData['Time'][i]
                        # 如果是指数，则4个盘口数据的信息都为None
                        sliceData = SliceData(iDictKey, timeStamp, time, None, None, None, None, lastPrice,
                                              volume, amount, totalVolume, totalAmt, preClose, None, None, None, None)
                        self.__dictData[iDictKey][ii].append(sliceData)

            elif ((iDictKey[0] == "0" or iDictKey[0] == "3")and iDictKey[-1] == "Z") or (iDictKey[0] == "6" and iDictKey[-1] == "H"):  # 如果是股票
                for ii in range(iDictStockData.__len__()):
                    stockData = iDictStockData[ii]   # iDict股票每天的数据
                    if stockData is None:
                        continue
                    for i in range(len(stockData['BidP1'])):
                        bidPrice = [stockData['BidP1'][i], stockData['BidP2'][i],
                                    stockData['BidP3'][i], stockData['BidP4'][i],
                                    stockData['BidP5'][i]]
                        askPrice = [stockData['AskP1'][i], stockData['AskP2'][i],
                                    stockData['AskP3'][i], stockData['AskP4'][i],
                                    stockData['AskP5'][i]]
                        bidVolume = [stockData['BidV1'][i], stockData['BidV2'][i],
                                     stockData['BidV3'][i], stockData['BidV4'][i],
                                     stockData['BidV5'][i]]
                        askVolume = [stockData['AskV1'][i], stockData['AskV2'][i],
                                     stockData['AskV3'][i], stockData['AskV4'][i],
                                     stockData['AskV5'][i]]
                        lastPrice = stockData['Price'][i]
                        volume = stockData['Volume'][i]
                        amount = stockData['Turover'][i]
                        totalVolume = stockData['AccVolume'][i]
                        totalAmt = stockData['AccTurover'][i]

                        preClose = stockData['PreClose'][i]
                        timeStamp = stockData['TimeStamp'][i]
                        time = stockData['Time'][i]

                        sliceData = SliceData(iDictKey, timeStamp, time, bidPrice, askPrice, bidVolume, askVolume, lastPrice,
                                              volume, amount, totalVolume, totalAmt, preClose, None)
                        self.__dictData[iDictKey][ii].append(sliceData)
            else:
                for ii in range(iDictStockData.__len__()):
                    stockData = iDictStockData[ii]   # iDict股票每天的数据
                    if stockData is None:
                        continue
                    for i in range(len(stockData['BidPrice'])):
                        bidPrice = [stockData['BidPrice'][i]]
                        askPrice = [stockData['AskPrice'][i]]
                        bidVolume = [stockData['BidVolume'][i]]
                        askVolume = [stockData['AskVolume'][i]]
                        lastPrice = stockData['Price'][i]
                        volume = stockData['Volume'][i]
                        amount = stockData['Turover'][i]
                        totalVolume = stockData['AccVolume'][i]
                        totalAmt = stockData['AccTurover'][i]
                        preClose = stockData['PreClose'][i]
                        timeStamp = stockData['TimeStamp'][i]
                        time = stockData['Time'][i]
                        contract = stockData['Contract'][i]
                        sliceData = SliceData(iDictKey, timeStamp, time, bidPrice, askPrice, bidVolume, askVolume, lastPrice,
                                              volume, amount, totalVolume, totalAmt, preClose, contract)
                        self.__dictData[iDictKey][ii].append(sliceData)
        print("Finish Loading Data......")
        self.__lenForLoop = [len(self.__tradingUnderlyingCode), len(self.__tradingDays)]

    def getSliceData(self):
        sendSlice = self.__prepareData[self.__indexForPrepare[0]][self.__iterList[0]]
        indexMove = 0
        if len(self.__indexForPrepare) > 1:
            for i in range(len(self.__indexForPrepare)):
                if self.__prepareData[self.__indexForPrepare[i]][self.__iterList[i]].timeStamp < sendSlice.timeStamp:
                    sendSlice = self.__prepareData[self.__indexForPrepare[i]][self.__iterList[i]]
                    indexMove = i
        self.__iterList[indexMove] += 1

        if len(self.__prepareData[self.__indexForPrepare[indexMove]]) <= self.__iterList[indexMove]:
            self.__indexForPrepare.pop(indexMove)
            self.__iterList.pop(indexMove)
        return sendSlice

    def prepareSliceData(self, iTradingUnderlyingCode, iDate):
        self.__iterList = []
        dictKey = list(set(self.__tradingUnderlyingCode[iTradingUnderlyingCode] + self.__factorUnderlyingCode))
        self.__indexForPrepare = list(range(dictKey.__len__()))
        self.__prepareData = []
        sliceNum = 0
        for i in range(len(dictKey)):
            self.__prepareData.append(self.__dictData[dictKey[i]][iDate])
            self.__iterList.append(0)
            if len(self.__dictData[dictKey[i]][iDate]) != 0:
                sliceNum = sliceNum + len(self.__dictData[dictKey[i]][iDate])
            else:
                sliceNum = 0   # 只要当天组内有一只股票停牌，那么令sliceNum=0，并结束循环，返回0
                break
        return sliceNum
