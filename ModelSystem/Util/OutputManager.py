"""
Handles the output in SignalEvaluate
Use "addOrder" when an order is finished
Use "registerOutput" when position is closed: to integrate one trading deal
Get the info you want, then output the results

by 011478

@revise: 011478
on 20180910: 将多空翻转的交易，从统计中拆开（策略中仍为一笔订单），e.g. 多空，在统计输出时拆为多平和开空两笔订单
"""
import math
import datetime as dt


class OutputManager:
    def __init__(self, cost):
        self.__nonClosedOrderDict = {}  # 存入没有平仓的order; key = symbol, value = list
        self.__orderDict = {}  # key = symbol, value = list
        self.__detailedOrderDict = {}  # key = symbol, value = list
        self.__totalProfitDict = {}  # key = symbol, value = float
        self.__dailyInfoDict = {}  # key = symbol, value = dict: key = date, value = DailyInfo
        self.__cumOpenAmount = {}  # key = symbol, value = float
        self.__dayCounts = {}  # key = symbol, value = int
        self.__splited_cum_qty = {}  # key = symbol, value = tuple: closed position and open position
        self.__COST = cost

    def clearNonClosed(self, symbol):
        if symbol not in self.__detailedOrderDict:
            self.__detailedOrderDict.update({symbol: []})
        self.__updateDetailed(symbol)
        self.__nonClosedOrderDict.update({symbol: []})

    def addOrder(self, exchangeOrder, split_reversed_cum_qty):
        symbol = exchangeOrder.code
        if symbol not in self.__nonClosedOrderDict:
            self.__nonClosedOrderDict.update({symbol: []})
        self.__nonClosedOrderDict.get(symbol).append(exchangeOrder)
        if split_reversed_cum_qty is not None:
            self.__splited_cum_qty.update({exchangeOrder.orderNumber: split_reversed_cum_qty})
            self.__doOutput(symbol, exchangeOrder.orderTime.timestamp())
            self.__nonClosedOrderDict.get(symbol).append(exchangeOrder)

    def registerOutput(self, symbol, startTimeStamp):
        if symbol not in self.__nonClosedOrderDict or len(self.__nonClosedOrderDict.get(symbol)) == 0:
            return
        else:
            self.__doOutput(symbol, startTimeStamp)

    def __doOutput(self, symbol, startTimeStamp):
        if symbol not in self.__orderDict:
            self.__orderDict.update({symbol: []})
        if symbol not in self.__detailedOrderDict:
            self.__detailedOrderDict.update({symbol: []})
        size = len(self.__nonClosedOrderDict.get(symbol))
        # make sure there are two directions
        process = False
        direction = self.__nonClosedOrderDict.get(symbol)[0].BSFlag
        for i in range(size):
            if self.__nonClosedOrderDict.get(symbol)[i].BSFlag != direction:
                process = True
                break
        if not process:
            self.clearNonClosed(symbol)
            return

        # update the self.__orderDict
        sumOpenAmountCum = 0
        sumOpenAmountOrder = 0
        sumCloseAmount = 0
        sumOpenVolume = 0
        sumCloseVolume = 0
        tempOrder = {}
        for i in range(size):
            exchangeOrder = self.__nonClosedOrderDict.get(symbol)[i]
            if i == 0:
                tempOrder.update({'code': symbol})
                tempOrder.update({'startTime': exchangeOrder.orderTime.strftime('%m/%d/%y-%H:%M:%S')})
                if direction == 'B':
                    tempOrder.update({'direction': 'long '})
                else:
                    tempOrder.update({'direction': 'short'})
                tempOrder.update({'startPrice': exchangeOrder.setPrice})
                if exchangeOrder.orderNumber in self.__splited_cum_qty:
                    cum_qty_close = self.__splited_cum_qty.get(exchangeOrder.orderNumber)[0]
                    cum_qty_open = self.__splited_cum_qty.get(exchangeOrder.orderNumber)[1]
                    sumOpenAmountCum += cum_qty_open * exchangeOrder.price()
                    sumOpenAmountOrder += exchangeOrder.setPrice * (exchangeOrder.setVolume - cum_qty_close)
                    sumOpenVolume += cum_qty_open
                else:
                    sumOpenAmountCum += exchangeOrder.accMount
                    sumOpenAmountOrder += exchangeOrder.setPrice * exchangeOrder.setVolume
                    sumOpenVolume += exchangeOrder.volume
            elif i == size - 1:
                tempOrder.update({'endPrice': exchangeOrder.setPrice})
                tempOrder.update({'endTime': exchangeOrder.orderTime.strftime('%m/%d/%y-%H:%M:%S')})
                if exchangeOrder.BSFlag == direction:
                    if exchangeOrder.orderNumber in self.__splited_cum_qty:
                        cum_qty_close = self.__splited_cum_qty.get(exchangeOrder.orderNumber)[0]
                        sumOpenAmountCum += cum_qty_close * exchangeOrder.price()
                        sumOpenAmountOrder += exchangeOrder.setPrice * cum_qty_close
                        sumOpenVolume += cum_qty_close
                    else:
                        sumOpenAmountCum += exchangeOrder.accMount
                        sumOpenAmountOrder += exchangeOrder.setPrice * exchangeOrder.setVolume
                        sumOpenVolume += exchangeOrder.volume
                else:
                    if exchangeOrder.orderNumber in self.__splited_cum_qty:
                        cum_qty_close = self.__splited_cum_qty.get(exchangeOrder.orderNumber)[0]
                        sumCloseAmount += cum_qty_close * exchangeOrder.price()
                        sumCloseVolume += cum_qty_close
                    else:
                        sumCloseAmount += exchangeOrder.accMount
                        sumCloseVolume += exchangeOrder.volume
            else:
                if exchangeOrder.BSFlag == direction:
                    # open side
                    sumOpenAmountCum += exchangeOrder.accMount
                    sumOpenAmountOrder += exchangeOrder.setPrice * exchangeOrder.setVolume
                    sumOpenVolume += exchangeOrder.volume
                else:
                    # close side
                    sumCloseAmount += exchangeOrder.accMount
                    sumCloseVolume += exchangeOrder.volume
        returnInfo = self.__calReturn(symbol, sumOpenAmountCum, sumCloseAmount, direction, startTimeStamp)
        if returnInfo is None:
            self.clearNonClosed(symbol)
            return
        tempOrder.update({'orderAmount': sumOpenAmountOrder})
        tempOrder.update({'cumAmount': sumOpenAmountCum})
        tempOrder.update({'returnRate': returnInfo.returnRate})
        tempOrder.update({'afterCostProfit': returnInfo.afterCostProfit})
        self.__orderDict.get(symbol).append(tempOrder)
        self.clearNonClosed(symbol)

    def __updateDetailed(self, symbol):
        combinedOrder = []
        if symbol not in self.__nonClosedOrderDict or len(self.__nonClosedOrderDict.get(symbol)) == 0:
            return
        else:
            for i in range(len(self.__nonClosedOrderDict.get(symbol))):
                exchangeOrder = self.__nonClosedOrderDict.get(symbol)[i]
                tempOrder = {}
                tempOrder.update({'code': symbol})
                tempOrder.update({'orderTime': exchangeOrder.orderTime.strftime('%m/%d/%y-%H:%M:%S')})
                if exchangeOrder.BSFlag == 'B':
                    tempOrder.update({'direction': 'long '})
                else:
                    tempOrder.update({'direction': 'short'})
                tempOrder.update({'price': exchangeOrder.setPrice})
                tempOrder.update({'avgPrice': exchangeOrder.price()})
                tempOrder.update({'status': exchangeOrder.order_state()})
                if exchangeOrder.orderNumber in self.__splited_cum_qty:
                    if i == 0:
                        cum_qty_close = self.__splited_cum_qty.get(exchangeOrder.orderNumber)[0]
                        cum_qty_open = self.__splited_cum_qty.get(exchangeOrder.orderNumber)[1]
                        tempOrder.update({'quantity': exchangeOrder.setVolume - cum_qty_close})
                        tempOrder.update({'cumQty': cum_qty_open})
                        orderAmount = (exchangeOrder.setVolume - cum_qty_close) * exchangeOrder.setPrice
                        tempOrder.update({'orderAmount': round(orderAmount, 2)})
                        tempOrder.update({'cumAmount': exchangeOrder.price() * cum_qty_open})
                    else:
                        cum_qty_close = self.__splited_cum_qty.get(exchangeOrder.orderNumber)[0]
                        tempOrder.update({'quantity': cum_qty_close})
                        tempOrder.update({'cumQty': cum_qty_close})
                        orderAmount = cum_qty_close * exchangeOrder.setPrice
                        tempOrder.update({'orderAmount': round(orderAmount, 2)})
                        tempOrder.update({'cumAmount': exchangeOrder.price() * cum_qty_close})
                else:
                    tempOrder.update({'quantity': exchangeOrder.setVolume})
                    tempOrder.update({'cumQty': exchangeOrder.volume})
                    orderAmount = exchangeOrder.setVolume * exchangeOrder.setPrice
                    tempOrder.update({'orderAmount': round(orderAmount, 2)})
                    tempOrder.update({'cumAmount': exchangeOrder.accMount})
                combinedOrder.append(tempOrder)
            self.__detailedOrderDict.get(symbol).append(combinedOrder)

    def __calReturn(self, symbol, sumOpenAmountCum, sumCloseAmount, direction, startTimeStamp):
        if symbol not in self.__totalProfitDict:
            self.__totalProfitDict.update({symbol: 0})
        if symbol not in self.__cumOpenAmount:
            self.__cumOpenAmount.update({symbol: 0})
        if symbol not in self.__dailyInfoDict:
            self.__dailyInfoDict.update({symbol: {}})
        # benchmark = 100
        # openVolumeFloor = self.__floorFun(sumOpenVolume)
        # closeVolumeFloor = self.__floorFun(sumCloseVolume)
        # if openVolumeFloor == 0 and closeVolumeFloor == 0:
        #     return None
        # if openVolumeFloor == 0:
        #     benchmark = closeVolumeFloor
        # elif closeVolumeFloor == 0:
        #     benchmark = openVolumeFloor
        # else:
        #     benchmark = min(openVolumeFloor, closeVolumeFloor)
        # if sumOpenVolume != benchmark:
        #     adjustedOpenAmount = sumOpenAmountCum / sumOpenVolume * benchmark
        # else:
        #     adjustedOpenAmount = sumOpenAmountCum
        # if sumCloseVolume != benchmark:
        #     adjustedCloseAmount = sumCloseAmount / sumCloseVolume * benchmark
        # else:
        #     adjustedCloseAmount = sumCloseAmount
        adjustedOpenAmount = sumOpenAmountCum
        adjustedCloseAmount = sumCloseAmount
        tempCumOpenAmount = self.__cumOpenAmount.get(symbol)
        tempCumOpenAmount += adjustedOpenAmount
        self.__cumOpenAmount.update({symbol: tempCumOpenAmount})

        date = dt.datetime.fromtimestamp(startTimeStamp).date()
        if date not in self.__dailyInfoDict.get(symbol):
            self.__dailyInfoDict.get(symbol).update({date: DailyInfo(0, 0)})

        dailyInfo = self.__dailyInfoDict.get(symbol).get(date)
        profit = self.__totalProfitDict.get(symbol)
        if direction == 'B':
            earning = adjustedCloseAmount - adjustedOpenAmount
            profit += earning
            dailyInfo.dailyProfit += earning
            dailyInfo.dailyOpenAmount += adjustedOpenAmount
            self.__dailyInfoDict.get(symbol).update({date: dailyInfo})
            self.__totalProfitDict.update({symbol: profit})
            afterCostEarning = earning - self.__COST * adjustedOpenAmount
            # afterCostReturnRate = afterCostEarning / adjustedOpenAmount
            returnRate = round(adjustedCloseAmount / adjustedOpenAmount - 1, 5)
            return ReturnInfo(round(afterCostEarning, 2), round(returnRate, 5))
        else:
            earning = adjustedOpenAmount - adjustedCloseAmount
            profit += earning
            dailyInfo.dailyProfit += earning
            dailyInfo.dailyOpenAmount += adjustedOpenAmount
            self.__dailyInfoDict.get(symbol).update({date: dailyInfo})
            self.__totalProfitDict.update({symbol: profit})
            afterCostEarning = earning - self.__COST * adjustedOpenAmount
            # afterCostReturnRate = afterCostEarning / adjustedOpenAmount
            returnRate = round(1 - adjustedCloseAmount / adjustedOpenAmount, 5)
            return ReturnInfo(round(afterCostEarning, 2), round(returnRate, 5))

    def __floorFun(self, x):
        return math.floor(x / 100) * 100

    # def getDateCounts(self, symbol):
    #     if symbol not in self.__dailyInfoDict:
    #         return 0
    #     else:
    #         return len(self.__dailyInfoDict.get(symbol).keys())

    def addOneDay(self, symbol):
        if symbol not in self.__dayCounts:
            self.__dayCounts.update({symbol: 1})
        else:
            self.__dayCounts[symbol] += 1

    def getDayCounts(self, symbol):
        if symbol not in self.__dayCounts:
            return 0
        else:
            return self.__dayCounts.get(symbol)

    def getProfit(self, symbol):
        if symbol not in self.__totalProfitDict:
            return 0
        else:
            return round(self.__totalProfitDict.get(symbol), 2)

    def getCumOpenAmount(self, symbol):
        if symbol not in self.__cumOpenAmount:
            return 0
        else:
            return round(self.__cumOpenAmount.get(symbol), 2)

    def getOrder(self, symbol):
        if symbol not in self.__orderDict:
            return []
        else:
            return self.__orderDict.get(symbol)

    def getDetailedOrder(self, symbol):
        if symbol not in self.__detailedOrderDict:
            return []
        else:
            return self.__detailedOrderDict.get(symbol)

    def getDailyProfitDict(self, symbol):
        if symbol not in self.__dailyInfoDict:
            return {}
        else:
            dict = {}
            for date in self.__dailyInfoDict.get(symbol).keys():
                dict.update({str(date): round(self.__dailyInfoDict.get(symbol).get(date).dailyProfit, 2)})
            return dict

    def getAfterCostDailyProfitDict(self, symbol):
        if symbol not in self.__dailyInfoDict:
            return {}
        else:
            dict = {}
            for date in self.__dailyInfoDict.get(symbol).keys():
                dailyProfit = self.__dailyInfoDict.get(symbol).get(date).dailyProfit
                dailyOpenAmount = self.__dailyInfoDict.get(symbol).get(date).dailyOpenAmount
                afterCostProfit = dailyProfit - self.__COST * dailyOpenAmount
                dict.update({str(date): round(afterCostProfit, 2)})
            return dict

    def getDailyOpenAmountDict(self, symbol):
        if symbol not in self.__dailyInfoDict:
            return {}
        else:
            dict = {}
            for date in self.__dailyInfoDict.get(symbol).keys():
                dict.update({str(date): round(self.__dailyInfoDict.get(symbol).get(date).dailyOpenAmount, 2)})
            return dict


class DailyInfo:
    def __init__(self, dailyProfit, dailyOpenAmount):
        self.dailyProfit = dailyProfit
        self.dailyOpenAmount = dailyOpenAmount


class ReturnInfo:
    # profit is after cost; return rate is pre-cost
    def __init__(self, afterCostProfit, returnRate):
        self.afterCostProfit = afterCostProfit
        self.returnRate = returnRate
