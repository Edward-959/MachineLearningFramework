# -*- coding: utf-8 -*-
"""
Created on Wed Aug 16 13:51:09 2017

@author: 006547 & 006566
updated: 2018/4/25
如要添加新标签子类（SubTag），注意需添加如下几处：
1) 实例化储存不同算法标签的类
2) def calculate
3) def SubTag（视情况而定）

updated: 2018/6/14 & 6/15 & 6/22
1） 把涉及时间的MaxMin类subTag的计算方法，都改为最后计算（原来是过程中逐步更新）
2） 新增了1minMaxMinLong和1minMaxMinShort两类标签，以1minMaxMinLong为例，它的returnRate有3个值，都是以卖1价开仓、
    买1价平仓计算的，这3个值分别是：[相对开仓点的最大涨幅、相对开仓点的最大跌幅、从开仓点到最大涨幅之间相对开仓点的最大
    跌幅]， 1minMaxMinShort则类似，以买1价开仓、卖1价平仓；
3)  新增了1minRR，它的returnRate有4个值，即1minMaxMinLong的第1个值、第3个值和1minMaxMinShort的第1个值和第3个值

updated: 2018/6/25 —— 1) 新增1minMM12s，2minMM12s
2) 为了给pickle文件节约空间，把1minMaxMinLong, 1minMaxMinShort, 2minMaxMinLong, 2minMaxMinShort,1min和2min的endSliceData注释了

updated: 2018/6/28 & 7/2
1) 新增1minLongAB -- 以Ask1的价格开仓，1min后Bid1价格平仓； 1minShortBA, 2minLongAB, 2minShortBA同理
2) 新增1minLongAVWAP -- 以Ask1的价格开仓，整个1min的VWap平仓；1minShortBVWAP, 2minLongAVWAP, 2minShortBVWAP同理
3) 修正了LongAVWP（以及ShortBVWP）等标签中计算收益率时除数为0的问题

updated: 2018/7/11 & 7/25  删除endSliceData; 修正逐笔成交的bug
updated: 2018/8/2 修正了self.__ask1PriceList的错误，为subTag新增了startMidPrice和endMidPrice两个属性
"""
from System.BaseTag import BaseTag
from datetime import datetime
from numpy import mean


class Tag(BaseTag):
    def __init__(self, para, factorManagement, sliceData):
        BaseTag.__init__(self, para, factorManagement)
        # 获取Tag计算参数
        self.__paraMaxDropHorizon = para["paraMaxDropHorizon"]
        self.__paraEmaMidPriceLag = para["paraEmaMidPriceLag"]
        self.__paraOrderPressureLag = para["paraOrderPressureLag"]
        self.__paraNumOrderMax = para['paraNumOrderMax']  # 比较盘口档位数
        self.__paraNumOrderMin = para['paraNumOrderMin']  # 比较盘口档位数
        self.__paraEmaSlicePressureLag = para["paraEmaSlicePressureLag"]
        self.__paraMaxLose = para["paraMaxLose"]
        self.__paraFastLag = para["paraFastLag"]
        self.__paraSlowLag = para["paraSlowLag"]

        # 获取数据和其他因子值
        self.__data = self.getTradingUnderlyingData(self.getIndexTradingUnderlying()[0])
        self.__midPrice = self.getFactorData({"name": "midPrice", "className": "MidPrice",
                                              "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                              "indexFactorUnderlying": self.getIndexFactorUnderlying()})
        paraEmaMidPrice = {"name": "emaMidPrice", "className": "Ema",
                           "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                           "indexFactorUnderlying": self.getIndexFactorUnderlying(),
                           "paraLag": self.__paraEmaMidPriceLag,
                           "paraOriginalData": {"name": "midPrice", "className": "MidPrice",
                                                "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                                "indexFactorUnderlying": self.getIndexFactorUnderlying()}}
        self.__emaMidPrice = self.getFactorData(paraEmaMidPrice)
        self.__orderPressure = self.getFactorData({"name": "orderPressure", "className": "FactorOrderPressure",
                                                   "indexTradingUnderlying": [0], "indexFactorUnderlying": [],
                                                   "paraOrderPressureLag": self.__paraOrderPressureLag})
        self.__emaSlicePressure = self.getFactorData({"name": "emaSlicePressure", "className": "FactorEmaSlicePressure",
                                                      "indexTradingUnderlying": [0], "indexFactorUnderlying": [],
                                                      "paraNumOrderMax": self.__paraNumOrderMax,
                                                      "paraNumOrderMin": self.__paraNumOrderMin,
                                                      "paraEmaSlicePressureLag": self.__paraEmaSlicePressureLag})
        self.__extremePoint = self.getFactorData({"name": "extremePoint", "className": "ExtremePoint",
                                                  "indexTradingUnderlying": self.getIndexTradingUnderlying(),
                                                  "indexFactorUnderlying": self.getIndexFactorUnderlying(),
                                                  "paraFastLag": self.__paraFastLag, "paraSlowLag": self.__paraSlowLag})
        self.__extremePointInfo = self.__extremePoint.getExtremePointInfo()
        # 实例化储存不同算法标签的类
        self.subTag = {}
        self.subTag.update({"1min": SubTag(self.__data, self.__midPrice, sliceData, "mid", 0, 0)})
        # self.subTag.update({"2min": SubTag(self.__data, self.__midPrice, sliceData, "mid", 0, 0)})
        # self.subTag.update({"5min": SubTag(self.__data, self.__midPrice, sliceData, "mid", 0, 0)})
        # self.subTag.update({"1minMaxMin": SubTag(self.__data, self.__midPrice, sliceData, "mid", 0, 0, "list", 2)})
        self.subTag.update({"2minMaxMin": SubTag(self.__data, self.__midPrice, sliceData, "mid", 0, 0, "list", 2)})
        # self.subTag.update({"5minMaxMin": SubTag(self.__data, self.__midPrice, sliceData, "mid", 0, 0, "list", 2)})
        # self.subTag.update({"1minMaxMinLong": SubTag(self.__data, self.__midPrice, sliceData, "ask1", 1, 0, "list", 3)})
        # self.subTag.update({"1minMaxMinShort": SubTag(self.__data, self.__midPrice, sliceData, "bid1", 1, 0, "list", 3)})
        # self.subTag.update({"1minRR": SubTag(self.__data, self.__midPrice, sliceData, "mid", 0, 0, "list", 4)})
        # self.subTag.update({"2minMaxMinLong": SubTag(self.__data, self.__midPrice, sliceData, "ask1", 1, 0, "list", 3)})
        # self.subTag.update({"2minMaxMinShort": SubTag(self.__data, self.__midPrice, sliceData, "bid1", 1, 0, "list", 3)})
        # self.subTag.update({"2minRR": SubTag(self.__data, self.__midPrice, sliceData, "mid", 0, 0, "list", 4)})
        # self.subTag.update({"1minLongAB": SubTag(self.__data, self.__midPrice, sliceData, "ask1", 1, 0)})
        # self.subTag.update({"1minShortBA": SubTag(self.__data, self.__midPrice, sliceData, "bid1", 1, 0)})
        # self.subTag.update({"2minLongAB": SubTag(self.__data, self.__midPrice, sliceData, "ask1", 1, 0)})
        # self.subTag.update({"2minShortBA": SubTag(self.__data, self.__midPrice, sliceData, "bid1", 1, 0)})
        # self.subTag.update({"1minLongAVWAP": SubTag(self.__data, self.__midPrice, sliceData, "ask1", 1, 0)})
        # self.subTag.update({"1minShortBVWAP": SubTag(self.__data, self.__midPrice, sliceData, "bid1", 1, 0)})
        # self.subTag.update({"2minLongAVWAP": SubTag(self.__data, self.__midPrice, sliceData, "ask1", 1, 0)})
        # self.subTag.update({"2minShortBVWAP": SubTag(self.__data, self.__midPrice, sliceData, "bid1", 1, 0)})
        # self.subTag.update({"BASpread": SubTag(self.__data, self.__midPrice, sliceData, "mid", 0, 0, "list", 3)})
        # self.subTag.update({"BASpreadPercent": SubTag(self.__data, self.__midPrice, sliceData, "mid", 0, 0, "list", 3)})

        self.finished = False
        if sliceData.isLastSlice:
            self.finished = True
        # 需要用到的中间变量
        self.__maxDrop_Up_3 = 0
        self.__maxDrop_Up_2 = 0
        self.__maxRise_Down_3 = 0
        self.__maxRise_Down_2 = 0
        self.__maxEmaMidPrice_Up_2 = 0
        self.__maxEmaMidPrice_Up_3 = 0
        self.__minEmaMidPrice_Down_3 = 0
        self.__minEmaMidPrice_Down_2 = 0
        self.__maxDropLong = 0
        self.__maxDropShort = 0
        self.__maxEmaMidPrice = self.__emaMidPrice.getLastContent()
        self.__minEmaMidPrice = self.__emaMidPrice.getLastContent()
        self.__bid1PriceList = []
        self.__ask1PriceList = []
        self.__midPriceList = []
        self.__timeStampList = []
        self.__amountList = []
        self.__volumeList = []

    def calculate(self, sliceData):
        if self.__data.getLastContent().bidPrice[0] > 0:
            self.__bid1PriceList.append(self.__data.getLastContent().bidPrice[0])
        else:
            self.__bid1PriceList.append(self.__midPrice.getLastContent())
        if self.__data.getLastContent().askPrice[0] > 0:
            self.__ask1PriceList.append(self.__data.getLastContent().askPrice[0])
        else:
            self.__ask1PriceList.append(self.__midPrice.getLastContent())
        self.__midPriceList.append(self.__midPrice.getLastContent())
        self.__timeStampList.append(sliceData.timeStamp)
        self.__amountList.append(sliceData.amount)
        self.__volumeList.append(sliceData.volume)

        # 1min 持仓1分钟，以中间价计算收益率
        if len(self.__emaMidPrice.getContent()) > 0 and len(self.__orderPressure.getContent()) > 0 \
                and (not self.subTag["1min"].finished):
            timeElapsed = TimeElapsed(sliceData.timeStamp, self.subTag["1min"].startTimeStamp)
            if timeElapsed >= 60 or sliceData.isLastSlice:
                self.subTag["1min"].endTimeStamp = sliceData.timeStamp
                self.subTag["1min"].endPrice = self.__midPrice.getLastContent()
                self.subTag["1min"].returnRate = self.subTag["1min"].endPrice / self.subTag["1min"].startPrice - 1
                self.subTag["1min"].endMidPrice = self.__midPrice.getLastContent()
                self.subTag["1min"].finished = True
        # # 2min 持仓2分钟，以中间价计算收益率
        # if len(self.__emaMidPrice.getContent()) > 0 and len(self.__orderPressure.getContent()) > 0 \
        #         and (not self.subTag["2min"].finished):
        #     timeElapsed = TimeElapsed(sliceData.timeStamp, self.subTag["2min"].startTimeStamp)
        #     if timeElapsed >= 120 or sliceData.isLastSlice:
        #         self.subTag["2min"].endTimeStamp = sliceData.timeStamp
        #         self.subTag["2min"].endPrice = self.__midPrice.getLastContent()
        #         self.subTag["2min"].returnRate = \
        #             self.subTag["2min"].endPrice / self.subTag["2min"].startPrice - 1
        #         self.subTag["2min"].endMidPrice = self.__midPrice.getLastContent()
        #         self.subTag["2min"].finished = True
        #
        # # "1min 最大涨幅、最大跌幅"，subTag的returnRate一个list，长度为2，第1个值是未来1分钟的最大涨幅，第2个值是未来1分钟的最大跌幅
        # if len(self.__emaMidPrice.getContent()) > 0 and len(self.__orderPressure.getContent()) > 0 and (
        #         not self.subTag["1minMaxMin"].finished):
        #     timeElapsed = TimeElapsed(sliceData.timeStamp, self.subTag["1minMaxMin"].startTimeStamp)
        #     if timeElapsed >= 60 or sliceData.isLastSlice:
        #         if self.subTag["1minMaxMin"].startPrice > 0 and self.__midPriceList.__len__() > 0:
        #             self.subTag["1minMaxMin"].returnRate[0] = max(self.__midPriceList) / self.subTag["1minMaxMin"].startPrice - 1
        #             self.subTag["1minMaxMin"].returnRate[1] = min(self.__midPriceList) / self.subTag["1minMaxMin"].startPrice - 1
        #         else:
        #             self.subTag["1minMaxMin"].returnRate = [0, 0]
        #         self.subTag["1minMaxMin"].endTimeStamp = sliceData.timeStamp
        #         self.subTag["1minMaxMin"].endPrice = self.__midPrice.getLastContent()
        #         self.subTag["1minMaxMin"].endMidPrice = self.__midPrice.getLastContent()
        #         self.subTag["1minMaxMin"].finished = True

        # "2min 最大涨幅、最大跌幅"，subTag的returnRate一个list，长度为2，第1个值是未来2分钟的最大涨幅，第2个值是未来2分钟的最大跌幅
        if len(self.__emaMidPrice.getContent()) > 0 and len(self.__orderPressure.getContent()) > 0 and (
                not self.subTag["2minMaxMin"].finished):
            timeElapsed = TimeElapsed(sliceData.timeStamp, self.subTag["2minMaxMin"].startTimeStamp)
            if timeElapsed >= 120 or sliceData.isLastSlice:
                if self.subTag["2minMaxMin"].startPrice > 0 and self.__midPriceList.__len__() > 0:
                    self.subTag["2minMaxMin"].returnRate[0] = max(self.__midPriceList) / self.subTag["2minMaxMin"].startPrice - 1
                    self.subTag["2minMaxMin"].returnRate[1] = min(self.__midPriceList) / self.subTag["2minMaxMin"].startPrice - 1
                else:
                    self.subTag["2minMaxMin"].returnRate = [0, 0]
                self.subTag["2minMaxMin"].endTimeStamp = sliceData.timeStamp
                self.subTag["2minMaxMin"].endPrice = self.__midPrice.getLastContent()
                self.subTag["2minMaxMin"].endMidPrice = self.__midPrice.getLastContent()
                self.subTag["2minMaxMin"].finished = True

        # # "1minMaxMinLong", 1min做多最高收益率和最大回撤 ，以起始时的卖1开仓、买1平仓计算
        # if len(self.__emaMidPrice.getContent()) > 0 and len(self.__orderPressure.getContent()) > 0 and (
        #         not self.subTag["1minMaxMinLong"].finished):
        #     timeElapsed = TimeElapsed(sliceData.timeStamp, self.subTag["1minMaxMinLong"].startTimeStamp)
        #     # 如开仓价是涨停价——应当不能买入，则收益率直接赋为0，并结束
        #     if self.subTag["1minMaxMinLong"].startPrice == 0:
        #         self.subTag["1minMaxMinLong"].returnRate = [0, 0, 0]
        #         self.subTag["1minMaxMinLong"].endTimeStamp = sliceData.timeStamp
        #         self.subTag["1minMaxMinLong"].endPrice = self.__data.getLastContent().bidPrice[0]
        #         self.subTag["1minMaxMinLong"].endMidPrice = self.__midPrice.getLastContent()
        #         self.subTag["1minMaxMinLong"].finished = True
        #     # 如时间超过60秒，或初始化时遇到最后一个tick的切片
        #     if timeElapsed >= 60 or sliceData.isLastSlice:
        #         if self.subTag["1minMaxMinLong"].startPrice > 0 and self.__bid1PriceList.__len__() > 0:
        #             self.subTag["1minMaxMinLong"].returnRate[0] = max(self.__bid1PriceList) / self.subTag[
        #                 "1minMaxMinLong"].startPrice - 1  # 区间中，相对于开仓点的最大涨幅
        #             self.subTag["1minMaxMinLong"].returnRate[1] = min(self.__bid1PriceList) / self.subTag[
        #                 "1minMaxMinLong"].startPrice - 1  # 区间中，相对于开仓点的最大跌幅
        #             # 接下来计算“从开仓点到最高价的路径中，相对于开仓点的最大回撤”
        #             # 如相对于开仓点的最大涨幅<=0，则做多的“最高点”无意义，这时令最大回撤0
        #             if self.subTag["1minMaxMinLong"].returnRate[0] <= 0:
        #                 self.subTag["1minMaxMinLong"].returnRate[2] = 0
        #             else:
        #                 # 找到最高价的位置（如有重复为第1个值）
        #                 maxIndex = self.__bid1PriceList.index(max(self.__bid1PriceList))
        #                 if maxIndex > 1:
        #                     # 从开仓点到最高价之间，找到最低点的索引
        #                     drawbackIndex = self.__bid1PriceList[:maxIndex + 1].index(
        #                         min(self.__bid1PriceList[:maxIndex + 1]))
        #                     # 计算“从开仓点到最高价之间的最低点”相对开仓点的收益率，如为负则是最大回撤，否则为0
        #                     self.subTag["1minMaxMinLong"].returnRate[2] = min(0, self.__bid1PriceList[
        #                         drawbackIndex] / self.subTag["1minMaxMinLong"].startPrice - 1)
        #                 else:
        #                     self.subTag["1minMaxMinLong"].returnRate[2] = 0
        #             self.subTag["1minMaxMinLong"].endTimeStamp = sliceData.timeStamp
        #             self.subTag["1minMaxMinLong"].endPrice = self.__data.getLastContent().bidPrice[0]
        #             self.subTag["1minMaxMinLong"].endMidPrice = self.__midPrice.getLastContent()
        #             self.subTag["1minMaxMinLong"].finished = True
        #         else:
        #             self.subTag["1minMaxMinLong"].returnRate = [0, 0, 0]
        #             self.subTag["1minMaxMinLong"].endTimeStamp = sliceData.timeStamp
        #             self.subTag["1minMaxMinLong"].endPrice = self.__data.getLastContent().bidPrice[0]
        #             self.subTag["1minMaxMinLong"].endMidPrice = self.__midPrice.getLastContent()
        #             self.subTag["1minMaxMinLong"].finished = True
        # 
        # # "1minMaxMinShort", 1min做空最高收益率和最大回撤 ，以起始时的买1开仓、卖1平仓计算
        # if len(self.__emaMidPrice.getContent()) > 0 and len(self.__orderPressure.getContent()) > 0 and (
        #         not self.subTag["1minMaxMinShort"].finished):
        #     timeElapsed = TimeElapsed(sliceData.timeStamp, self.subTag["1minMaxMinShort"].startTimeStamp)
        #     # 如开仓价是跌停价——应当不能卖出，则收益率直接赋为0，并结束
        #     if self.subTag["1minMaxMinShort"].startPrice == 0:
        #         self.subTag["1minMaxMinShort"].returnRate = [0, 0, 0]
        #         self.subTag["1minMaxMinShort"].endTimeStamp = sliceData.timeStamp
        #         self.subTag["1minMaxMinShort"].endPrice = self.__data.getLastContent().askPrice[0]
        #         self.subTag["1minMaxMinShort"].endMidPrice = self.__midPrice.getLastContent()
        #         self.subTag["1minMaxMinShort"].finished = True
        #     # 如时间超过60秒，或初始化时遇到最后一个tick的切片
        #     if timeElapsed >= 60 or sliceData.isLastSlice:
        #         if self.subTag["1minMaxMinShort"].startPrice > 0 and self.__ask1PriceList.__len__() > 0:
        #             self.subTag["1minMaxMinShort"].returnRate[0] = min(self.__ask1PriceList) / self.subTag[
        #                 "1minMaxMinShort"].startPrice - 1  # 区间中，相对于开仓点的最大跌幅
        #             self.subTag["1minMaxMinShort"].returnRate[1] = max(self.__ask1PriceList) / self.subTag[
        #                 "1minMaxMinShort"].startPrice - 1  # 区间中，相对于开仓点的最大涨幅
        #             # 接下来计算“从开仓点到最低价的路径中，相对于开仓点的最大回撤”
        #             # 如相对于开仓点的最大跌幅>=0，则做空的“最低点”无意义，这时令最大回撤为0
        #             if self.subTag["1minMaxMinShort"].returnRate[0] >= 0:
        #                 self.subTag["1minMaxMinShort"].returnRate[2] = 0
        #             else:
        #                 # 找到最低价的位置（如有重复为第1个值）
        #                 minIndex = self.__ask1PriceList.index(min(self.__ask1PriceList))
        #                 if minIndex > 1:
        #                     # 从开仓点到最低价之间，找到最高点的索引
        #                     drawbackIndex = self.__ask1PriceList[:minIndex + 1].index(
        #                         max(self.__ask1PriceList[:minIndex + 1]))
        #                     # 计算“从开仓点到最低价之间的最高点”相对开仓点的收益率，如为正则是最大回撤，否则为0
        #                     self.subTag["1minMaxMinShort"].returnRate[2] = max(0, self.__ask1PriceList[
        #                         drawbackIndex] / self.subTag["1minMaxMinShort"].startPrice - 1)
        #                 else:
        #                     self.subTag["1minMaxMinShort"].returnRate[2] = 0
        #             self.subTag["1minMaxMinShort"].endTimeStamp = sliceData.timeStamp
        #             self.subTag["1minMaxMinShort"].endPrice = self.__data.getLastContent().askPrice[0]
        #             self.subTag["1minMaxMinShort"].endMidPrice = self.__midPrice.getLastContent()
        #             self.subTag["1minMaxMinShort"].finished = True
        #         else:
        #             self.subTag["1minMaxMinShort"].returnRate = [0, 0, 0]
        #             self.subTag["1minMaxMinShort"].endTimeStamp = sliceData.timeStamp
        #             self.subTag["1minMaxMinShort"].endPrice = self.__data.getLastContent().askPrice[0]
        #             self.subTag["1minMaxMinShort"].endMidPrice = self.__midPrice.getLastContent()
        #             self.subTag["1minMaxMinShort"].finished = True
        # 
        # # "1minRR -- Reward and Risk
        # if len(self.__emaMidPrice.getContent()) > 0 and len(self.__orderPressure.getContent()) > 0 and (
        #         not self.subTag["1minRR"].finished):
        #     if self.subTag["1minMaxMinLong"].finished and self.subTag["1minMaxMinShort"].finished:
        #         self.subTag["1minRR"].returnRate[0] = self.subTag["1minMaxMinLong"].returnRate[0]
        #         self.subTag["1minRR"].returnRate[1] = self.subTag["1minMaxMinLong"].returnRate[2]
        #         self.subTag["1minRR"].returnRate[2] = self.subTag["1minMaxMinShort"].returnRate[0]
        #         self.subTag["1minRR"].returnRate[3] = self.subTag["1minMaxMinShort"].returnRate[2]
        #         self.subTag["1minRR"].endTimeStamp = sliceData.timeStamp
        #         self.subTag["1minRR"].endPrice = self.__midPrice.getLastContent()
        #         self.subTag["1minRR"].endMidPrice = self.__midPrice.getLastContent()
        #         self.subTag["1minRR"].finished = True
        # 
        # # "2minMaxMinLong", 2min做多最高收益率和最大回撤 ，以起始时的卖1开仓、买1平仓计算
        # if len(self.__emaMidPrice.getContent()) > 0 and len(self.__orderPressure.getContent()) > 0 and (
        #         not self.subTag["2minMaxMinLong"].finished):
        #     timeElapsed = TimeElapsed(sliceData.timeStamp, self.subTag["2minMaxMinLong"].startTimeStamp)
        #     # 如开仓价是涨停价——应当不能买入，则收益率直接赋为0，并结束
        #     if self.subTag["2minMaxMinLong"].startPrice == 0:
        #         self.subTag["2minMaxMinLong"].returnRate = [0, 0, 0]
        #         self.subTag["2minMaxMinLong"].endTimeStamp = sliceData.timeStamp
        #         self.subTag["2minMaxMinLong"].endPrice = self.__data.getLastContent().bidPrice[0]
        #         self.subTag["2minMaxMinLong"].endMidPrice = self.__midPrice.getLastContent()
        #         self.subTag["2minMaxMinLong"].finished = True
        #     # 如时间超过120秒，或初始化时遇到最后一个tick的切片
        #     if timeElapsed >= 120 or sliceData.isLastSlice:
        #         if self.subTag["2minMaxMinLong"].startPrice > 0 and self.__bid1PriceList.__len__() > 0:
        #             self.subTag["2minMaxMinLong"].returnRate[0] = max(self.__bid1PriceList) / self.subTag[
        #                 "2minMaxMinLong"].startPrice - 1  # 区间中，相对于开仓点的最大涨幅
        #             self.subTag["2minMaxMinLong"].returnRate[1] = min(self.__bid1PriceList) / self.subTag[
        #                 "2minMaxMinLong"].startPrice - 1  # 区间中，相对于开仓点的最大跌幅
        #             # 接下来计算“从开仓点到最高价的路径中，相对于开仓点的最大回撤”
        #             # 如相对于开仓点的最大涨幅<=0，则做多的“最高点”无意义，这时令最大回撤0
        #             if self.subTag["2minMaxMinLong"].returnRate[0] <= 0:
        #                 self.subTag["2minMaxMinLong"].returnRate[2] = 0
        #             else:
        #                 # 找到最高价的位置（如有重复为第1个值）
        #                 maxIndex = self.__bid1PriceList.index(max(self.__bid1PriceList))
        #                 if maxIndex > 1:
        #                     # 从开仓点到最高价之间，找到最低点的索引
        #                     drawbackIndex = self.__bid1PriceList[:maxIndex + 1].index(
        #                         min(self.__bid1PriceList[:maxIndex + 1]))
        #                     # 计算“从开仓点到最高价之间的最低点”相对开仓点的收益率，如为负则是最大回撤，否则为0
        #                     self.subTag["2minMaxMinLong"].returnRate[2] = min(0, self.__bid1PriceList[
        #                         drawbackIndex] / self.subTag["2minMaxMinLong"].startPrice - 1)
        #                 else:
        #                     self.subTag["2minMaxMinLong"].returnRate[2] = 0
        #             self.subTag["2minMaxMinLong"].endTimeStamp = sliceData.timeStamp
        #             self.subTag["2minMaxMinLong"].endPrice = self.__data.getLastContent().bidPrice[0]
        #             self.subTag["2minMaxMinLong"].endMidPrice = self.__midPrice.getLastContent()
        #             self.subTag["2minMaxMinLong"].finished = True
        #         else:
        #             self.subTag["2minMaxMinLong"].returnRate = [0, 0, 0]
        #             self.subTag["2minMaxMinLong"].endTimeStamp = sliceData.timeStamp
        #             self.subTag["2minMaxMinLong"].endPrice = self.__data.getLastContent().bidPrice[0]
        #             self.subTag["2minMaxMinLong"].endMidPrice = self.__midPrice.getLastContent()
        #             self.subTag["2minMaxMinLong"].finished = True
        # 
        # # "2minMaxMinShort", 2min做空最高收益率和最大回撤 ，以起始时的买1开仓、卖1平仓计算
        # if len(self.__emaMidPrice.getContent()) > 0 and len(self.__orderPressure.getContent()) > 0 and (
        #         not self.subTag["2minMaxMinShort"].finished):
        #     timeElapsed = TimeElapsed(sliceData.timeStamp, self.subTag["2minMaxMinShort"].startTimeStamp)
        #     # 如开仓价是跌停价——应当不能卖出，则收益率直接赋为0，并结束
        #     if self.subTag["2minMaxMinShort"].startPrice == 0:
        #         self.subTag["2minMaxMinShort"].returnRate = [0, 0, 0]
        #         self.subTag["2minMaxMinShort"].endTimeStamp = sliceData.timeStamp
        #         self.subTag["2minMaxMinShort"].endPrice = self.__data.getLastContent().askPrice[0]
        #         self.subTag["2minMaxMinShort"].endMidPrice = self.__midPrice.getLastContent()
        #         self.subTag["2minMaxMinShort"].finished = True
        #     # 如时间超过120秒，或初始化时遇到最后一个tick的切片
        #     if timeElapsed >= 120 or sliceData.isLastSlice:
        #         if self.subTag["2minMaxMinShort"].startPrice > 0 and self.__ask1PriceList.__len__() > 0:
        #             self.subTag["2minMaxMinShort"].returnRate[0] = min(self.__ask1PriceList) / self.subTag[
        #                 "2minMaxMinShort"].startPrice - 1  # 区间中，相对于开仓点的最大跌幅
        #             self.subTag["2minMaxMinShort"].returnRate[1] = max(self.__ask1PriceList) / self.subTag[
        #                 "2minMaxMinShort"].startPrice - 1  # 区间中，相对于开仓点的最大涨幅
        #             # 接下来计算“从开仓点到最低价的路径中，相对于开仓点的最大回撤”
        #             # 如相对于开仓点的最大跌幅>=0，则做空的“最低点”无意义，这时令最大回撤为0
        #             if self.subTag["2minMaxMinShort"].returnRate[0] >= 0:
        #                 self.subTag["2minMaxMinShort"].returnRate[2] = 0
        #             else:
        #                 # 找到最低价的位置（如有重复为第1个值）
        #                 minIndex = self.__ask1PriceList.index(min(self.__ask1PriceList))
        #                 if minIndex > 1:
        #                     # 从开仓点到最低价之间，找到最高点的索引
        #                     drawbackIndex = self.__ask1PriceList[:minIndex + 1].index(
        #                         max(self.__ask1PriceList[:minIndex + 1]))
        #                     # 计算“从开仓点到最低价之间的最高点”相对开仓点的收益率，如为正则是最大回撤，否则为0
        #                     self.subTag["2minMaxMinShort"].returnRate[2] = max(0, self.__ask1PriceList[
        #                         drawbackIndex] / self.subTag["2minMaxMinShort"].startPrice - 1)
        #                 else:
        #                     self.subTag["2minMaxMinShort"].returnRate[2] = 0
        #             self.subTag["2minMaxMinShort"].endTimeStamp = sliceData.timeStamp
        #             self.subTag["2minMaxMinShort"].endPrice = self.__data.getLastContent().askPrice[0]
        #             self.subTag["2minMaxMinShort"].endMidPrice = self.__midPrice.getLastContent()
        #             self.subTag["2minMaxMinShort"].finished = True
        #         else:
        #             self.subTag["2minMaxMinShort"].returnRate = [0, 0, 0]
        #             self.subTag["2minMaxMinShort"].endTimeStamp = sliceData.timeStamp
        #             self.subTag["2minMaxMinShort"].endPrice = self.__data.getLastContent().askPrice[0]
        #             self.subTag["2minMaxMinShort"].endMidPrice = self.__midPrice.getLastContent()
        #             self.subTag["2minMaxMinShort"].finished = True
        # 
        # # "2minRR -- Reward and Risk
        # if len(self.__emaMidPrice.getContent()) > 0 and len(self.__orderPressure.getContent()) > 0 and (
        #         not self.subTag["2minRR"].finished):
        #     if self.subTag["2minMaxMinLong"].finished and self.subTag["2minMaxMinShort"].finished:
        #         self.subTag["2minRR"].returnRate[0] = self.subTag["2minMaxMinLong"].returnRate[0]
        #         self.subTag["2minRR"].returnRate[1] = self.subTag["2minMaxMinLong"].returnRate[2]
        #         self.subTag["2minRR"].returnRate[2] = self.subTag["2minMaxMinShort"].returnRate[0]
        #         self.subTag["2minRR"].returnRate[3] = self.subTag["2minMaxMinShort"].returnRate[2]
        #         self.subTag["2minRR"].endTimeStamp = sliceData.timeStamp
        #         self.subTag["2minRR"].endPrice = self.__midPrice.getLastContent()
        #         self.subTag["2minRR"].endMidPrice = self.__midPrice.getLastContent()
        #         self.subTag["2minRR"].finished = True
        # 
        # # 1minLongAB -- 以Ask1开，Bid1平
        # if len(self.__emaMidPrice.getContent()) > 0 and len(self.__orderPressure.getContent()) > 0 and (
        #         not self.subTag["1minLongAB"].finished):
        #     timeElapsed = TimeElapsed(sliceData.timeStamp, self.subTag["1minLongAB"].startTimeStamp)
        #     # 如开仓价是涨停价——应当不能买入，则收益率直接赋为0，并结束
        #     if self.subTag["1minLongAB"].startPrice == 0:
        #         self.subTag["1minLongAB"].returnRate = 0
        #         self.subTag["1minLongAB"].endTimeStamp = sliceData.timeStamp
        #         self.subTag["1minLongAB"].endPrice = 0
        #         self.subTag["1minLongAB"].endMidPrice = self.__midPrice.getLastContent()
        #         self.subTag["1minLongAB"].finished = True
        #     # 如时间超过60秒，或初始化时遇到最后一个tick的切片
        #     if timeElapsed >= 60 or sliceData.isLastSlice:
        #         self.subTag["1minLongAB"].endTimeStamp = sliceData.timeStamp
        #         self.subTag["1minLongAB"].endPrice = self.__data.getLastContent().bidPrice[0]
        #         self.subTag["1minLongAB"].returnRate = self.subTag["1minLongAB"].endPrice / self.subTag[
        #             "1minLongAB"].startPrice - 1
        #         self.subTag["1minLongAB"].endMidPrice = self.__midPrice.getLastContent()
        #         self.subTag["1minLongAB"].finished = True
        # 
        # # 1minShortBA -- 以Bid1开，Ask1平
        # if len(self.__emaMidPrice.getContent()) > 0 and len(self.__orderPressure.getContent()) > 0 and (
        #         not self.subTag["1minShortBA"].finished):
        #     timeElapsed = TimeElapsed(sliceData.timeStamp, self.subTag["1minShortBA"].startTimeStamp)
        #     # 如开仓价是涨停价——应当不能买入，则收益率直接赋为0，并结束
        #     if self.subTag["1minShortBA"].startPrice == 0:
        #         self.subTag["1minShortBA"].returnRate = 0
        #         self.subTag["1minShortBA"].endTimeStamp = sliceData.timeStamp
        #         self.subTag["1minShortBA"].endPrice = 0
        #         self.subTag["1minShortBA"].endMidPrice = self.__midPrice.getLastContent()
        #         self.subTag["1minShortBA"].finished = True
        #     # 如时间超过60秒，或初始化时遇到最后一个tick的切片
        #     if timeElapsed >= 60 or sliceData.isLastSlice:
        #         self.subTag["1minShortBA"].endTimeStamp = sliceData.timeStamp
        #         self.subTag["1minShortBA"].endPrice = self.__data.getLastContent().askPrice[0]
        #         self.subTag["1minShortBA"].returnRate = self.subTag["1minShortBA"].endPrice / self.subTag[
        #             "1minShortBA"].startPrice - 1
        #         self.subTag["1minShortBA"].endMidPrice = self.__midPrice.getLastContent()
        #         self.subTag["1minShortBA"].finished = True
        # 
        # # 2minLongAB -- 以Ask1开，Bid1平
        # if len(self.__emaMidPrice.getContent()) > 0 and len(self.__orderPressure.getContent()) > 0 and (
        #         not self.subTag["2minLongAB"].finished):
        #     timeElapsed = TimeElapsed(sliceData.timeStamp, self.subTag["2minLongAB"].startTimeStamp)
        #     # 如开仓价是涨停价——应当不能买入，则收益率直接赋为0，并结束
        #     if self.subTag["2minLongAB"].startPrice == 0:
        #         self.subTag["2minLongAB"].returnRate = 0
        #         self.subTag["2minLongAB"].endTimeStamp = sliceData.timeStamp
        #         self.subTag["2minLongAB"].endPrice = 0
        #         self.subTag["2minLongAB"].endMidPrice = self.__midPrice.getLastContent()
        #         self.subTag["2minLongAB"].finished = True
        #     # 如时间超过120秒，或初始化时遇到最后一个tick的切片
        #     if timeElapsed >= 120 or sliceData.isLastSlice:
        #         self.subTag["2minLongAB"].endTimeStamp = sliceData.timeStamp
        #         self.subTag["2minLongAB"].endPrice = self.__data.getLastContent().bidPrice[0]
        #         self.subTag["2minLongAB"].returnRate = self.subTag["2minLongAB"].endPrice / self.subTag[
        #             "2minLongAB"].startPrice - 1
        #         self.subTag["2minLongAB"].endMidPrice = self.__midPrice.getLastContent()
        #         self.subTag["2minLongAB"].finished = True
        # 
        # # 2minShortBA -- 以Bid1开，Ask1平
        # if len(self.__emaMidPrice.getContent()) > 0 and len(self.__orderPressure.getContent()) > 0 and (
        #         not self.subTag["2minShortBA"].finished):
        #     timeElapsed = TimeElapsed(sliceData.timeStamp, self.subTag["2minShortBA"].startTimeStamp)
        #     # 如开仓价是涨停价——应当不能买入，则收益率直接赋为0，并结束
        #     if self.subTag["2minShortBA"].startPrice == 0:
        #         self.subTag["2minShortBA"].returnRate = 0
        #         self.subTag["2minShortBA"].endTimeStamp = sliceData.timeStamp
        #         self.subTag["2minShortBA"].endPrice = 0
        #         self.subTag["2minShortBA"].endMidPrice = self.__midPrice.getLastContent()
        #         self.subTag["2minShortBA"].finished = True
        #     # 如时间超过120秒，或初始化时遇到最后一个tick的切片
        #     if timeElapsed >= 120 or sliceData.isLastSlice:
        #         self.subTag["2minShortBA"].endTimeStamp = sliceData.timeStamp
        #         self.subTag["2minShortBA"].endPrice = self.__data.getLastContent().askPrice[0]
        #         self.subTag["2minShortBA"].returnRate = self.subTag["2minShortBA"].endPrice / self.subTag[
        #             "2minShortBA"].startPrice - 1
        #         self.subTag["2minShortBA"].endMidPrice = self.__midPrice.getLastContent()
        #         self.subTag["2minShortBA"].finished = True
        # 
        # # 1minLongAVWAP -- 以Ask1开，VWAP平
        # if len(self.__emaMidPrice.getContent()) > 0 and len(self.__orderPressure.getContent()) > 0 and (
        #         not self.subTag["1minLongAVWAP"].finished):
        #     timeElapsed = TimeElapsed(sliceData.timeStamp, self.subTag["1minLongAVWAP"].startTimeStamp)
        #     # 如开仓价是涨停价——应当不能买入，则收益率直接赋为0，并结束
        #     if self.subTag["1minLongAVWAP"].startPrice == 0:
        #         self.subTag["1minLongAVWAP"].returnRate = 0
        #         self.subTag["1minLongAVWAP"].endTimeStamp = sliceData.timeStamp
        #         self.subTag["1minLongAVWAP"].endPrice = 0
        #         self.subTag["1minLongAVWAP"].endMidPrice = self.__midPrice.getLastContent()
        #         self.subTag["1minLongAVWAP"].finished = True
        #     # 如时间超过60秒，或初始化时遇到最后一个tick的切片
        #     if timeElapsed >= 60 or sliceData.isLastSlice:
        #         self.subTag["1minLongAVWAP"].endTimeStamp = sliceData.timeStamp
        #         if sum(self.__volumeList) > 0:
        #             self.subTag["1minLongAVWAP"].endPrice = sum(self.__amountList) / sum(self.__volumeList)
        #             self.subTag["1minLongAVWAP"].returnRate = self.subTag["1minLongAVWAP"].endPrice / self.subTag[
        #                 "1minLongAVWAP"].startPrice - 1
        #         else:
        #             self.subTag["1minLongAVWAP"].endPrice = 0
        #             self.subTag["1minLongAVWAP"].returnRate = 0
        #         self.subTag["1minLongAVWAP"].endMidPrice = self.__midPrice.getLastContent()
        #         self.subTag["1minLongAVWAP"].finished = True
        # 
        # # 1minShortBVWAP -- 以Bid1开，VWAP平
        # if len(self.__emaMidPrice.getContent()) > 0 and len(self.__orderPressure.getContent()) > 0 and (
        #         not self.subTag["1minShortBVWAP"].finished):
        #     timeElapsed = TimeElapsed(sliceData.timeStamp, self.subTag["1minShortBVWAP"].startTimeStamp)
        #     # 如开仓价是涨停价——应当不能买入，则收益率直接赋为0，并结束
        #     if self.subTag["1minShortBVWAP"].startPrice == 0:
        #         self.subTag["1minShortBVWAP"].returnRate = 0
        #         self.subTag["1minShortBVWAP"].endTimeStamp = sliceData.timeStamp
        #         self.subTag["1minShortBVWAP"].endPrice = 0
        #         self.subTag["1minShortBVWAP"].endMidPrice = self.__midPrice.getLastContent()
        #         self.subTag["1minShortBVWAP"].finished = True
        #     # 如时间超过60秒，或初始化时遇到最后一个tick的切片
        #     if timeElapsed >= 60 or sliceData.isLastSlice:
        #         self.subTag["1minShortBVWAP"].endTimeStamp = sliceData.timeStamp
        #         if sum(self.__volumeList) > 0:
        #             self.subTag["1minShortBVWAP"].endPrice = sum(self.__amountList) / sum(self.__volumeList)
        #             self.subTag["1minShortBVWAP"].returnRate = self.subTag["1minShortBVWAP"].endPrice / self.subTag[
        #                 "1minShortBVWAP"].startPrice - 1
        #         else:
        #             self.subTag["1minShortBVWAP"].endPrice = 0
        #             self.subTag["1minShortBVWAP"].returnRate = 0
        #         self.subTag["1minShortBVWAP"].endMidPrice = self.__midPrice.getLastContent()
        #         self.subTag["1minShortBVWAP"].finished = True
        # 
        # # 2minLongAVWAP -- 以Ask1开，VWAP平
        # if len(self.__emaMidPrice.getContent()) > 0 and len(self.__orderPressure.getContent()) > 0 and (
        #         not self.subTag["2minLongAVWAP"].finished):
        #     timeElapsed = TimeElapsed(sliceData.timeStamp, self.subTag["2minLongAVWAP"].startTimeStamp)
        #     # 如开仓价是涨停价——应当不能买入，则收益率直接赋为0，并结束
        #     if self.subTag["2minLongAVWAP"].startPrice == 0:
        #         self.subTag["2minLongAVWAP"].returnRate = 0
        #         self.subTag["2minLongAVWAP"].endTimeStamp = sliceData.timeStamp
        #         self.subTag["2minLongAVWAP"].endPrice = 0
        #         self.subTag["2minLongAVWAP"].endMidPrice = self.__midPrice.getLastContent()
        #         self.subTag["2minLongAVWAP"].finished = True
        #     # 如时间超过120秒，或初始化时遇到最后一个tick的切片
        #     if timeElapsed >= 120 or sliceData.isLastSlice:
        #         self.subTag["2minLongAVWAP"].endTimeStamp = sliceData.timeStamp
        #         if sum(self.__volumeList) > 0:
        #             self.subTag["2minLongAVWAP"].endPrice = sum(self.__amountList) / sum(self.__volumeList)
        #             self.subTag["2minLongAVWAP"].returnRate = self.subTag["2minLongAVWAP"].endPrice / self.subTag[
        #                 "2minLongAVWAP"].startPrice - 1
        #         else:
        #             self.subTag["2minLongAVWAP"].endPrice = 0
        #             self.subTag["2minLongAVWAP"].returnRate = 0
        #         self.subTag["2minLongAVWAP"].endMidPrice = self.__midPrice.getLastContent()
        #         self.subTag["2minLongAVWAP"].finished = True
        # 
        # # 2minShortBVWAP -- 以Bid1开，VWAP平
        # if len(self.__emaMidPrice.getContent()) > 0 and len(self.__orderPressure.getContent()) > 0 and (
        #         not self.subTag["2minShortBVWAP"].finished):
        #     timeElapsed = TimeElapsed(sliceData.timeStamp, self.subTag["2minShortBVWAP"].startTimeStamp)
        #     # 如开仓价是涨停价——应当不能买入，则收益率直接赋为0，并结束
        #     if self.subTag["2minShortBVWAP"].startPrice == 0:
        #         self.subTag["2minShortBVWAP"].returnRate = 0
        #         self.subTag["2minShortBVWAP"].endTimeStamp = sliceData.timeStamp
        #         self.subTag["2minShortBVWAP"].endPrice = 0
        #         self.subTag["2minShortBVWAP"].endMidPrice = self.__midPrice.getLastContent()
        #         self.subTag["2minShortBVWAP"].finished = True
        #     # 如时间超过120秒，或初始化时遇到最后一个tick的切片
        #     if timeElapsed >= 120 or sliceData.isLastSlice:
        #         self.subTag["2minShortBVWAP"].endTimeStamp = sliceData.timeStamp
        #         if sum(self.__volumeList) > 0:
        #             self.subTag["2minShortBVWAP"].endPrice = sum(self.__amountList) / sum(self.__volumeList)
        #             self.subTag["2minShortBVWAP"].returnRate = self.subTag["2minShortBVWAP"].endPrice / self.subTag[
        #                 "2minShortBVWAP"].startPrice - 1
        #         else:
        #             self.subTag["2minShortBVWAP"].endPrice = 0
        #             self.subTag["2minShortBVWAP"].returnRate = 0
        #         self.subTag["2minShortBVWAP"].endMidPrice = self.__midPrice.getLastContent()
        #         self.subTag["2minShortBVWAP"].finished = True

        # # "价差"，subTag的result是一个list，长度为3(判断长度可以修改)，依次是随后3个切片的价差（单位:元）
        # if len(self.__emaMidPrice.getContent()) > 0 and (not self.subTag["BASpread"].finished):
        #     self.subTag["BASpread"].endTimeStamp.append(sliceData.timeStamp)
        #     if sliceData.bidPrice[0] != 0 and sliceData.askPrice[0] != 0:
        #         self.subTag["BASpread"].returnRate[len(self.subTag["BASpread"].endTimeStamp) - 1] = \
        #             sliceData.askPrice[0] - sliceData.bidPrice[0]
        #     if len(self.subTag["BASpread"].endTimeStamp) >= 3 or sliceData.isLastSlice:
        #         self.subTag["BASpread"].finished = True
        #
        # # "百分比价差"，subTag的result是一个list，长度为3，依次是随后3个切片的相对于当前切片中间价的价差（单位:%）
        # if len(self.__emaMidPrice.getContent()) > 0 and (not self.subTag["BASpreadPercent"].finished):
        #     self.subTag["BASpreadPercent"].endTimeStamp.append(sliceData.timeStamp)
        #     if sliceData.bidPrice[0] != 0 and sliceData.askPrice[0] != 0:
        #         self.subTag["BASpreadPercent"].returnRate[len(self.subTag["BASpreadPercent"].endTimeStamp) - 1] = \
        #             (sliceData.askPrice[0] - sliceData.bidPrice[0]) / self.subTag["BASpreadPercent"].startPrice * 100
        #     if len(self.subTag["BASpreadPercent"].endTimeStamp) >= 3 or sliceData.isLastSlice:
        #         self.subTag["BASpreadPercent"].finished = True

        # 所有子标签完成计算后Tag才算完成
        self.finished = True
        for key in self.subTag:
            if not self.subTag[key].finished:
                self.finished = False
                break


class SubTag:
    def __init__(self, data, midPrice, sliceData, bidOrAsk, position, adjust, resultType="scalar", seqLen=10):
        # resultType 如为"scalar"，则returnRate初值赋为0、endPrice赋为None；
        # resultType 如为"list"则returnRate初始化为长度为seq的list，内容全是0；endPrice, endTimeStamp 和 endSliceData初始化为[]
        if len(data.getContent()) > 0 and (not sliceData.isLastSlice):
            self.startTimeStamp = sliceData.timeStamp
            self.startMidPrice = midPrice.getLastContent()
            self.startSliceData = data.getLastContent()
            self.code = data.getLastContent().code
            if bidOrAsk == "ask":
                if data.getLastContent().askPrice[position - 1] != 0:
                    self.startPrice = data.getLastContent().askPrice[position - 1] + adjust
                else:
                    self.startPrice = midPrice.getLastContent()
            elif bidOrAsk == "bid":
                if data.getLastContent().bidPrice[position - 1] != 0:
                    self.startPrice = data.getLastContent().bidPrice[position - 1] + adjust
                else:
                    self.startPrice = midPrice.getLastContent()
            elif bidOrAsk == "mid":
                self.startPrice = midPrice.getLastContent() + adjust
            elif bidOrAsk == "ask1":
                self.startPrice = data.getLastContent().askPrice[position - 1] + adjust
            elif bidOrAsk == "bid1":
                self.startPrice = data.getLastContent().bidPrice[position - 1] + adjust
            if resultType == "scalar":
                self.endPrice = None
                self.endMidPrice = None
                self.returnRate = 0
                self.endTimeStamp = None
            elif resultType == "list":
                self.endPrice = []
                self.endMidPrice = []
                self.returnRate = [0] * seqLen
                self.endTimeStamp = []
            elif resultType == "scalar2":
                self.endPrice = None
                self.endMidPrice = None
                self.returnRate = None
                self.endTimeStamp = None
            elif resultType == "list2":
                self.endPrice = []
                self.endMidPrice = []
                self.returnRate = [None] * seqLen
                self.endTimeStamp = []
            self.finished = False
        elif len(data.getContent()) > 0 and sliceData.isLastSlice:  # 刚初始化就遇到最后一个切片
            self.startTimeStamp = sliceData.timeStamp
            self.endTimeStamp = sliceData.timeStamp
            self.startMidPrice = midPrice.getLastContent()
            self.startSliceData = data.getLastContent()
            self.code = data.getLastContent().code
            self.startPrice = midPrice.getLastContent()
            if resultType == "scalar" or resultType == "scalar2":
                self.returnRate = 0
                self.endPrice = midPrice.getLastContent()
                self.endMidPrice = midPrice.getLastContent()
                self.endTimeStamp = None
            elif resultType == "list":
                self.returnRate = [0] * seqLen
                self.endPrice = []
                self.endMidPrice = midPrice.getLastContent()
                self.endTimeStamp = []
            elif resultType == "list2":
                self.endPrice = []
                self.endMidPrice = midPrice.getLastContent()
                self.returnRate = [None] * seqLen
                self.endTimeStamp = []
            self.finished = True
        else:
            self.startTimeStamp = sliceData.timeStamp
            self.endTimeStamp = sliceData.timeStamp
            self.startMidPrice = midPrice.getLastContent()
            self.startSliceData = None
            self.code = None
            self.startPrice = None
            if resultType == "scalar" or resultType == "scalar2":
                self.returnRate = 0
                self.endPrice = None
                self.endMidPrice = None
                self.endTimeStamp = None
            elif resultType == "list":
                self.returnRate = [0] * seqLen
                self.endPrice = []
                self.endMidPrice = []
                self.endTimeStamp = []
            elif resultType == "list2":
                self.endPrice = []
                self.endMidPrice = []
                self.returnRate = [None] * seqLen
                self.endTimeStamp = []
            self.finished = True


def TimeElapsed(time1, time2):  # 输入时间time1和time2 （都为timestamp），其中time2时间早于time1，返回两者之间的差（单位是秒）
    hour1 = datetime.fromtimestamp(time1).hour  # 目前的小时
    hour2 = datetime.fromtimestamp(time2).hour  # 起始时间的小时
    if (hour1 <= 11 and hour2 <= 11) or (hour1 >= 13 and hour2 >= 13):  # 如跨中午，则需另外计算
        timeElapsed = time1 - time2
    else:
        timeElapsed = time1 - time2 - 5400
    return timeElapsed
