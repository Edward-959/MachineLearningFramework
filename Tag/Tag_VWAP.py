# -*- coding: utf-8 -*-
"""
updated: 2018/7/11 & 7/12  删除endSliceData; 将startSliceData中的逐笔成交信息设为[]，以减小内存占用
updated: 2018/7/17 测试版，仅保留1minLongAVWAP, 1minShortBVWAP, 及2min, 5min版共6个标签
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
        self.subTag.update({"1minLongAVWAP": SubTag(self.__data, self.__midPrice, sliceData, "ask1", 1, 0)})
        self.subTag.update({"1minShortBVWAP": SubTag(self.__data, self.__midPrice, sliceData, "bid1", 1, 0)})
        self.subTag.update({"2minLongAVWAP": SubTag(self.__data, self.__midPrice, sliceData, "ask1", 1, 0)})
        self.subTag.update({"2minShortBVWAP": SubTag(self.__data, self.__midPrice, sliceData, "bid1", 1, 0)})
        self.subTag.update({"5minLongAVWAP": SubTag(self.__data, self.__midPrice, sliceData, "ask1", 1, 0)})
        self.subTag.update({"5minShortBVWAP": SubTag(self.__data, self.__midPrice, sliceData, "bid1", 1, 0)})

        self.finished = False
        if sliceData.isLastSlice:
            self.finished = True
        # 需要用到的中间变量
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

        # 1minLongAVWAP -- 以Ask1开，VWAP平
        if len(self.__emaMidPrice.getContent()) > 0 and len(self.__orderPressure.getContent()) > 0 and (
                not self.subTag["1minLongAVWAP"].finished):
            timeElapsed = TimeElapsed(sliceData.timeStamp, self.subTag["1minLongAVWAP"].startTimeStamp)
            # 如开仓价是涨停价——应当不能买入，则收益率直接赋为0，并结束
            if self.subTag["1minLongAVWAP"].startPrice == 0:
                self.subTag["1minLongAVWAP"].returnRate = 0
                self.subTag["1minLongAVWAP"].endTimeStamp = sliceData.timeStamp
                self.subTag["1minLongAVWAP"].endPrice = 0
                self.subTag["1minLongAVWAP"].endMidPrice = self.__midPrice.getLastContent()
                self.subTag["1minLongAVWAP"].finished = True
            # 如时间超过60秒，或初始化时遇到最后一个tick的切片
            if timeElapsed >= 60 or sliceData.isLastSlice:
                self.subTag["1minLongAVWAP"].endTimeStamp = sliceData.timeStamp
                if sum(self.__volumeList) > 0:
                    self.subTag["1minLongAVWAP"].endPrice = sum(self.__amountList) / sum(self.__volumeList)
                    self.subTag["1minLongAVWAP"].returnRate = self.subTag["1minLongAVWAP"].endPrice / self.subTag[
                        "1minLongAVWAP"].startPrice - 1
                else:
                    self.subTag["1minLongAVWAP"].endPrice = 0
                    self.subTag["1minLongAVWAP"].returnRate = 0
                self.subTag["1minLongAVWAP"].endMidPrice = self.__midPrice.getLastContent()
                self.subTag["1minLongAVWAP"].finished = True

        # 1minShortBVWAP -- 以Bid1开，VWAP平
        if len(self.__emaMidPrice.getContent()) > 0 and len(self.__orderPressure.getContent()) > 0 and (
                not self.subTag["1minShortBVWAP"].finished):
            timeElapsed = TimeElapsed(sliceData.timeStamp, self.subTag["1minShortBVWAP"].startTimeStamp)
            # 如开仓价是涨停价——应当不能买入，则收益率直接赋为0，并结束
            if self.subTag["1minShortBVWAP"].startPrice == 0:
                self.subTag["1minShortBVWAP"].returnRate = 0
                self.subTag["1minShortBVWAP"].endTimeStamp = sliceData.timeStamp
                self.subTag["1minShortBVWAP"].endPrice = 0
                self.subTag["1minShortBVWAP"].endMidPrice = self.__midPrice.getLastContent()
                self.subTag["1minShortBVWAP"].finished = True
            # 如时间超过60秒，或初始化时遇到最后一个tick的切片
            if timeElapsed >= 60 or sliceData.isLastSlice:
                self.subTag["1minShortBVWAP"].endTimeStamp = sliceData.timeStamp
                if sum(self.__volumeList) > 0:
                    self.subTag["1minShortBVWAP"].endPrice = sum(self.__amountList) / sum(self.__volumeList)
                    self.subTag["1minShortBVWAP"].returnRate = self.subTag["1minShortBVWAP"].endPrice / self.subTag[
                        "1minShortBVWAP"].startPrice - 1
                else:
                    self.subTag["1minShortBVWAP"].endPrice = 0
                    self.subTag["1minShortBVWAP"].returnRate = 0
                self.subTag["1minShortBVWAP"].endMidPrice = self.__midPrice.getLastContent()
                self.subTag["1minShortBVWAP"].finished = True

        # 2minLongAVWAP -- 以Ask1开，VWAP平
        if len(self.__emaMidPrice.getContent()) > 0 and len(self.__orderPressure.getContent()) > 0 and (
                not self.subTag["2minLongAVWAP"].finished):
            timeElapsed = TimeElapsed(sliceData.timeStamp, self.subTag["2minLongAVWAP"].startTimeStamp)
            # 如开仓价是涨停价——应当不能买入，则收益率直接赋为0，并结束
            if self.subTag["2minLongAVWAP"].startPrice == 0:
                self.subTag["2minLongAVWAP"].returnRate = 0
                self.subTag["2minLongAVWAP"].endTimeStamp = sliceData.timeStamp
                self.subTag["2minLongAVWAP"].endPrice = 0
                self.subTag["2minLongAVWAP"].endMidPrice = self.__midPrice.getLastContent()
                self.subTag["2minLongAVWAP"].finished = True
            # 如时间超过120秒，或初始化时遇到最后一个tick的切片
            if timeElapsed >= 120 or sliceData.isLastSlice:
                self.subTag["2minLongAVWAP"].endTimeStamp = sliceData.timeStamp
                if sum(self.__volumeList) > 0:
                    self.subTag["2minLongAVWAP"].endPrice = sum(self.__amountList) / sum(self.__volumeList)
                    self.subTag["2minLongAVWAP"].returnRate = self.subTag["2minLongAVWAP"].endPrice / self.subTag[
                        "2minLongAVWAP"].startPrice - 1
                else:
                    self.subTag["2minLongAVWAP"].endPrice = 0
                    self.subTag["2minLongAVWAP"].returnRate = 0
                self.subTag["2minLongAVWAP"].endMidPrice = self.__midPrice.getLastContent()
                self.subTag["2minLongAVWAP"].finished = True

        # 2minShortBVWAP -- 以Bid1开，VWAP平
        if len(self.__emaMidPrice.getContent()) > 0 and len(self.__orderPressure.getContent()) > 0 and (
                not self.subTag["2minShortBVWAP"].finished):
            timeElapsed = TimeElapsed(sliceData.timeStamp, self.subTag["2minShortBVWAP"].startTimeStamp)
            # 如开仓价是涨停价——应当不能买入，则收益率直接赋为0，并结束
            if self.subTag["2minShortBVWAP"].startPrice == 0:
                self.subTag["2minShortBVWAP"].returnRate = 0
                self.subTag["2minShortBVWAP"].endTimeStamp = sliceData.timeStamp
                self.subTag["2minShortBVWAP"].endPrice = 0
                self.subTag["2minShortBVWAP"].endMidPrice = self.__midPrice.getLastContent()
                self.subTag["2minShortBVWAP"].finished = True
            # 如时间超过120秒，或初始化时遇到最后一个tick的切片
            if timeElapsed >= 120 or sliceData.isLastSlice:
                self.subTag["2minShortBVWAP"].endTimeStamp = sliceData.timeStamp
                if sum(self.__volumeList) > 0:
                    self.subTag["2minShortBVWAP"].endPrice = sum(self.__amountList) / sum(self.__volumeList)
                    self.subTag["2minShortBVWAP"].returnRate = self.subTag["2minShortBVWAP"].endPrice / self.subTag[
                        "2minShortBVWAP"].startPrice - 1
                else:
                    self.subTag["2minShortBVWAP"].endPrice = 0
                    self.subTag["2minShortBVWAP"].returnRate = 0
                self.subTag["2minShortBVWAP"].endMidPrice = self.__midPrice.getLastContent()
                self.subTag["2minShortBVWAP"].finished = True

        # 5minLongAVWAP -- 以Ask1开，VWAP平
        if len(self.__emaMidPrice.getContent()) > 0 and len(self.__orderPressure.getContent()) > 0 and (
                not self.subTag["5minLongAVWAP"].finished):
            timeElapsed = TimeElapsed(sliceData.timeStamp, self.subTag["5minLongAVWAP"].startTimeStamp)
            # 如开仓价是涨停价——应当不能买入，则收益率直接赋为0，并结束
            if self.subTag["5minLongAVWAP"].startPrice == 0:
                self.subTag["5minLongAVWAP"].returnRate = 0
                self.subTag["5minLongAVWAP"].endTimeStamp = sliceData.timeStamp
                self.subTag["5minLongAVWAP"].endPrice = 0
                self.subTag["5minLongAVWAP"].endMidPrice = self.__midPrice.getLastContent()
                self.subTag["5minLongAVWAP"].finished = True
            # 如时间超过600秒，或初始化时遇到最后一个tick的切片
            if timeElapsed >= 600 or sliceData.isLastSlice:
                self.subTag["5minLongAVWAP"].endTimeStamp = sliceData.timeStamp
                if sum(self.__volumeList) > 0:
                    self.subTag["5minLongAVWAP"].endPrice = sum(self.__amountList) / sum(self.__volumeList)
                    self.subTag["5minLongAVWAP"].returnRate = self.subTag["5minLongAVWAP"].endPrice / self.subTag[
                        "5minLongAVWAP"].startPrice - 1
                else:
                    self.subTag["5minLongAVWAP"].endPrice = 0
                    self.subTag["5minLongAVWAP"].returnRate = 0
                self.subTag["5minLongAVWAP"].endMidPrice = self.__midPrice.getLastContent()
                self.subTag["5minLongAVWAP"].finished = True

        # 5minShortBVWAP -- 以Bid1开，VWAP平
        if len(self.__emaMidPrice.getContent()) > 0 and len(self.__orderPressure.getContent()) > 0 and (
                not self.subTag["5minShortBVWAP"].finished):
            timeElapsed = TimeElapsed(sliceData.timeStamp, self.subTag["5minShortBVWAP"].startTimeStamp)
            # 如开仓价是涨停价——应当不能买入，则收益率直接赋为0，并结束
            if self.subTag["5minShortBVWAP"].startPrice == 0:
                self.subTag["5minShortBVWAP"].returnRate = 0
                self.subTag["5minShortBVWAP"].endTimeStamp = sliceData.timeStamp
                self.subTag["5minShortBVWAP"].endPrice = 0
                self.subTag["5minShortBVWAP"].endMidPrice = self.__midPrice.getLastContent()
                self.subTag["5minShortBVWAP"].finished = True
            # 如时间超过600秒，或初始化时遇到最后一个tick的切片
            if timeElapsed >= 600 or sliceData.isLastSlice:
                self.subTag["5minShortBVWAP"].endTimeStamp = sliceData.timeStamp
                if sum(self.__volumeList) > 0:
                    self.subTag["5minShortBVWAP"].endPrice = sum(self.__amountList) / sum(self.__volumeList)
                    self.subTag["5minShortBVWAP"].returnRate = self.subTag["5minShortBVWAP"].endPrice / self.subTag[
                        "5minShortBVWAP"].startPrice - 1
                else:
                    self.subTag["5minShortBVWAP"].endPrice = 0
                    self.subTag["5minShortBVWAP"].returnRate = 0
                self.subTag["5minShortBVWAP"].endMidPrice = self.__midPrice.getLastContent()
                self.subTag["5minShortBVWAP"].finished = True



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
