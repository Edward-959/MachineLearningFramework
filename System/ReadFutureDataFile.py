# -*- coding: utf-8 -*-
"""
Created on 2019/1/16
@author: Xiu Zixing
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
        tradeDatesFile = 'C:\\Users\\USER\\Desktop\\TradeDates.txt'
        tradeDatesStr = open(tradeDatesFile).read().splitlines()  # 读入记录日期的文本文件，这个文件中每一行是一个交易日，目前存了2013年以来的数据；读入后得到一个内容是字符串list
        tradeDatesDT = [dt.datetime.strptime(tradeDatesStr[i], '%Y/%m/%d').date() for i in range(tradeDatesStr.__len__())]  # 将list中字符串类型的日期转为datetime类型的日期
        paraStartDate = dt.date(startDateTime.year, startDateTime.month, startDateTime.day)
        paraEndDate = dt.date(endDateTime.year, endDateTime.month, endDateTime.day)
        exchangeTradingDayList = [t for t in tradeDatesDT if (t >= paraStartDate) and (t <= paraEndDate)]   # 获取回测时间内的交易日

    # 根据startDateTime和endDateTime输出年月，例如输入dt.datetime(2016,11,9,9,30,00)和dt.datetime(2017,1,5,15,30,00)
    # 输出的yearMonthList是 ['2016-11-01', '2016-12-01', '2017-01-01']
    yearMonthList = []
    tempDateTime = startDateTime
    startTime8digit = startDateTime.hour * 10000000 + startDateTime.minute*100000 + startDateTime.second * 1000
    endTime8digit = endDateTime.hour * 10000000 + endDateTime.minute*100000 + endDateTime.second * 1000
    while tempDateTime <= endDateTime:
        yearMonthList.append(tempDateTime)
        tempDateTime += dt.timedelta(days=1)
    yearMonthList1 = []
    for i in range(yearMonthList.__len__()):
        yearMonthList1.append(yearMonthList[i].strftime('%Y%m'))
    yearMonthList1 = list(set(yearMonthList1))
    yearMonthList1.sort()
    yearMonthList = yearMonthList1

    StockData = pd.DataFrame()
    for i in range(yearMonthList.__len__()):
        if stockCode[-3:] == "SHF" or stockCode[-3:] == "CZC" or stockCode[-3:] == "DCE" or stockCode[-3:] == "CFE":
            matFilePath = 'C:\\Users\\USER\\Desktop\\MachineLearningBackTestFrameWork\\FutureTickData\\'+ stockCode+'\\'\
                          "TickInfo_" + stockCode + '_' + yearMonthList[i] + '.mat'
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
        if StockData['Contract'][0][0:2] == 'RB':
            timeFilter = (startTime8digit <= StockData['Time']) & (StockData['Time'] <= endTime8digit) &\
                         (((StockData['Time'] < 113000000) | (StockData['Time'] >= 133000000)) & (StockData['Time'] < 145657000)|((StockData['Time'] > 210000000) & (StockData['Time'] < 230000000)))
        elif StockData['Contract'][0][0:2] == 'TA':
            timeFilter = (startTime8digit <= StockData['Time']) & (StockData['Time'] <= endTime8digit) &\
                         (((StockData['Time'] < 113000000) | (StockData['Time'] >= 133000000)) & (StockData['Time'] < 145657000)|((StockData['Time'] > 210000000) & (StockData['Time'] < 233000000)))
    else:
        timeFilter = ((StockData['Time'] >= 93000000) & (StockData['Time'] < 11300000000)) | ((StockData['Time'] >= 130000000) & (StockData['Time'] < 145657000))
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