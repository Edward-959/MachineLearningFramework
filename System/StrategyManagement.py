# -*- coding: utf-8 -*-
"""
Created on Thu Aug 10 22:27:59 2017
@author: 006547
"""
from System.DataBroadcast import DataBroadcast
from System.ExecuteStrategy import ExecuteStrategy
from System.ProgressBar import ProgressBar
import datetime as dt


class StrategyManagement:
    def __init__(self):
        self.__strategy = []
        self.__dataBroadcast = []

    def registerStrategy(self, strategy):
        # 将策略注册到策略管理模块
        if self in self.__strategy:
            pass
        else:
            self.__strategy.append(strategy)

    def start(self):
        startTimeStamp = dt.datetime.timestamp(dt.datetime.now())
        bar = ProgressBar()
        for iStrategy in range(len(self.__strategy)):
            dataBroadcast = self.__dataBroadcast[iStrategy]
            for iTradingUnderlyingCode in range(dataBroadcast.getLenForLoop()[0]):
                preDayTicks= []
                for iDate in range(dataBroadcast.getLenForLoop()[1]):
                    sliceNum = dataBroadcast.prepareSliceData(iTradingUnderlyingCode, iDate)
                    if sliceNum < 150:   # 如果sliceNum ==0 则表示当天组中有至少一只股票停牌，那么跳过
                        continue
                    self.__strategy[iStrategy].getExecuteStrategy()[iTradingUnderlyingCode].append(
                        ExecuteStrategy(self.__strategy[iStrategy], iTradingUnderlyingCode))    # 实例化一个ExecuteStrategy的类
                    executeStrategy = self.__strategy[iStrategy].getExecuteStrategy()[iTradingUnderlyingCode][-1]   #[-1]的意思就是刚刚实例化的那个，因为上面的名字太长了，这里临时命名一个引用
                    if len(preDayTicks) != 0:
                        executeStrategy.setPreDayticks(preDayTicks)
                        preDayTicks = []
                        try:
                            for iSlice in range(sliceNum):
                                print("Proccessing Date %i of %i Days, Slice %i of %i Slice" % (
                                iDate + 1, dataBroadcast.getLenForLoop()[1], iSlice + 1, sliceNum))
                                sliceData = dataBroadcast.getSliceData()
                                if iSlice == sliceNum - 1:
                                    sliceData.isLastSlice = True
                                executeStrategy.onMarketData(sliceData)    # 把数据传进去并且计算
                                executeStrategy.saveOutput()               # 把数据保存
                                preDayTicks.append(sliceData)
                        except Exception:
                            print("出错")
                    else:
                        for iSlice in range(sliceNum):
                            sliceData = dataBroadcast.getSliceData()
                            preDayTicks.append(sliceData)


                    del executeStrategy                            # 删除刚刚临时命名的那个引用名
                    bar.move(len(self.__strategy) * dataBroadcast.getLenForLoop()[0] * dataBroadcast.getLenForLoop()[1])
                    bar.log()
        endTimeStamp = dt.datetime.timestamp(dt.datetime.now())
        print("Calculating time: " + str(round((endTimeStamp - startTimeStamp) / 60, 2)) + " min")

    def loadData(self):
        startTimeStamp = dt.datetime.timestamp(dt.datetime.now())
        for iStrategy in range(len(self.__strategy)):
            dataBroadcast = DataBroadcast()
            self.__dataBroadcast.append(dataBroadcast)
            dataBroadcast.setTradingUnderlyingCode(self.__strategy[iStrategy].getTradingUnderlyingCode())
            dataBroadcast.setFactorUnderlyingCode(self.__strategy[iStrategy].getFactorUnderlyingCode())
            dataBroadcast.setStartDateTime(self.__strategy[iStrategy].getStartDateTime())
            dataBroadcast.setEndDateTime(self.__strategy[iStrategy].getEndDateTime())
            dataBroadcast.loadData()
        endTimeStamp = dt.datetime.timestamp(dt.datetime.now())
        print("Load data time: " + str(round(endTimeStamp - startTimeStamp, 2)) + "s")

    def getStrategy(self):
        return self.__strategy

    def getDataBroadcast(self):
        return self.__dataBroadcast
