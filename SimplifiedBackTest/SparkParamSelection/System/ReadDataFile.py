# -*- coding: utf-8 -*-
"""
Created on Tue Aug 22 17:53:24 2017
Updated on 2018/5/7：将取tick数据的getData函数中的exchangeTradingDayList的默认值设为None, 这样调用该函数时可不传入exchangeTradingDaylist，方便调试
但为了不修改其他部分的代码，传入exchangeTradingDayList程序也可正常跑通
Updated on 2018/5/10 16:55 -- 修正了timeMode=1的bug
@author: 006566
"""
import pandas as pd
import datetime as dt
import numpy as np
import scipy.io as sio


def getData(stockCode, startDateTime, endDateTime, exchangeTradingDayList=None, timeMode=1):
    """
    getData这个函数是根据输入的股票代码、开始日期时间、终止日期时间及交易所日历中的交易日(exchangeTradingDayList)，输出所选的股票tick数据
    输出的数据的格式是list, 其长度等于开始日期和终止日期之间的交易所日历交易日天数
    输出的list的内容是dict, 若某天股票停牌，则当天为空
    timeMode默认=1，则输出的每天的数据的时间是startDateTime.time()和endDateTime.time()之间的时间
    若timeMode=2，则输出的每天的数据的时间就是连续竞价期间的时间
    """
    if exchangeTradingDayList is None:  # 若没有传入exchangeTradingDayList，则计算一遍
        tradeDatesFile = 'S:\TradeDates.txt'
        tradeDatesStr = open(tradeDatesFile).read().splitlines()  # 读入记录日期的文本文件，这个文件中每一行是一个交易日，目前存了2013年以来的数据；读入后得到一个内容是字符串list
        tradeDatesDT = [dt.datetime.strptime(tradeDatesStr[i], '%Y/%m/%d').date() for i in range(tradeDatesStr.__len__())]  # 将list中字符串类型的日期转为datetime类型的日期
        paraStartDate = dt.date(startDateTime.year, startDateTime.month, startDateTime.day)
        paraEndDate = dt.date(endDateTime.year, endDateTime.month, endDateTime.day)
        exchangeTradingDayList = [t for t in tradeDatesDT if (t >= paraStartDate) and (t <= paraEndDate)]   # 获取回测时间内的交易日

    # 根据startDateTime和endDateTime输出年月，例如输入dt.datetime(2016,11,9,9,30,00)和dt.datetime(2017,1,5,15,30,00)
    # 输出的yearMonthList是 ['2016-11', '2016-12', '2017-01']
    yearMonthList = []
    tempDateTime = startDateTime
    startTime8digit = startDateTime.hour * 10000000 + startDateTime.minute*100000 + startDateTime.second * 1000
    endTime8digit = endDateTime.hour * 10000000 + endDateTime.minute*100000 + endDateTime.second * 1000
    while tempDateTime <= endDateTime:
        yearMonthList.append(tempDateTime)
        tempDateTime += dt.timedelta(days=1)
    for i in range(yearMonthList.__len__()):
        yearMonthList[i] = str(yearMonthList[i])[0:7]
    yearMonthList = list(set(yearMonthList))
    yearMonthList.sort()

    StockData = pd.DataFrame()
    for i in range(yearMonthList.__len__()):
        if (stockCode[0] == "0" and stockCode[-1] == "H") or (stockCode[:2] == "39" and stockCode[-1] == "Z"):  # 如果是指数，则在指数文件夹下读取文档
            matFilePath = 'S:\\MatData\\IndexTickData\\' + stockCode + '\\TickInfo_' + stockCode + '_' + yearMonthList[i] + '.mat'
        else:
            matFilePath = 'S:\\MatData\\StockTickData\\' + stockCode + '\\TickInfo_' + stockCode + '_' + yearMonthList[i] + '.mat'
        try:
            matData = sio.loadmat(matFilePath)  # 将matlab数据读进来，得到一个叫matData的字典
        except FileNotFoundError:
            print(stockCode, yearMonthList[i], "无数据")   # 若这只股票当月无数据文件，则跳过
            continue
        if len(matData['TimeStamp']) == 0:  # 若股票整个月都停牌，则跳过
            continue
        DateTimeIndex = [None for _ in range(len(matData['TimeStamp']))]
        for iTime in range(0, len(matData['TimeStamp'])):
            DateTimeIndex[iTime] = dt.datetime.fromtimestamp(matData['TimeStamp'][iTime])
        del matData['__header__']  # 读入mat文件会生成这3个无用的数据，删去
        del matData['__version__']
        del matData['__globals__']
        tempStockData = pd.DataFrame(index=DateTimeIndex)
        for key in matData:
            tempStockData[key] = matData[key]
        if StockData.__len__() > 0:
            StockData = StockData.append(tempStockData)
        else:
            StockData = tempStockData.copy()

    if StockData.__len__() == 0:  # 如完全无数据
        return [None]

    startDateTimeStamp = startDateTime.timestamp()
    endDateTimeStamp = endDateTime.timestamp()
    validTime1 = (StockData['TimeStamp'] >= startDateTimeStamp) & (StockData['TimeStamp'] <= endDateTimeStamp)
    StockData = StockData[validTime1]  # 仅保留startDateTime和endDateTime之间的数据
    if timeMode == 1:
        if stockCode[-1] == 'H':  # 上交所的股票或指数
            timeFilter = (startTime8digit <= StockData['Time']) & (StockData['Time'] <= endTime8digit) & \
                         ((StockData['Time'] < 113000000) | (StockData['Time'] >= 130000000)) & (StockData['Time'] < 145957000)
        else:  # 深交所的股票或指数
            timeFilter = (startTime8digit <= StockData['Time']) & (StockData['Time'] <= endTime8digit) &\
                         ((StockData['Time'] < 113000000) | (StockData['Time'] >= 130000000)) & (StockData['Time'] < 145657000)
    else:
        if stockCode[-1] == 'H':  # 上交所的股票或指数
            timeFilter = ((StockData['Time'] >= 93000000) & (StockData['Time'] < 113000000)) | ((StockData['Time'] >= 130000000) & (StockData['Time'] < 145957000))
        else:   # 深交所的股票或指数
            timeFilter = ((StockData['Time'] >= 93000000) & (StockData['Time'] < 113000000)) | ((StockData['Time'] >= 130000000) & (StockData['Time'] < 145657000))
    StockData = StockData[timeFilter]  # 仅保留在连续竞价期间的数据

    tradeDates = list(set(StockData.index.date))   # 股票本身在这段期间的交易日
    tradeDates.sort()   # 对交易日进行排序
    StockData2 = [None for _ in range(exchangeTradingDayList.__len__())]   # StockData2是一个list, 里面每个元素是一天的数据
    for iTradeDate in range(exchangeTradingDayList.__len__()):
        if exchangeTradingDayList[iTradeDate] in tradeDates:     # 对交易所交易日进行循环，如果当天股票有交易
            tempStockData = StockData[str(exchangeTradingDayList[iTradeDate])]
            tempStockData2 = {}
            for column in tempStockData:
                tempStockData2[column] = np.array(tempStockData[column]).tolist()
            StockData2[iTradeDate] = tempStockData2
    return StockData2


def getTransactionData(stockCode, startDateTime, endDateTime, timeMode=1):
    """
    getTransactionData这个函数是根据输入的股票代码、开始日期时间、终止日期时间及交易所日历中的交易日(exchangeTradingDayList，输出所选的股票成交数据
    输出的数据的格式是list, 其长度等于开始日期和终止日期之间的交易所日历交易日天数
    输出的list的内容是dict, 若某天股票停牌，则当天为空
    timeMode默认=1，则输出的每天的数据的时间是startDateTime.time()和endDateTime.time()之间的时间
    若timeMode=2，则输出的每天的数据的时间就是连续竞价期间的时间
    """
    # 根据startDateTime和endDateTime输出年月，例如输入dt.datetime(2016,11,9,9,30,00)和dt.datetime(2017,1,5,15,30,00)
    # 输出的yearMonthList是 ['2016-11', '2016-12', '2017-01']
    tradeDatesFile = 'S:\TradeDates.txt'
    tradeDatesStr = open(tradeDatesFile).read().splitlines()  # 读入记录日期的文本文件，这个文件中每一行是一个交易日，目前存了2013年以来的数据；读入后得到一个内容是字符串list
    tradeDatesDT = [dt.datetime.strptime(tradeDatesStr[i], '%Y/%m/%d').date() for i in range(tradeDatesStr.__len__())]  # 将list中字符串类型的日期转为datetime类型的日期
    paraStartDate = dt.date(startDateTime.year, startDateTime.month, startDateTime.day)
    paraEndDate = dt.date(endDateTime.year, endDateTime.month, endDateTime.day)
    exchangeTradingDayList = [t for t in tradeDatesDT if (t >= paraStartDate) and (t <= paraEndDate)]   # 获取回测时间内的交易日

    yearMonthList = []
    tempDateTime = startDateTime
    startTime8digit = startDateTime.hour * 10000000 + startDateTime.minute*100000 + startDateTime.second * 1000
    endTime8digit = endDateTime.hour * 10000000 + endDateTime.minute*100000 + endDateTime.second * 1000
    while tempDateTime <= endDateTime:
        yearMonthList.append(tempDateTime)
        tempDateTime += dt.timedelta(days=1)
    for i in range(yearMonthList.__len__()):
        yearMonthList[i] = str(yearMonthList[i])[0:7]
    yearMonthList = list(set(yearMonthList))
    yearMonthList.sort()

    StockData = pd.DataFrame()
    for i in range(yearMonthList.__len__()):
        matFilePath = 'S:\\MatData\\TransactionData\\' + stockCode + '\\Transaction_' + stockCode + '_' + yearMonthList[i] + '.mat'
        try:
            matData = sio.loadmat(matFilePath)  # 将matlab数据读进来，得到一个叫matData的字典
        except FileNotFoundError:
            print(stockCode, yearMonthList[i], "无数据")   # 若这只股票当月无数据文件，则跳过
            continue
        if len(matData['TimeStamp']) == 0:  # 若股票整个月都停牌，则跳过
            continue
        DateTimeIndex = [None for _ in range(len(matData['TimeStamp']))]
        for iTime in range(0, len(matData['TimeStamp'])):
            DateTimeIndex[iTime] = dt.datetime.fromtimestamp(matData['TimeStamp'][iTime])
        del matData['__header__']   # 读入mat文件会生成这3个无用的数据，删去
        del matData['__version__']
        del matData['__globals__']
        tempStockData = pd.DataFrame(index=DateTimeIndex)
        for key in matData:
            tempStockData[key] = matData[key]
        if StockData.__len__() > 0:
            StockData = StockData.append(tempStockData)
        else:
            StockData = tempStockData.copy()

    if StockData.__len__() == 0:  # 如完全无数据
        return [None]

    startDateTimeStamp = startDateTime.timestamp()
    endDateTimeStamp = endDateTime.timestamp()
    validTime1 = (StockData['TimeStamp'] >= startDateTimeStamp) & (StockData['TimeStamp'] <= endDateTimeStamp)
    StockData = StockData[validTime1]  # 仅保留startDateTime和endDateTime之间的数据
    if timeMode == 1:
        if stockCode[-1] == 'H':  # 上交所的股票
            timeFilter = ((StockData['Time'] >= startTime8digit) & (StockData['Time'] < 113000000)) | ((StockData['Time'] >= 130000000) & (StockData['Time'] < 145957000) & (StockData['Time'] < endTime8digit))
        else:  # 深交所的股票
            timeFilter = ((StockData['Time'] >= startTime8digit) & (StockData['Time'] < 113000000)) | ((StockData['Time'] >= 130000000) & (StockData['Time'] < 145657000) & (StockData['Time'] < endTime8digit))
    else:
        if stockCode[-1] == 'H':  # 上交所的股票
            timeFilter = ((StockData['Time'] >= 93000000) & (StockData['Time'] < 113000000)) | ((StockData['Time'] >= 130000000) & (StockData['Time'] < 145957000))
        else:  # 深交所的股票
            timeFilter = ((StockData['Time'] >= 93000000) & (StockData['Time'] < 113000000)) | ((StockData['Time'] >= 130000000) & (StockData['Time'] < 145657000))
    StockData = StockData[timeFilter]  # 仅保留在连续竞价期间的数据
    # del StockData['Time']

    tradeDates = list(set(StockData.index.date))  # 股票本身在这段期间的交易日
    tradeDates.sort()  # 对交易日进行排序
    StockData2 = [None for _ in range(exchangeTradingDayList.__len__())]  # StockData2是一个list, 里面每个元素是一天的数据
    for iTradeDate in range(exchangeTradingDayList.__len__()):
        if exchangeTradingDayList[iTradeDate] in tradeDates:  # 对交易所交易日进行循环，如果当天股票有交易
            tempStockData = StockData[str(exchangeTradingDayList[iTradeDate])]
            tempStockData2 = {}
            for column in tempStockData:
                tempStockData2[column] = np.array(tempStockData[column]).tolist()
            StockData2[iTradeDate] = tempStockData2
    return StockData2


# 以下代码是为了测试用的，可不用理会
# 引用时请修改下列3个要素
# startDateTime = dt.datetime(2017, 7, 17, 9, 40, 00)
# endDateTime = dt.datetime(2017, 9, 20, 10, 00, 00)
# stockCode = '000002.SZ'
# tradeDatesFile = 'S:\TradeDates.txt'
# tradeDatesStr = open(tradeDatesFile).read().splitlines()
# tradeDatesDT = [dt.datetime.strptime(tradeDatesStr[i], '%Y/%m/%d').date() for i in range(tradeDatesStr.__len__())]
# startDate = startDateTime.date()
# endDate = endDateTime.date()
# tradingDays = [t for t in tradeDatesDT if (t >= startDate) and (t <= endDate)]  # 获取回测时间内的交易日
#
# data1 = getData(stockCode, startDateTime, endDateTime, tradingDays, 1)
# print("break point here")

# 获取transaction data
# transactionData = getTransactionData(stockCode, startDateTime, endDateTime)
# print("break point here")
# 获取tick data
# tickData = getTransactionData(stockCode, startDateTime, endDateTime, exchangeTradingDays)
# print("break point here")
