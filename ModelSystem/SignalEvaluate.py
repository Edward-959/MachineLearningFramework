# -*- coding: utf-8 -*-
"""
Created on 2017/9/26 13:19

@author: 006547
@revise: 006688

@revise: 011478
on 20180706: 修复了加仓下单数量的逻辑bug，修改了calQty
on 20180713: 加入了最大单边总金额暴露风控参数，通过mockTradePara传入。如果字典中不含有该参数，则默认没有该风控。
on 20180726: 加入onNewTick方法，确保每个tick都会执行该方法，以便更新tick信息
on 20180727: 加入了START_OPEN_TIME和LAST_OPEN_TIME，从而确定开仓时间。超过禁止开仓时间，若有头寸，则会等待自然平仓。
on 20180727: 改变了SignalExecutorBase，现在能获取positionMgr的持仓和订单信息。并且tickData也会传入Executor，其可能为None，请自行处理异常
on 20180727: 优化了输出的统计计算，多空反转的开平仓收益、收益率计算更准确。
on 20180801: 修改了下单数量风控：
             1. 如果executor返回了price和volume：则最大单边上限为maxExposure，流动性乘数不再有效。下单数量被单笔最大委托金额上限控制。其他为可买可卖额度控制。
             2. 如果executor返回了True or False: 则最大单边上限为maxExposure和maAmount * 流动性乘数的最小值。下单数量被单笔最大委托金额上限、持仓额度比例控制。其他为可买可卖额度控制。
on 20180802: 修复了如果executor返回price和volume，遇到止损可能会造成price和volume不更新的问题
on 20180802: 增加了多空翻转的处理：如果executor返回了price和volume，则可以根据volume进行多空操作，请在executor里自行处理好逻辑。优化RiskManager的多空翻转的成本计算。
on 20180830: * 为ExchangeHouse修复了上午发出的订单同时要在下午drive撮合时，必须加入中午时间的不一致：see def __timeSpan
on 20180910: 支持了OutputManager里的多空翻转拆单；加入了股票涨跌幅达到9.5%时禁止开仓，达到9.8%时按净头寸全部平仓的优化
"""
import datetime as dt
import json
import os
import sys
import importlib
# import matplotlib.pyplot as plt
from enum import Enum
import math
import numpy as np

from ModelSystem.Util.PositionManager import PositionManager
from ModelSystem.Util.OutputManager import OutputManager
from ModelSystem.Util.RiskManager import RiskManager
from ModelSystem.Util.OrderSide import OrderSide
from ExchangeHouse.ExchangeHouse import ExchangeHouse
from ExchangeHouse.ExchangeOrder import ExchangeOrder
from ExchangeHouse.Data.Data import Data
from ExchangeHouse.Order import Order
from ModelSystem.Util.ExcelWriter import OutputSpreadSheet


class SignalEvaluate:
    # temporarily use default initialisation
    def __init__(self, signalDataSet, para, mockTradePara, executorStr, absolutePath, tickData=None, transactionData=None):
        # 定义一些常量
        self.__STOP_LOSS = abs(para["maxLose"])  # 止损线参数（不考虑手续费）
        self.__COST_RATE = 0.0012  # 手续费
        self.__NOON = 120000000  # 12:00:00
        self.__MARKET_CLOSE = 145500000  # 14:55:00
        self.__OPEN_FORBIDDEN = 0.095  # 禁止开仓涨跌幅

        self.__backTestUnderlying = signalDataSet.backTestUnderlying()
        self.__tagName = signalDataSet.tagName()
        self.__modelName = signalDataSet.modelName()
        self.__customFactorDict = signalDataSet.customFactorDict()
        self.__factorForSignalDict = signalDataSet.factorForSignalDict()
        self.__tradingUnderlyingCode = signalDataSet.tradingUnderlyingCode()
        self.__outputByWindow = signalDataSet.outputByWindow()
        self.__outputByUnderlying = signalDataSet.outputByUnderlying()

        self.__para = para
        self.__executorStr = executorStr
        self.__absolutePath = absolutePath

        self.__outputMgr = OutputManager(self.__COST_RATE)
        self.__positionManager = PositionManager()
        self.__riskMgr = RiskManager(self.__STOP_LOSS)

        self.__tickData = tickData
        self.__data = Data(self.__tickData, transactionData)
        self.__exchangeHouse = ExchangeHouse(self.__data)
        self.__modules = importlib.import_module('ModelSystem.' + executorStr)  # 通过String来生成的Executor的实例，先import
        self.__signalExecutor = getattr(self.__modules, executorStr)(self.__positionManager, self.__riskMgr)

        self.__START_OPEN_TIME = mockTradePara.get("startOpenTime")  # 从该时刻起，允许开仓。格式为 dt.time(9,30,0)
        if self.__START_OPEN_TIME is None:
            self.__START_OPEN_TIME = dt.time(9, 30, 0)  # 若外部参数没有设置，则默认值为 9:30:00起允许开仓
        self.__LAST_OPEN_TIME = mockTradePara.get("lastOpenTime")  # 从该时刻起，禁止开仓，若有仓位，则会依据信号值自然平仓。格式为 dt.time(9,45,0)
        if self.__LAST_OPEN_TIME is None:
            self.__LAST_OPEN_TIME = dt.time(14, 57, 0)  # 若外部参数没有设置，则默认值为 14:57:00起禁止再开仓

        self.__initAmount = mockTradePara["initAmount"]  # 初始资金
        self.__maxExposure = mockTradePara.get("maxExposure")  # 最大单边总金额暴露，与成交额均值的较小值（get方式，不抛异常）
        self.__maxTurnoverPerOrder = mockTradePara["maxTurnoverPerOrder"]  # 每笔最大委托金额
        self.__maxRatePerOrder = mockTradePara["maxRatePerOrder"]  # 每笔最大委托占比
        self.__maAmountRate = mockTradePara["maAmountRate"]  # 控制总金额暴露的占成交额均值的乘数，与最大单边总金额暴露的较小值
        self.__openWithdrawSeconds = mockTradePara["openWithdrawSeconds"]  # 开仓单驱动时间
        self.__closeWithdrawSeconds = mockTradePara["closeWithdrawSeconds"]  # 平仓单驱动时间，建议始终设为3
        self.__buyLevel = mockTradePara["buyLevel"]  # 1-based index, not 0-based
        self.__sellLevel = mockTradePara["sellLevel"]  # 1-based index, not 0-based
        self.__buyDeviation = mockTradePara["buyDeviation"]
        self.__sellDeviation = mockTradePara["sellDeviation"]
        self.__MIN_ORDER_QTY = mockTradePara["MIN_ORDER_QTY"]

        self.__preTagInfo = {}
        self.__pre_net_position = {}
        self.__orderInfo = {}  # record the order info for each sent order: orderNo, isOpen
        self.__exePriceQty = {}  # the dictionary (key = price, volume) (may be) returned in the signal executor
        self.__noonRange = {}  # the noon range is not a constant value. It may vary.

        self.__funStr = None
        # self.__errorMsg = []  # the list contains the error message, which will be print at the end of the programme

    def evaluate(self, funStr=None, show=True):
        rollingTradingOrder = []
        combineTradingOrder = []
        # model = self.__modelManagement.model[self.__modelName]
        # backTestUnderlying = model.backTestUnderlying
        windowUnderlyingSameIndex = []
        for i in range(len(self.__outputByWindow)):
            rollingTradingOrder.append([])
            # 如果window这层rolling data的长度为1，则和outputByUnderlying的效果一样
            if len(self.__outputByWindow[i]) == 1:
                windowUnderlyingSameIndex.append(i)
                rollingTradingOrder[i].append({})
                continue
            for j in range(len(self.__outputByWindow[i])):
                rollingTradingOrder[i].append({})
                outSamplePredict = self.__outputByWindow[i][j]["outSamplePredict"]
                inSamplePredict = self.__outputByWindow[i][j]["inSamplePredict"]
                outSampleRMSE = self.__outputByWindow[i][j]["outSampleRMSE"]
                numTrainData = self.__outputByWindow[i][j]["numTrainData"]
                outSampleSubTag = self.__outputByWindow[i][j]["outSampleSubTag"]
                # featureScores = model.outputByWindow[i][j]["featureScores"]
                tempRollingTradingOrder = {}
                if funStr is None:
                    tempRollingTradingOrder = self.runBackTest(self.__getSymbolFromModelMgm(i), outSamplePredict, inSamplePredict,
                                                               outSampleSubTag)
                elif funStr == 'signalTag':
                    self.__funStr = funStr
                    tempRollingTradingOrder = self.signalTag(outSamplePredict, inSamplePredict, outSampleSubTag)
                elif funStr == "signalMaxMinTag":
                    self.__funStr = funStr
                    tempRollingTradingOrder = self.signalMaxMinTag(outSamplePredict, inSamplePredict, outSampleSubTag)
                tempRollingTradingOrder.update({"outSampleRMSE": outSampleRMSE})
                tempRollingTradingOrder.update({"numTrainData": numTrainData})
                # tempRollingTradingOrder.update({"featureScores": featureScores})
                self.TradingEvaluate(tempRollingTradingOrder, outSamplePredict, False)
                rollingTradingOrder[i][j].update(tempRollingTradingOrder)

        for i in range(len(self.__outputByUnderlying)):
            combineTradingOrder.append({})
            outSamplePredict = self.__outputByUnderlying[i]["outSamplePredict"]
            inSamplePredict = self.__outputByUnderlying[i]["inSamplePredict"]
            outSampleRMSE = self.__outputByUnderlying[i]["outSampleRMSE"]
            numTrainData = self.__outputByUnderlying[i]["numTrainData"]
            outSampleSubTag = self.__outputByUnderlying[i]["outSampleSubTag"]
            # featureScores = model.outputByUnderlying[i]["featureScores"]
            tempCombineTradingOrder = {}
            if funStr is None:
                tempCombineTradingOrder = self.runBackTest(self.__getSymbolFromModelMgm(i), outSamplePredict, inSamplePredict,
                                                           outSampleSubTag)
            elif funStr == 'signalTag':
                self.__funStr = funStr
                tempCombineTradingOrder = self.signalTag(outSamplePredict, inSamplePredict, outSampleSubTag)
            elif funStr == "signalMaxMinTag":
                self.__funStr = funStr
                tempCombineTradingOrder = self.signalMaxMinTag(outSamplePredict, inSamplePredict, outSampleSubTag)
            tempCombineTradingOrder.update({"outSampleRMSE": outSampleRMSE})
            tempCombineTradingOrder.update({"numTrainData": numTrainData})
            # tempCombineTradingOrder.update({"featureScores": featureScores})
            self.TradingEvaluate(tempCombineTradingOrder, outSamplePredict, show)
            if show:
                self.__consoleOutput(tempCombineTradingOrder)
            combineTradingOrder[i].update(tempCombineTradingOrder)
            detailedOrders = tempCombineTradingOrder.get("detailedOrders")
            tempCombineTradingOrder.pop("detailedOrders", None)
            filePath = self.__absolutePath+'ModelSaved/' + self.__backTestUnderlying + '_' + self.__modelName + '_SavedModelBuilder'
            if os.path.exists(filePath):
                with open(filePath + "/result.json", "w") as f:
                    json.dump(tempCombineTradingOrder, f)
            else:
                with open("result.json", "w") as f:
                    json.dump(tempCombineTradingOrder, f)
            # output the detailed orders in the json file
            if self.__funStr is None:
                if os.path.exists(filePath):
                    with open(filePath + "/detailedOrders.json", "w") as f:
                        json.dump(detailedOrders, f)
                else:
                    with open("detailedOrders.json", "w") as f:
                        json.dump(detailedOrders, f)
            OutputSpreadSheet(detailedOrders, tempCombineTradingOrder, filePath, self.__funStr)
            if len(windowUnderlyingSameIndex) != 0:
                for k in range(len(windowUnderlyingSameIndex)):
                    rollingTradingOrder[windowUnderlyingSameIndex[k]][0] = combineTradingOrder[windowUnderlyingSameIndex[k]]
        return rollingTradingOrder, combineTradingOrder

    def TradingEvaluate(self, TradingOrder, outSamplePredict, show):
        threshold = 0.001  # 盈利阈值
        triggerTimes = TradingOrder["order"].__len__()  # 触发次数
        winTimes = 0  # 获利次数
        winRate = 0  # 胜率
        timesPerDay = 0  # 日均开仓次数
        longTimes = 0  # 开多仓次数
        shortTimes = 0  # 开空仓次数
        averageReturnRate = 0  # 平均收益率
        averageReturnRateProfit = 0  # 平均获利收益率
        averageReturnRateLoss = 0  # 平均亏损收益率
        profitLossRatio = 0  # 盈亏比
        maxLoss = 0  # 最大亏损
        averagePositionTime = 0  # 平均持仓时间
        afterCostProfit = 0  # 算上手续费的总盈亏
        aveDailyCumAmount = 0  # 日均成交额
        maxDailyCumAmount = 0  # 最大日成交额
        annualReturnMV = 0  # 年化市值收益率
        if triggerTimes != 0:
            winRate = winTimes / triggerTimes
            if self.__funStr is None:
                cumOpenAmount = TradingOrder["cumOpenAmount"]
                preCostProfit = TradingOrder["preCostProfit"]
                afterCostProfit = preCostProfit - self.__COST_RATE * cumOpenAmount
                afterCostProfit = round(afterCostProfit, 2)
                dayCounts = TradingOrder["dayCounts"]
                if dayCounts != 0:
                    aveDailyCumAmount = cumOpenAmount / dayCounts
                    for item in TradingOrder["dailyOpenAmount"].values():
                        if item > maxDailyCumAmount:
                            maxDailyCumAmount = item
                    annualReturnMV = afterCostProfit / self.__initAmount / dayCounts * 250
            else:
                dayCounts = outSamplePredict.__len__() / 4800
            if dayCounts != 0:
                timesPerDay = triggerTimes / dayCounts
        if triggerTimes > 0:
            for order in TradingOrder["order"]:
                if show:
                    print(order)
                # 计算持仓时间(min)
                startTime = dt.datetime.strptime(order["startTime"], "%m/%d/%y-%H:%M:%S")
                endTime = dt.datetime.strptime(order["endTime"], "%m/%d/%y-%H:%M:%S")
                if startTime.hour <= 11 and endTime.hour >= 13:
                    averagePositionTime += (endTime - startTime).seconds / 60 - 90
                else:
                    averagePositionTime += (endTime - startTime).seconds / 60
                # 计算开多和开空次数
                if order["direction"] == 'long ':
                    longTimes += 1
                else:
                    shortTimes += 1
                # 计算收益率相关值
                averageReturnRate += order["returnRate"]
                if order["returnRate"] > threshold:
                    winTimes += 1
                    averageReturnRateProfit += order["returnRate"] - threshold
                else:
                    averageReturnRateLoss += order["returnRate"] - threshold
                    if order["returnRate"] < maxLoss:
                        maxLoss = order["returnRate"]
            averagePositionTime /= triggerTimes
            winRate = winTimes / triggerTimes
            averageReturnRate /= triggerTimes
            if winTimes > 0:
                averageReturnRateProfit /= winTimes
            if triggerTimes > winTimes:
                averageReturnRateLoss /= (triggerTimes - winTimes)
                if abs(averageReturnRateLoss) > 0:
                    profitLossRatio = averageReturnRateProfit / abs(averageReturnRateLoss)
        TradingOrder.update({"triggerTimes": triggerTimes})
        TradingOrder.update({"timesPerDay": timesPerDay})
        TradingOrder.update({"winTimes": winTimes})
        TradingOrder.update({"winRate": winRate})
        TradingOrder.update({"longTimes": longTimes})
        TradingOrder.update({"shortTimes": shortTimes})
        TradingOrder.update({"averageReturnRate": averageReturnRate})
        TradingOrder.update({"averageReturnRateProfit": averageReturnRateProfit})
        TradingOrder.update({"averageReturnRateLoss": averageReturnRateLoss})
        TradingOrder.update({"profitLossRatio": profitLossRatio})
        TradingOrder.update({"maxLoss": maxLoss})
        TradingOrder.update({"averagePositionTime": averagePositionTime})
        if self.__funStr is None:
            TradingOrder.update({"afterCostProfit": afterCostProfit})
            TradingOrder.update({"initAmount": self.__initAmount})
            TradingOrder.update({"aveDailyCumAmount": aveDailyCumAmount})
            TradingOrder.update({"maxDailyCumAmount": maxDailyCumAmount})
            TradingOrder.update({"annualReturnMV": annualReturnMV})
        return TradingOrder

    def __consoleOutput(self, tempCombineTradingOrder):
        print("modelName:          " + self.__modelName)
        print("longTriggerRatio:   " + str(tempCombineTradingOrder["longTriggerRatio"]))
        print("shortTriggerRatio:  " + str(tempCombineTradingOrder["shortTriggerRatio"]))
        print("triggerTimes:       " + str(tempCombineTradingOrder["triggerTimes"]))
        print("winTimes:           " + str(tempCombineTradingOrder["winTimes"]))
        print("winRate:            " + str(tempCombineTradingOrder["winRate"]))
        print("averageReturnRate:  " + str(tempCombineTradingOrder["averageReturnRate"]))
        print("longTimes:          " + str(tempCombineTradingOrder["longTimes"]))
        print("shortTimes:         " + str(tempCombineTradingOrder["shortTimes"]))
        print("profitLossRatio:    " + str(tempCombineTradingOrder["profitLossRatio"]))
        print("maxLoss:            " + str(tempCombineTradingOrder["maxLoss"]))
        print("averagePositionTime:" + str(tempCombineTradingOrder["averagePositionTime"]))
        print("timesPerDay:        " + str(tempCombineTradingOrder["timesPerDay"]))
        print("outSampleRMSE:      " + str(tempCombineTradingOrder["outSampleRMSE"]))
        print("numTrainData:       " + str(tempCombineTradingOrder["numTrainData"]))
        if self.__funStr is None:
            print("initAmount          " + str(tempCombineTradingOrder["initAmount"]))
            print("costRate            " + str(self.__COST_RATE))
            print("cumOpenAmount       " + str(tempCombineTradingOrder["cumOpenAmount"]))
            print("preCostProfit       " + str(tempCombineTradingOrder["preCostProfit"]))
            print("afterCostProfit     " + str(tempCombineTradingOrder["afterCostProfit"]))
            print("afterCostDailyProfit" + str(tempCombineTradingOrder["afterCostDailyProfit"]))
            print("dailyOpenAmount     " + str(tempCombineTradingOrder["dailyOpenAmount"]))
            print("aveDailyCumAmount   " + str(tempCombineTradingOrder["aveDailyCumAmount"]))
            print("maxDailyCumAmount   " + str(tempCombineTradingOrder["maxDailyCumAmount"]))
            print("annualReturnMV      " + str(tempCombineTradingOrder["annualReturnMV"]))
        print("\r")

    def signalTag(self, outSamplePredict, inSamplePredict, subTag):  # 按照信号值去平仓
        # plt.figure()
        # plt.plot(outSamplePredict)
        # with open("Predict.json", "w") as f:
        #     Predict = {'Predict': outSamplePredict.tolist()}
        #     json.dump(Predict, f)
        tradingOrder = {}
        order = []
        k = 0
        longTriggerRatio = max([self.__para["longMinTriggerRatio"], 0.02 / subTag[-1][self.__tagName].startPrice,
                                np.percentile(inSamplePredict, self.__para["longTriggerRatioPercentile"])])
        shortTriggerRatio = min([self.__para["shortMinTriggerRatio"], -0.02 / subTag[-1][self.__tagName].startPrice,
                                 np.percentile(inSamplePredict, self.__para["shortTriggerRatioPercentile"])])
        longCloseRatio = self.__para["closeRatio"]
        shortCloseRatio = -self.__para["closeRatio"]
        if os.path.exists(self.__absolutePath+'ModelSaved/' + self.__backTestUnderlying + '_' + self.__modelName + '_SavedModelBuilder'):
            with open(self.__absolutePath+'ModelSaved/' + self.__backTestUnderlying + '_' + self.__modelName + '_SavedModelBuilder' + "/triggerRatio.json", "w") as f:
                triggerRatio = {'longTriggerRatio': longTriggerRatio, 'shortTriggerRatio': shortTriggerRatio,
                                'longCloseRatio': longCloseRatio, 'shortCloseRatio': shortCloseRatio}
                json.dump(triggerRatio, f)
        else:
            with open("triggerRatio.json", "w") as f:
                triggerRatio = {'longTriggerRatio': longTriggerRatio, 'shortTriggerRatio': shortTriggerRatio,
                                'longCloseRatio': 0, 'shortCloseRatio': 0}
                json.dump(triggerRatio, f)
        while k < outSamplePredict.__len__() - 1: # 对样本外的记录（每个tick一条）进行逐行循环
            if outSamplePredict[k] > longTriggerRatio:  # 如样本外的未来1分钟收益率预测值 > longTriggerRatio, 则下面添加一条做多的记录
                tempOrder = {}
                tagName = self.__tagName
                tempOrder.update({"code": subTag[k][tagName].code})  # 以下记录开仓方向、时间和价格
                tempOrder.update({"direction": "long "})
                tempOrder.update({"startTime": dt.datetime.fromtimestamp(
                    subTag[k][tagName].startTimeStamp).strftime('%m/%d/%y-%H:%M:%S')})
                if subTag[k][tagName].startSliceData is None:  # 因为计算tag时候可能传入指数切片，此时切片会为None
                    k += 1
                    continue
                if subTag[k][tagName].startSliceData.askPrice[0] != 0:
                    tempOrder.update({"startPrice": round(subTag[k][tagName].startSliceData.askPrice[0], 2)})
                else:
                    k += 1
                    continue
                if (subTag[k + 1][tagName].startTimeStamp - subTag[k][tagName].startTimeStamp) > 3600:  # 如跨中午或跨日则不开仓
                    k += 1
                    continue
                k += 1
                while k < outSamplePredict.__len__() - 1:  # 判断是否满足这些条件：如未来1分钟收益率预测值 <= longCloseRatio，或跨中午、或跨日，或回撤超过maxLose
                    if outSamplePredict[k] <= longCloseRatio or (
                            subTag[k + 1][tagName].startTimeStamp - subTag[k][tagName].startTimeStamp) \
                            > 3600 or subTag[k][tagName].startSliceData.bidPrice[0] / tempOrder["startPrice"] - 1 < self.__para["maxLose"]:
                        break   # 若满足上述条件则满足了平仓条件，否则继续找下一条记录（这个回测逻辑是基于若已开仓、不会再开仓）
                    else:   # 下面记录平仓时点、价格和收益率
                        k += 1
                tempOrder.update({"endTime": dt.datetime.fromtimestamp(
                    subTag[k][tagName].startTimeStamp).strftime('%m/%d/%y-%H:%M:%S')})
                if subTag[k][tagName].startSliceData is None:
                    k += 1
                    continue
                if subTag[k][tagName].startSliceData.askPrice[0] != 0:
                    tempOrder.update({"endPrice": round(subTag[k][tagName].startSliceData.askPrice[0] - 0.01, 2)})
                else:
                    tempOrder.update({"endPrice": round(subTag[k][tagName].startSliceData.bidPrice[0], 2)})
                tempOrder.update({"returnRate": round(tempOrder["endPrice"] / tempOrder["startPrice"] - 1, 5)})
                order.append(tempOrder)
            elif outSamplePredict[k] < shortTriggerRatio:
                tempOrder = {}
                tagName = self.__tagName
                tempOrder.update({"code": subTag[k][tagName].code})
                tempOrder.update({"direction": "short"})
                tempOrder.update({"startTime": dt.datetime.fromtimestamp(
                    subTag[k][tagName].startTimeStamp).strftime('%m/%d/%y-%H:%M:%S')})
                if subTag[k][tagName].startSliceData is None:
                    k += 1
                    continue
                if subTag[k][tagName].startSliceData.bidPrice[0] != 0:
                    tempOrder.update({"startPrice": round(subTag[k][tagName].startSliceData.bidPrice[0], 2)})
                else:
                    k += 1
                    continue
                if (subTag[k + 1][tagName].startTimeStamp - subTag[k][tagName].startTimeStamp) > 3600:
                    k += 1
                    continue
                k += 1
                while k < outSamplePredict.__len__() - 1:
                    if outSamplePredict[k] >= shortTriggerRatio or (
                            subTag[k + 1][tagName].startTimeStamp - subTag[k][tagName].startTimeStamp) > 3600 \
                            or 1 - subTag[k][tagName].startSliceData.askPrice[0] / tempOrder["startPrice"] < self.__para["maxLose"]:
                        break
                    else:
                        k += 1
                tempOrder.update({"endTime": dt.datetime.fromtimestamp(
                    subTag[k][tagName].startTimeStamp).strftime('%m/%d/%y-%H:%M:%S')})
                if subTag[k][tagName].startSliceData is None:
                    k += 1
                    continue
                if subTag[k][tagName].startSliceData.bidPrice[0] != 0:
                    tempOrder.update({"endPrice": round(subTag[k][tagName].startSliceData.bidPrice[0] + 0.01, 2)})
                else:
                    tempOrder.update({"endPrice": round(subTag[k][tagName].startSliceData.askPrice[0], 2)})
                tempOrder.update({"returnRate": round(1 - tempOrder["endPrice"] / tempOrder["startPrice"], 5)})
                order.append(tempOrder)
            else:
                k += 1
        tradingOrder.update({"longTriggerRatio": longTriggerRatio})
        tradingOrder.update({"shortTriggerRatio": shortTriggerRatio})
        tradingOrder.update({"order": order})
        return tradingOrder

    def signalMaxMinTag(self, outSamplePredict, inSamplePredict, subTag):  # 按照信号值去平仓
        # plt.figure()
        # plt.plot(outSamplePredict)
        with open("Predict.json", "w") as f:
            Predict = {'Predict': outSamplePredict.tolist()}
            json.dump(Predict, f)
        tradingOrder = {}
        order = []
        k = 0
        longTriggerRatio = max([self.__para["longMinTriggerRatio"], 0.01 / subTag[-1][self.__tagName].startPrice,
                                np.percentile((inSamplePredict[:, 0]+inSamplePredict[:, 1])/2, self.__para["longTriggerRatioPercentile"])])
        shortTriggerRatio = min([self.__para["shortMinTriggerRatio"], -0.01 / subTag[-1][self.__tagName].startPrice,
                                 np.percentile((inSamplePredict[:, 0]+inSamplePredict[:, 1])/2, self.__para["shortTriggerRatioPercentile"])])
        longRiskRatio = self.__para["riskRatio"]
        shortRiskRatio = -self.__para["riskRatio"]
        longCloseRatio = self.__para["closeRatio"]
        shortCloseRatio = -self.__para["closeRatio"]
        if os.path.exists(self.__absolutePath+'ModelSaved/' + self.__backTestUnderlying + '_' + self.__modelName + '_SavedModelBuilder'):
            with open(self.__absolutePath+'ModelSaved/' + self.__backTestUnderlying + '_' + self.__modelName + '_SavedModelBuilder' + "/triggerRatio.json", "w") as f:
                triggerRatio = {'longTriggerRatio': longTriggerRatio, 'shortTriggerRatio': shortTriggerRatio,
                                'longRiskRatio': longRiskRatio, 'shortRiskRatio': shortRiskRatio,
                                'longCloseRatio': longCloseRatio, 'shortCloseRatio': shortCloseRatio}
                json.dump(triggerRatio, f)
        else:
            with open("triggerRatio.json", "w") as f:
                triggerRatio = {'longTriggerRatio': longTriggerRatio, 'shortTriggerRatio': shortTriggerRatio,
                                'longRiskRatio': longRiskRatio, 'shortRiskRatio': shortRiskRatio,
                                'longCloseRatio': longCloseRatio, 'shortCloseRatio': shortCloseRatio}
                json.dump(triggerRatio, f)
        while k < outSamplePredict.shape[0] - 1:  # outSamplePredict[k, 0] 是预测未来1分钟收益率的最大值，[k, 1]是预测未来1分钟收益率的最小值
            if (outSamplePredict[k, 0]+outSamplePredict[k, 1])/2 > longTriggerRatio and outSamplePredict[k, 1] > longRiskRatio:
                # longCloseRatio = max([-(outSamplePredict[k, 0]+outSamplePredict[k, 1])/2/2, longCloseRatio])
                tempOrder = {}
                tagName = self.__tagName
                tempOrder.update({"code": subTag[k][tagName].code})  # 以下记录开仓方向、时间和价格
                tempOrder.update({"direction": "long "})
                tempOrder.update({"startTime": dt.datetime.fromtimestamp(
                    subTag[k][tagName].startTimeStamp).strftime('%m/%d/%y-%H:%M:%S')})
                if subTag[k][tagName].startSliceData is None:  # 因为计算tag时候可能传入指数切片，此时切片会为None
                    k += 1
                    continue
                if subTag[k][tagName].startSliceData.askPrice[0] != 0:
                    tempOrder.update({"startPrice": round(subTag[k][tagName].startSliceData.askPrice[0], 2)})
                else:
                    k += 1
                    continue
                if (subTag[k + 1][tagName].startTimeStamp - subTag[k][tagName].startTimeStamp) > 3600:   # 如跨中午或跨日则不开仓
                    k += 1
                    continue
                k += 1
                while k < outSamplePredict.shape[0] - 1:  # 判断平仓条件、并记录结束时间、价格和收益率等
                    if (outSamplePredict[k, 0] + outSamplePredict[k, 1]) / 2 <= longCloseRatio or (
                            subTag[k + 1][tagName].startTimeStamp - subTag[k][tagName].startTimeStamp) \
                            > 3600 or subTag[k][tagName].startSliceData.bidPrice[0] / tempOrder["startPrice"] - 1 < self.__para["maxLose"]:
                        break
                    else:
                        k += 1
                tempOrder.update({"endTime": dt.datetime.fromtimestamp(
                    subTag[k][tagName].startTimeStamp).strftime('%m/%d/%y-%H:%M:%S')})
                if subTag[k][tagName].startSliceData is None:
                    k += 1
                    continue
                if subTag[k][tagName].startSliceData.askPrice[0] != 0:
                    tempOrder.update({"endPrice": round(subTag[k][tagName].startSliceData.askPrice[0] - 0.01, 2)})
                else:
                    tempOrder.update({"endPrice": round(subTag[k][tagName].startSliceData.bidPrice[0], 2)})
                tempOrder.update({"returnRate": round(tempOrder["endPrice"] / tempOrder["startPrice"] - 1, 5)})
                order.append(tempOrder)
            elif (outSamplePredict[k, 0]+outSamplePredict[k, 1])/2 < shortTriggerRatio and outSamplePredict[k, 0] < shortRiskRatio:
                # shortCloseRatio = min([-(outSamplePredict[k, 0]+outSamplePredict[k, 1])/2/2, shortCloseRatio])
                tempOrder = {}
                tagName = self.__tagName
                tempOrder.update({"code": subTag[k][tagName].code})
                tempOrder.update({"direction": "short"})
                tempOrder.update({"startTime": dt.datetime.fromtimestamp(
                    subTag[k][tagName].startTimeStamp).strftime('%m/%d/%y-%H:%M:%S')})
                if subTag[k][tagName].startSliceData is None:
                    k += 1
                    continue
                if subTag[k][tagName].startSliceData.bidPrice[0] != 0:
                    tempOrder.update({"startPrice": round(subTag[k][tagName].startSliceData.bidPrice[0], 2)})
                else:
                    k += 1
                    continue
                if (subTag[k + 1][tagName].startTimeStamp - subTag[k][tagName].startTimeStamp) > 3600:
                    k += 1
                    continue
                k += 1
                while k < outSamplePredict.__len__() - 1:
                    if (outSamplePredict[k, 0] + outSamplePredict[k, 1]) / 2 >= shortCloseRatio or (
                            subTag[k + 1][tagName].startTimeStamp - subTag[k][tagName].startTimeStamp) > 3600 \
                            or 1 - subTag[k][tagName].startSliceData.askPrice[0] / tempOrder["startPrice"] < self.__para["maxLose"]:
                        break
                    else:
                        k += 1
                tempOrder.update({"endTime": dt.datetime.fromtimestamp(
                    subTag[k][tagName].startTimeStamp).strftime('%m/%d/%y-%H:%M:%S')})
                if subTag[k][tagName].startSliceData is None:
                    k += 1
                    continue
                if subTag[k][tagName].startSliceData.bidPrice[0] != 0:
                    tempOrder.update({"endPrice": round(subTag[k][tagName].startSliceData.bidPrice[0] + 0.01, 2)})
                else:
                    tempOrder.update({"endPrice": round(subTag[k][tagName].startSliceData.askPrice[0], 2)})
                tempOrder.update({"returnRate": round(1 - tempOrder["endPrice"] / tempOrder["startPrice"], 5)})
                order.append(tempOrder)
            else:
                k += 1
        tradingOrder.update({"longTriggerRatio": longTriggerRatio})
        tradingOrder.update({"shortTriggerRatio": shortTriggerRatio})
        tradingOrder.update({"order": order})
        return tradingOrder

    @staticmethod
    def triggerOptimization(analysisMat):
        analysisMat = np.array(analysisMat)
        score = (analysisMat[:, 3] - 0.001) * analysisMat[:, 5]
        index = np.array(list(range(analysisMat.shape[0])))
        winRateCondition = analysisMat[:, 2] >= 0.65
        averageReturnRateCondition = analysisMat[:, 3] >= 0.002
        timesPerDayCondition = analysisMat[:, 5] <= 15

        condition1 = np.vstack((winRateCondition, averageReturnRateCondition, timesPerDayCondition)).all(
            0)
        condition2 = np.vstack((winRateCondition, timesPerDayCondition)).all(0)
        condition3 = np.vstack((averageReturnRateCondition, timesPerDayCondition)).all(0)
        condition4 = timesPerDayCondition
        condition5 = np.vstack((winRateCondition, averageReturnRateCondition)).all(0)
        condition6 = winRateCondition
        if condition1.any():
            bestLine = index[condition1][np.argmax(score[condition1])]
        elif condition2.any():
            bestLine = index[condition2][np.argmax(score[condition2])]
        elif condition3.any():
            bestLine = index[condition3][np.argmax(score[condition3])]
        elif condition4.any():
            bestLine = index[condition4][np.argmax(score[condition4])]
        elif condition5.any():
            bestLine = index[condition5][np.argmax(score[condition5])]
        elif condition6.any():
            bestLine = index[condition6][np.argmax(score[condition6])]
        else:
            bestLine = np.argmax(score)

        return bestLine

    @staticmethod
    def triggerOptimizationProfit(analysisMat):
        analysisMat = np.array(analysisMat)
        score = analysisMat[:, 6]
        index = np.array(list(range(analysisMat.shape[0])))
        winRateCondition = analysisMat[:, 2] >= 0.55
        averageReturnRateCondition = analysisMat[:, 3] >= 0.0018
        # timesPerDayCondition = analysisMat[:, 5] <= 15

        condition1 = np.vstack((winRateCondition, averageReturnRateCondition)).all(
            0)
        condition2 = winRateCondition
        condition3 = averageReturnRateCondition
        if condition1.any():
            bestLine = index[condition1][np.argmax(score[condition1])]
        elif condition2.any():
            bestLine = index[condition2][np.argmax(score[condition2])]
        elif condition3.any():
            bestLine = index[condition3][np.argmax(score[condition3])]
        else:
            bestLine = np.argmax(score)

        return bestLine

    @staticmethod
    def triggerOptimizationProfitAndInitAmount(analysisMat):
        analysisMat = np.array(analysisMat)
        score = analysisMat[:, 6]
        score2 = analysisMat[:, 7]
        index = np.array(list(range(analysisMat.shape[0])))
        annualReturnMVCondition = analysisMat[:, 7] >= 0.08
        winRateCondition = analysisMat[:, 2] >= 0.55
        averageReturnRateCondition = analysisMat[:, 3] >= 0.0018
        # timesPerDayCondition = analysisMat[:, 5] <= 15

        condition1 = np.vstack((annualReturnMVCondition, winRateCondition, averageReturnRateCondition)).all(0)
        condition2 = np.vstack((annualReturnMVCondition, winRateCondition)).all(0)
        condition3 = np.vstack((annualReturnMVCondition, averageReturnRateCondition)).all(0)
        condition4 = annualReturnMVCondition
        condition5 = np.vstack((winRateCondition, averageReturnRateCondition)).all(0)
        condition6 = winRateCondition
        condition7 = averageReturnRateCondition
        if condition1.any():
            bestLine = index[condition1][np.argmax(score[condition1])]
        elif condition2.any():
            bestLine = index[condition2][np.argmax(score[condition2])]
        elif condition3.any():
            bestLine = index[condition3][np.argmax(score[condition3])]
        elif condition4.any():
            bestLine = index[condition4][np.argmax(score[condition4])]
        elif condition5.any():
            bestLine = index[condition5][np.argmax(score2[condition5])]
        elif condition6.any():
            bestLine = index[condition6][np.argmax(score2[condition6])]
        elif condition7.any():
            bestLine = index[condition7][np.argmax(score2[condition7])]
        else:
            bestLine = np.argmax(score2)

        return bestLine

    def runBackTest(self, symbol, outSamplePredict, inSamplePredict, subTag):  # 按照信号值去平仓
        # self.__plotPredict(outSamplePredict)

        self.__outputMgr = OutputManager(self.__COST_RATE)
        self.__signalExecutor.generateTriggerRatio(symbol, self.__backTestUnderlying, self.__para, inSamplePredict,
                                                   subTag[-1][self.__tagName].startPrice, self.__absolutePath,
                                                   self.__modelName, self.__tickData)

        k = 0
        while k < outSamplePredict.shape[0] - 1:  # outSamplePredict[k, 0] 是预测未来1分钟收益率的最大值，[k, 1]是预测未来1分钟收益率的最小值
            outSamplePredictArray = outSamplePredict[k]
            tagInfo = subTag[k][self.__tagName]
            if tagInfo.startSliceData is not None:
                self.__setNoonRange(symbol, tagInfo)
                if self.__isNewDay(symbol, tagInfo.startTimeStamp):
                    self.__comingNewDay(symbol, tagInfo)
                # making order here because the time span between two ticks may vary.
                # making the order that was placed last tick
                self.__makeOrder(symbol, tagInfo)
                if self.__validTradingTime(tagInfo.startSliceData.time):
                    self.__mockTrading(symbol, outSamplePredictArray, tagInfo)
                else:
                    self.__processMarketClose(symbol, tagInfo)
                self.__preTagInfo.update({symbol: tagInfo})
            k += 1
        return self.__returnTradings(symbol)

    def __mockTrading(self, symbol, outSamplePredictArray, tagInfo):
        self.__riskMgr.checkStopLoss(symbol, tagInfo.startSliceData)
        # check non finished close order status
        if self.__positionManager.hasNonFinished(symbol):
            if self.__isOrderValid(symbol, tagInfo) and not self.__riskMgr.isStopLoss(symbol) and not self.__riskMgr.isInDanger(symbol):
                # drive the non-finished order and return to the next predict slice directly
                self.__onNewTick(symbol, outSamplePredictArray, tagInfo)
                return
            else:
                self.__driveInValidNonFinishedOrder(symbol)
        # do mock trading
        self.__onNewTick(symbol, outSamplePredictArray, tagInfo)
        self.__onPredictUpdated(symbol, outSamplePredictArray, tagInfo)

    #  判断这笔平仓订单是否在一档盘口及以内
    #  如果订单inValid，则return False，需要撤单
    #  如果订单Valid，则return True，不需要撤单
    def __isOrderValid(self, symbol, tagInfo):
        exchangeOrder = self.__positionManager.getNonFinishedOrder(symbol)
        price = exchangeOrder.setPrice
        ask1 = tagInfo.startSliceData.askPrice[0]
        bid1 = tagInfo.startSliceData.bidPrice[0]
        if self.__getOrderSide(exchangeOrder.BSFlag) == OrderSide.Sell and price > ask1:
            return False
        elif self.__getOrderSide(exchangeOrder.BSFlag) == OrderSide.Buy and price < bid1:
            return False
        else:
            return True

    # def __driveValidNonFinishedOrder(self, symbol):
    #     exchangeOrder = self.__positionManager.getNonFinishedOrder(symbol)
    #     self.__makeOrder(exchangeOrder.orderNumber, False)

    def __driveInValidNonFinishedOrder(self, symbol):
        exchangeOrder = self.__positionManager.getNonFinishedOrder(symbol)
        exchangeOrder = self.__exchangeHouse.back(exchangeOrder.orderNumber)
        self.__orderFinished(exchangeOrder)

    # this method will now be called as every tick comes, to update tick info
    def __onNewTick(self, symbol, outSamplePredictArray, tagInfo):
        self.__signalExecutor.updatePredictInfo(outSamplePredictArray, tagInfo)

    def __onPredictUpdated(self, symbol, outSamplePredictArray, tagInfo):
        if self.__positionManager.isPositionClosed(symbol):
            self.__outputMgr.registerOutput(symbol, tagInfo.startTimeStamp)  # 平仓状态，outputMgr负责生成order统计
            self.__allowOpenNew(symbol, outSamplePredictArray, tagInfo)
        elif self.__positionManager.isPositionPositive(symbol):
            self.__processPositivePosition(symbol, outSamplePredictArray, tagInfo)
        elif self.__positionManager.isPositionNegative(symbol):
            self.__processNegativePosition(symbol, outSamplePredictArray, tagInfo)

    def __allowOpenNew(self, symbol, outSamplePredictArray, tagInfo):
        if self.__isOpenLong(symbol, outSamplePredictArray, tagInfo):
            self.__processOpenSignal(symbol, OrderSide.Buy, tagInfo)
        elif self.__isOpenShort(symbol, outSamplePredictArray, tagInfo):
            self.__processOpenSignal(symbol, OrderSide.Sell, tagInfo)

    def __processPositivePosition(self, symbol, outSamplePredictArray, tagInfo):
        if self.__isCloseLong(symbol, outSamplePredictArray, tagInfo) or self.__riskMgr.isStopLoss(symbol) or self.__riskMgr.isInDanger(symbol):
            self.__processCloseSignal(symbol, OrderSide.Sell, tagInfo)
        elif self.__isOpenLong(symbol, outSamplePredictArray, tagInfo):
            self.__processOpenSignal(symbol, OrderSide.Buy, tagInfo)

    def __processNegativePosition(self, symbol, outSamplePredictArray, tagInfo):
        if self.__isCloseShort(symbol, outSamplePredictArray, tagInfo) or self.__riskMgr.isStopLoss(symbol) or self.__riskMgr.isInDanger(symbol):
            self.__processCloseSignal(symbol, OrderSide.Buy, tagInfo)
        elif self.__isOpenShort(symbol, outSamplePredictArray, tagInfo):
            self.__processOpenSignal(symbol, OrderSide.Sell, tagInfo)

    def __processOpenSignal(self, symbol, side, tagInfo):
        price = self.__calPrice(symbol, side, True, tagInfo)
        quantity = self.__calQty(symbol, price, self.__getMaAmount(symbol, tagInfo))
        if quantity <= 0:
            return
        elif quantity < self.__MIN_ORDER_QTY:
            return
        preClosePx = tagInfo.startSliceData.previousClosingPrice
        ratio = abs(price / preClosePx - 1.0)
        if ratio >= self.__OPEN_FORBIDDEN:
            return
        self.__placeOrder(symbol, side, price, quantity, True, tagInfo.startTimeStamp)

    def __processCloseSignal(self, symbol, side, tagInfo):
        price = self.__calPrice(symbol, side, False, tagInfo)
        # quantity = abs(self.__positionManager.getNetPosition(symbol))
        quantity = self.__calCloseQty(symbol, price)
        self.__placeOrder(symbol, side, price, quantity, False, tagInfo.startTimeStamp)

    def __calCloseQty(self, symbol, price):
        netPosition = abs(self.__positionManager.getNetPosition(symbol))
        # 支持多空翻转操作，support for long-short inverse
        if symbol in self.__exePriceQty and "volume" in self.__exePriceQty.get(symbol):
            volume = int(self.__exePriceQty.get(symbol).get("volume"))
            if self.__riskMgr.isInDanger(symbol):
                return netPosition
            else:
                if volume > netPosition:
                    # 翻转下单
                    exposure = volume - netPosition
                    maxExposure = self.__maxExposure
                    if maxExposure is None:
                        maxExposure = sys.maxsize
                    exposure = min(exposure, maxExposure / price, self.__maxTurnoverPerOrder / price,
                                   self.__positionManager.getBuyAvailQty(symbol), self.__positionManager.getSellAvailQty(symbol))
                    return int(exposure + netPosition)
                else:
                    return volume
        else:
            return netPosition

    def __calPrice(self, symbol, side, isOpen, tagInfo):
        # priceLevel = 1
        # deviation = 0
        if isOpen:
            if side == OrderSide.Buy:
                priceLevel = self.__buyLevel
                deviation = self.__buyDeviation
            else:
                priceLevel = -self.__buyLevel
                deviation = -self.__buyDeviation
        else:
            if side == OrderSide.Buy:
                priceLevel = -self.__sellLevel
                deviation = -self.__sellDeviation
            else:
                priceLevel = self.__sellLevel
                deviation = self.__sellDeviation
        if priceLevel > 0:
            priceList = tagInfo.startSliceData.askPrice
        else:
            priceList = tagInfo.startSliceData.bidPrice
        price = priceList[abs(priceLevel) - 1]
        # in case that price is zero
        ask = np.array(tagInfo.startSliceData.askPrice)
        bid = np.array(tagInfo.startSliceData.bidPrice)
        askTemp = ask[ask > 0]
        bidTemp = bid[bid > 0]
        if len(askTemp) == 0:
            highest = tagInfo.startSliceData.bidPrice[0]
        else:
            highest = max(askTemp)
        if len(bidTemp) == 0:
            lowest = tagInfo.startSliceData.askPrice[0]
        else:
            lowest = min(bidTemp)

        # use the price given in the signal executor
        if symbol in self.__exePriceQty and "price" in self.__exePriceQty.get(symbol):
            price = self.__exePriceQty.get(symbol).get("price")
            if price == 0:
                if side == OrderSide.Buy:
                    price = highest
                elif side == OrderSide.Sell:
                    price = lowest
        elif not self.__riskMgr.isStopLoss(symbol) and not self.__riskMgr.isInDanger(symbol):
            if price == 0:
                if side == OrderSide.Buy:
                    price = highest
                elif side == OrderSide.Sell:
                    price = lowest
            price += deviation
            if price > highest:
                price = highest
            elif price < lowest:
                price = lowest
        else:  # stop loss in risk manager or price reaches high/low limits
            if side == OrderSide.Buy:
                ask = tagInfo.startSliceData.askPrice[0]
                if ask == 0:
                    price = highest
                else:
                    price = ask
            else:
                bid = tagInfo.startSliceData.bidPrice[0]
                if bid == 0:
                    price = lowest
                else:
                    price = bid

        return round(price, 2)

    def __calQty(self, symbol, price, maAmount):
        if maAmount is None or maAmount == 0:
            liquidQty = sys.maxsize
        else:
            liquidQty = maAmount * self.__maAmountRate / price

        if symbol in self.__exePriceQty and "volume" in self.__exePriceQty.get(symbol):
            if self.__maxExposure is not None:
                liquidQty = self.__maxExposure / price
            else:
                liquidQty = sys.maxsize
            availSpace = int(liquidQty - abs(self.__positionManager.getNetPosition(symbol)))
            volume = self.__exePriceQty.get(symbol).get("volume")
            quantity = min(availSpace, volume, self.__maxTurnoverPerOrder / price,
                           self.__positionManager.getBuyAvailQty(symbol), self.__positionManager.getSellAvailQty(symbol))
        else:
            if self.__maxExposure is not None:
                liquidQty = min(liquidQty, self.__maxExposure / price)
            availSpace = int(liquidQty - abs(self.__positionManager.getNetPosition(symbol)))
            quantity = min(availSpace, self.__maxTurnoverPerOrder / price,
                           self.__positionManager.getInitialQty(symbol) * self.__maxRatePerOrder,
                           self.__positionManager.getBuyAvailQty(symbol), self.__positionManager.getSellAvailQty(symbol))
        return int(math.floor(quantity / 100) * 100)

    def __placeOrder(self, symbol, side, price, quantity, isOpen, timeStamp):
        dateTime = dt.datetime.fromtimestamp(timeStamp)
        # 若在禁止开仓时刻之后，且为开仓单，则不再开仓。平仓单不受影响
        if (dateTime.time() < self.__START_OPEN_TIME or dateTime.time() >= self.__LAST_OPEN_TIME) and isOpen:
                return

        if side == OrderSide.Buy:
            sideStr = 'B'
        else:
            sideStr = 'S'
        order = Order(symbol, None, price, quantity, sideStr, dateTime)
        orderNo = self.__exchangeHouse.send(order)
        self.__orderInfo.update({symbol: OrderInfo(orderNo, isOpen)})

    def __makeOrder(self, symbol, tagInfo):
        if symbol not in self.__orderInfo or self.__orderInfo.get(symbol) is None:
            return
        orderInfo = self.__orderInfo.get(symbol)
        orderNo = orderInfo.orderNo
        if orderNo is None:
            self.__orderInfo.pop(symbol, None)
            return

        isOpen = orderInfo.isOpen
        currTime = tagInfo.startSliceData.time
        currTimeStamp = tagInfo.startTimeStamp
        exchangeOrder = self.__exchangeHouse.drive(orderNo, self.__getDriveTime(symbol, isOpen, currTime, currTimeStamp))
        if exchangeOrder.orderNumber is None or exchangeOrder is None:
            self.__orderInfo.pop(symbol, None)
            return

        # 开仓单必撤，平仓单需要在下一个Tick（当前）检查盘口
        if isOpen:
            exchangeOrder = self.__exchangeHouse.back(exchangeOrder.orderNumber)
            self.__orderFinished(exchangeOrder)
        else:
            if self.__isOrderFinished(exchangeOrder):
                self.__orderFinished(exchangeOrder)
            else:
                self.__positionManager.updatePosition(exchangeOrder)

    def __isNewDay(self, symbol, curr_timeStamp):
        if len(self.__preTagInfo) == 0 or symbol not in self.__preTagInfo:
            return True
        elif dt.datetime.fromtimestamp(curr_timeStamp).date() != dt.datetime.fromtimestamp(
                self.__preTagInfo.get(symbol).startTimeStamp).date():
            return True
        else:
            return False

    def __comingNewDay(self, symbol, tagInfo):
        preClosePrice = tagInfo.startSliceData.previousClosingPrice
        initQty = math.floor(self.__initAmount / preClosePrice / 100) * 100
        self.__signalExecutor.resetNewDay()
        self.__riskMgr.resetNewDay()
        self.__positionManager.initPosition(symbol, initQty)
        self.__pre_net_position.update({symbol: 0})
        self.__outputMgr.clearNonClosed(symbol)
        self.__outputMgr.addOneDay(symbol)
        self.__orderInfo.pop(symbol, None)

    def __split_reversed_cum_qty(self, last_net_position, net_position):
        if last_net_position * net_position < 0:
            return abs(last_net_position), abs(net_position)
        else:
            return None

    def __orderFinished(self, exchangeOrder):
        self.__orderInfo.pop(exchangeOrder.code, None)
        # self.__outputMgr.addOrder(exchangeOrder)
        # do not change the sequence!
        self.__positionManager.updatePosition(exchangeOrder)
        net_position = self.__positionManager.getNetPosition(exchangeOrder.code)
        self.__outputMgr.addOrder(exchangeOrder, self.__split_reversed_cum_qty(self.__pre_net_position.get(exchangeOrder.code), net_position))
        self.__riskMgr.updateCost(exchangeOrder, self.__positionManager.getNetPosition(exchangeOrder.code))
        self.__pre_net_position.update({exchangeOrder.code: net_position})

    def __isOpenLong(self, symbol, outSamplePredictArray, tagInfo):
        result = self.__signalExecutor.isOpenLong(outSamplePredictArray, tagInfo)
        return self.__checkExecutorOutput(symbol, result)

    def __isOpenShort(self, symbol, outSamplePredictArray, tagInfo):
        result = self.__signalExecutor.isOpenShort(outSamplePredictArray, tagInfo)
        return self.__checkExecutorOutput(symbol, result)

    def __isCloseLong(self, symbol, outSamplePredictArray, tagInfo):
        result = self.__signalExecutor.isCloseLong(outSamplePredictArray, tagInfo)
        return self.__checkExecutorOutput(symbol, result)

    def __isCloseShort(self, symbol, outSamplePredictArray, tagInfo):
        result = self.__signalExecutor.isCloseShort(outSamplePredictArray, tagInfo)
        return self.__checkExecutorOutput(symbol, result)

    # the returned value of signalExecutor may be one of three types
    # check SignalExecutorBase for more detailed info
    def __checkExecutorOutput(self, symbol, result):
        self.__exePriceQty.pop(symbol, None)
        # please do not change the sequence below!!
        if result is None:
            return False
        elif isinstance(result, bool):
            if result:
                return True
            else:
                return False
        elif isinstance(result, dict):
            self.__exePriceQty.update({symbol: result})
            return True

    def __processMarketClose(self, symbol, tagInfo):
        if self.__positionManager.hasNonFinished(symbol):
            exchangeOrder = self.__positionManager.getNonFinishedOrder(symbol)
            exchangeOrder = self.__exchangeHouse.back(exchangeOrder.orderNumber)
            self.__orderFinished(exchangeOrder)
        if not self.__positionManager.isPositionClosed(symbol):
            self.__closePositionAtMarketClose(symbol, tagInfo)

    # 如果当天收盘还有头寸未平，则fake一个ExchangeOrder，以市价盘口的思路去平仓
    # 如果十档内的量，能全部撮合，则价格为加权价格
    # 如果十档内的量，不能全部撮合，则价格为第十档价格
    def __closePositionAtMarketClose(self, symbol, tagInfo):
        dateTime = dt.datetime.fromtimestamp(tagInfo.startTimeStamp)
        netPosition = self.__positionManager.getNetPosition(symbol)
        price, accAmount = self.__calMarketCloseData(netPosition, tagInfo)
        if netPosition > 0:
            quantity = netPosition
            sideStr = 'S'
        else:
            quantity = -netPosition
            sideStr = 'B'

        order = Order(symbol, None, price, quantity, sideStr, dateTime)
        orderNo = self.__exchangeHouse.send(order)
        exchangeOrder = None
        # fake an exchange order
        if orderNo is not None:
            exchangeOrder = self.__exchangeHouse.drive(orderNo, 0)
        if orderNo is None or exchangeOrder is None:
            exchangeOrder = ExchangeOrder(order)
        if exchangeOrder.setVolume != exchangeOrder.volume:
            exchangeOrder.volume = int(quantity)
            exchangeOrder.accMount = accAmount
            exchangeOrder.isback = True
        self.__orderFinished(exchangeOrder)
        self.__outputMgr.registerOutput(symbol, tagInfo.startTimeStamp)
        # self.__positionManager.initPosition(symbol, self.__initQty)

    def __getDriveTime(self, symbol, isOpen, currTime, currTimeStamp):
        preTime = self.__preTagInfo.get(symbol).startSliceData.time
        preTimeStamp = self.__preTagInfo.get(symbol).startTimeStamp
        timeSpan = self.__timeSpan(symbol, preTime, preTimeStamp, currTime, currTimeStamp)
        if isOpen:
            if timeSpan >= self.__openWithdrawSeconds:
                return self.__openWithdrawSeconds
            else:
                return timeSpan
        else:
            return timeSpan

    def __validTradingTime(self, currTime):
        if currTime < self.__MARKET_CLOSE:
            return True
        else:
            return False

    # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    # helper functions
    # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    def __returnTradings(self, symbol):
        tradingOrder = {}
        tradingOrder.update({"order": self.__outputMgr.getOrder(symbol)})
        tradingOrder.update({"preCostProfit": self.__outputMgr.getProfit(symbol)})
        tradingOrder.update({"cumOpenAmount": self.__outputMgr.getCumOpenAmount(symbol)})
        tradingOrder.update({'detailedOrders': self.__outputMgr.getDetailedOrder(symbol)})
        tradingOrder.update({"longTriggerRatio": self.__signalExecutor.getLongTriggerRatio()})
        tradingOrder.update({"shortTriggerRatio": self.__signalExecutor.getShortTriggerRatio()})
        tradingOrder.update({"preCostDailyProfit": self.__outputMgr.getDailyProfitDict(symbol)})
        tradingOrder.update({"afterCostDailyProfit": self.__outputMgr.getAfterCostDailyProfitDict(symbol)})
        tradingOrder.update({"dailyOpenAmount": self.__outputMgr.getDailyOpenAmountDict(symbol)})
        tradingOrder.update({"dayCounts": self.__outputMgr.getDayCounts(symbol)})
        return tradingOrder

    # def __plotPredict(self, outSamplePredict):
    #     plt.figure()
    #     plt.plot(outSamplePredict)
    #     with open("Predict.json", "w") as f:
    #         Predict = {'Predict': outSamplePredict.tolist()}
    #         json.dump(Predict, f)

    def __getFactorValue(self, symbol, tagInfo, factorName):
        timestamp = tagInfo.startTimeStamp
        factorDict = self.__factorForSignalDict.get(symbol).get(timestamp)
        # If the factor name or the timestamp is not in the keys, please be careful that None will be returned.
        if factorDict is None:
            return None
        return factorDict.get(factorName)

    def __getMaAmount(self, symbol, tagInfo):
        # deprecated
        timestamp = tagInfo.startTimeStamp
        return self.__customFactorDict.get(symbol).get(timestamp)

    def __isOrderFinished(self, exchangeOrder):
        status = exchangeOrder.order_state()
        if status == 'cancelled' or status == 'filled' or status == 'partially_cancelled':
            return True
        else:
            return False

    def __calMarketCloseData(self, netPosition, lastTagInfo):
        if netPosition > 0:
            priceList = lastTagInfo.startSliceData.bidPrice
            volumeList = lastTagInfo.startSliceData.bidVolume
        else:
            priceList = lastTagInfo.startSliceData.askPrice
            volumeList = lastTagInfo.startSliceData.askVolume

        absPosition = abs(netPosition)
        accVolume = 0
        accAmount = 0
        for i in range(len(priceList)):
            temp = accVolume
            temp += volumeList[i]
            if temp >= absPosition:
                rest = absPosition - accVolume
                accAmount += rest * priceList[i]
                accVolume = absPosition
                break
            else:
                accVolume += volumeList[i]
                accAmount += volumeList[i] * priceList[i]
        if accVolume < absPosition:
            price = priceList[-1]
            if price == 0:
                for k in range(len(priceList) - 1, -1, -1):
                    if priceList[k] != 0:
                        price = priceList[k]
                if price == 0:
                    if netPosition > 0:
                        price = lastTagInfo.startSliceData.askPrice[0]
                    else:
                        price = lastTagInfo.startSliceData.bidPrice[0]
            accAmount = price * absPosition
            return price, accAmount
        else:
            price = accAmount / accVolume
            if netPosition > 0:
                return round(math.floor(price * 100) / 100, 2), accAmount
            else:
                return round(math.ceil(price * 100) / 100, 2), accAmount

    def __getOrderSide(self, BSFlag):
        if BSFlag == 'B':
            return OrderSide.Buy
        else:
            return OrderSide.Sell

    def __timeSpan(self, symbol, preTime, preTimeStamp, currTime, currTimeStamp):
        # startTime = self.__inTimeRange(preTime)
        # endTime = self.__inTimeRange(currTime)
        # if startTime == TimeRange.Morning and endTime == TimeRange.Afternoon:
        #     value = currTimeStamp - preTimeStamp - self.__noonRange.get(symbol)
        #     return value
        # else:
        return currTimeStamp - preTimeStamp

    def __inTimeRange(self, t):  # e.g. t = 93003000
        if t < self.__NOON:
            return TimeRange.Morning
        else:
            return TimeRange.Afternoon

    def __setNoonRange(self, symbol, tagInfo):
        curr_time = tagInfo.startSliceData.time
        curr_timeStamp = tagInfo.startTimeStamp
        if symbol not in self.__preTagInfo:
            return
        if self.__inTimeRange(self.__preTagInfo.get(symbol).startSliceData.time) == TimeRange.Morning \
                and self.__inTimeRange(curr_time) == TimeRange.Afternoon:
            value = curr_timeStamp - self.__preTagInfo.get(symbol).startTimeStamp
            self.__noonRange.update({symbol: value})

    def __getSymbolFromModelMgm(self, symbolIndex):
        return self.__tradingUnderlyingCode[symbolIndex]


class OrderInfo:
    def __init__(self, orderNo, isOpen):
        self.orderNo = orderNo
        self.isOpen = isOpen


class TimeRange(Enum):
    Morning = 0
    Afternoon = 1
    # Invalid = 2