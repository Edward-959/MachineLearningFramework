"""
SignalExecutorOppo

Please note:
isOpenLong, isOpenShort, isCloseLong, isCloseShort can return 3 types of value:
1. bool: True, False. If True, then processSignal will be called.
2. None: False. ProcessSignal will not be called
3. dict: True. key = "price", "volume". ProcessSignal will be called and the returned value is the order value.

In this executor, the dict will be returned.

Input:
outSamplePredict[bid, ask]

by 011478
"""
from ModelSystem.SignalExecutorBase import SignalExecutorBase
from ModelSystem.Util.OrderSide import OrderSide
import datetime as dt
import math


class SignalExecutorOppoNew(SignalExecutorBase):
    def __init__(self, positionMgr, riskMgr):
        SignalExecutorBase.__init__(self, positionMgr, riskMgr)
        # constants
        self.__start_time_morning = dt.time(9, 30, 15)  # 早上开盘从该时刻起，才认为是正常的行情，开始接收早盘行情信号
        self.__start_time_afternoon = dt.time(13, 00, 15)  # 下午开盘从该时刻起，才认为是正常的行情，开始接收午盘行情信号
        self.__close_time_morning = dt.time(11, 29, 0)  # 午盘平仓时间，从该时刻起至11:30:00，进行平仓，且不发开仓委托单
        self.__easy_close_time_morning = dt.time(11, 29, 20)  # 午盘轻松平仓时间，从午盘平仓至该时刻，可用不激进的价格去平仓
        self.__MAX_QTY_PER_ORDER = 10000  # 最大单笔委托数量（下入到SignalEvaluate后，只会被可买、可卖限制，不会被流动性限制。因为内部已经对流动性进行了处理）
        self.__STOP_LOSS_RATIO = -10  # 止损参数，单位千分之，-10代表1%止损（一定是负值，因直接跟return比较）

        self.__symbol = ""
        self.__longTriggerRatio = 0
        self.__shortTriggerRatio = 0
        self.__longCloseRatio = 0
        self.__longCloseRiskRatio = 0
        self.__shortCloseRatio = 0
        self.__shortCloseRiskRatio = 0

        self.__cum_open_predictions = None
        self.__cum_open_counts = None
        self.__cum_close_long_pred = None
        self.__cum_close_long_counts = None
        self.__cum_close_short_pred = None
        self.__cum_close_short_counts = None
        self.__tickData = None
        self.__volume_today = []  # 当天行情的volume
        self.__last_tagInfo = None  # 上一个tick的tagInfo
        # new parameters
        self.__bid_predictions = []  # 存放当天的所有预测值 index 0
        self.__ask_predictions = []  # 存放当天的所有预测值 index 1
        self.__bid_predictions_delta = []  # 存放了delta预测值，即当前tick的预测值跟上一个tick预测值的差值 index 0
        self.__ask_predictions_delta = []  # 存放了delta预测值，即当前tick的预测值跟上一个tick预测值的差值 index 1
        self.__close_long_threshold = None
        self.__close_short_threshold = None
        self.__open_long_threshold = None
        self.__open_short_threshold = None
        self.__open_long_times = 0
        self.__open_short_times = 0

        self.__first_long_price = 0  # may have to adjust the assignment position
        self.__first_short_price = 0
        self.__last_long_prediction = 0
        self.__last_short_prediction = 0

        self.__order = {}  # have to reset the dict at the beginning of every tick, key = open/close side, value = (price, volume)
        self.__pre_net_position = 0  # the net position of last tick

    def generateTriggerRatio(self, symbol, backTestUnderlying, para, inSamplePredict, lastPx, absolutePath, modelName,
                             tickData):
        if tickData is None:
            raise Exception("tickData in SignalExecutorOppo is None. Please load the tickData through SignalEvaluate.")
        self.__symbol = symbol
        self.__longTriggerRatio = 0.7
        self.__shortTriggerRatio = -0.7
        self.__longCloseRatio = -0.3
        self.__longCloseRiskRatio = -0.5  # 严格平多
        self.__shortCloseRatio = 0.3
        self.__shortCloseRiskRatio = 0.5  # 严格平空

        self.__tickData = tickData

    def resetNewDay(self):
        self.__cum_open_predictions = None
        self.__cum_open_counts = None
        self.__cum_close_long_pred = None
        self.__cum_close_long_counts = None
        self.__cum_close_short_pred = None
        self.__cum_close_short_counts = None
        self.__bid_predictions = []
        self.__ask_predictions = []
        self.__bid_predictions_delta = []
        self.__ask_predictions_delta = []
        self.__close_long_threshold = None
        self.__close_short_threshold = None
        self.__open_long_threshold = None
        self.__open_short_threshold = None
        self.__open_long_times = 0
        self.__open_short_times = 0
        self.__last_tagInfo = None
        self.__volume_today = []
        self.__first_long_price = 0
        self.__first_short_price = 0
        self.__last_long_prediction = 0
        self.__last_short_prediction = 0
        self.__order = {}
        self.__pre_net_position = 0

    # onNewTick
    def updatePredictInfo(self, outSamplePredict, tagInfo):
        # if there is non finished order? will it be called?
        valid = self.__process_tickData(tagInfo)
        self.__pre_processing()
        self.__store_predictions_and_delta(outSamplePredict)
        if not valid or self._positionMgr.hasNonFinished(self.__symbol):
            return

        # 11:29:00起，进行午盘平仓，且不发开仓单
        if self.__is_close_time_morning(tagInfo):
            self.__process_morning_close(self.__symbol, tagInfo)
            return

        if self._positionMgr.isPositionClosed(self.__symbol):
            # 初始化上笔开平仓阈值
            self.__close_long_threshold = None
            self.__close_short_threshold = None
            self.__open_long_threshold = None
            self.__open_short_threshold = None
            self.__open_long_times = 0
            self.__open_short_times = 0

            # net position is 0
            if outSamplePredict[0] > self.__longTriggerRatio:
                self.__initial_open(outSamplePredict, tagInfo, OrderSide.Buy)
            elif outSamplePredict[1] < self.__shortTriggerRatio:
                self.__initial_open(outSamplePredict, tagInfo, OrderSide.Sell)
        else:
            bid0 = tagInfo.startSliceData.bidPrice[0]
            ask0 = tagInfo.startSliceData.askPrice[0]
            if self._positionMgr.isPositionNegative(self.__symbol):
                curr_return = self.__cal_return(bid0)
                delta_close_ma = 0.1 * self.__cal_ema_delta(self.__bid_predictions_delta)
                delta_open_ma = 0.1 * self.__cal_ema_delta(self.__ask_predictions_delta)

                self.__open_long_threshold = None
                self.__close_long_threshold = None
                self.__open_long_times = 0
                if outSamplePredict[0] > self.__shortCloseRiskRatio:
                    self.__cum_close_short_pred = None
                    self.__cum_close_short_counts = None
                if outSamplePredict[1] > self.__longCloseRatio:
                    self.__cum_open_predictions = None
                    self.__cum_open_counts = None
                    self.__open_short_threshold = None
                if outSamplePredict[0] > self.__cal_close_trigger(delta_close_ma):
                    self.__process_close_signal(outSamplePredict, tagInfo, OrderSide.Buy)
                elif curr_return < self.__STOP_LOSS_RATIO:
                    self.__process_stop_loss(OrderSide.Buy, outSamplePredict, tagInfo)
                elif outSamplePredict[1] < self.__cal_open_trigger(delta_open_ma):
                    self.__process_multi_open(outSamplePredict, tagInfo, OrderSide.Sell)
            elif self._positionMgr.isPositionPositive(self.__symbol):
                delta_open_ma = 0.1 * self.__cal_ema_delta(self.__bid_predictions_delta)
                delta_close_ma = 0.1 * self.__cal_ema_delta(self.__ask_predictions_delta)
                curr_return = self.__cal_return(ask0)

                self.__open_short_threshold = None
                self.__close_short_threshold = None
                self.__open_short_times = 0
                if outSamplePredict[1] < self.__longCloseRiskRatio:
                    self.__cum_close_long_pred = None
                    self.__cum_close_long_counts = None
                if outSamplePredict[0] < self.__shortCloseRatio:
                    self.__cum_open_predictions = None
                    self.__cum_open_counts = None
                    self.__open_long_threshold = None
                if outSamplePredict[1] < self.__cal_close_trigger(delta_close_ma):
                    self.__process_close_signal(outSamplePredict, tagInfo, OrderSide.Sell)
                elif curr_return < self.__STOP_LOSS_RATIO:
                    self.__process_stop_loss(OrderSide.Sell, outSamplePredict, tagInfo)
                elif outSamplePredict[0] > self.__cal_open_trigger(delta_open_ma):
                    self.__process_multi_open(outSamplePredict, tagInfo, OrderSide.Buy)
            else:
                self.__cum_open_predictions = 0
                self.__cum_open_counts = 0
        self.__pre_net_position = self._positionMgr.getNetPosition(self.__symbol)

    def isOpenLong(self, outSamplePredict, tagInfo):
        if "OpenLong" not in self.__order:
            return False
        else:
            price, volume = self.__order["OpenLong"]
            dict = {}
            dict.update({"price": price, "volume": volume})
            return dict

    def isOpenShort(self, outSamplePredict, tagInfo):
        if "OpenShort" not in self.__order:
            return False
        else:
            price, volume = self.__order["OpenShort"]
            dict = {}
            dict.update({"price": price, "volume": volume})
            return dict

    def isCloseLong(self, outSamplePredict, tagInfo):
        if "CloseLong" not in self.__order:
            return False
        else:
            price, volume = self.__order["CloseLong"]
            dict = {}
            dict.update({"price": price, "volume": volume})
            return dict

    def isCloseShort(self, outSamplePredict, tagInfo):
        if "CloseShort" not in self.__order:
            return False
        else:
            price, volume = self.__order["CloseShort"]
            dict = {}
            dict.update({"price": price, "volume": volume})
            return dict

    def getLongTriggerRatio(self):
        return self.__longTriggerRatio

    def getShortTriggerRatio(self):
        return self.__shortTriggerRatio

    # 通过对上一个净头寸和当前净头寸的变动进行辨别开平方向
    def __pre_processing(self):
        self.__order = {}
        last_net_position = int(self.__pre_net_position)
        curr_net_position = int(self._positionMgr.getNetPosition(self.__symbol))

        # if last_net_position >= 0 and curr_net_position < 0:
        if curr_net_position < 0 <= last_net_position:
            self.__first_short_price = self._positionMgr.getFinishedOrders(self.__symbol)[-1].setPrice
            self.__cum_open_predictions = 2 * self.__last_short_prediction
            self.__cum_open_counts = 2
        # elif last_net_position < 0 and curr_net_position > 0:
        elif last_net_position < 0 < curr_net_position:
            self.__first_long_price = self._positionMgr.getFinishedOrders(self.__symbol)[-1].setPrice
            self.__cum_open_predictions = 2 * self.__last_long_prediction
            self.__cum_open_counts = 2
        elif last_net_position == 0 and curr_net_position > 0:
            self.__first_long_price = self._positionMgr.getFinishedOrders(self.__symbol)[-1].setPrice
            self.__cum_open_predictions = 2 * self.__last_long_prediction
            self.__cum_open_counts = 2

        # if last_net_position > 0 and curr_net_position < 0 or last_net_position < 0 and curr_net_position > 0 or curr_net_position == 0:
        if curr_net_position < 0 < last_net_position or last_net_position < 0 < curr_net_position or curr_net_position == 0:
            self.__cum_close_long_pred = None
            self.__cum_close_short_pred = None

    # 计算delta预测值，存放预测值和delta预测值
    def __store_predictions_and_delta(self, outSamplePredict):
        if len(self.__ask_predictions_delta) == 0:
            self.__ask_predictions_delta.append(0)
        else:
            self.__ask_predictions_delta.append(abs(outSamplePredict[1] - self.__ask_predictions[-1]))

        if len(self.__bid_predictions_delta) == 0:
            self.__bid_predictions_delta.append(0)
        else:
            self.__bid_predictions_delta.append(abs(outSamplePredict[0] - self.__bid_predictions[-1]))

        self.__ask_predictions.append(outSamplePredict[1])
        self.__bid_predictions.append(outSamplePredict[0])

    # 第一次开仓
    def __initial_open(self, outSamplePredict, tagInfo, side):
        open_long_coef = 1.0002
        open_short_coef = 0.9998
        bid_delta = self.__bid_predictions_delta[-1]
        ask_delta = self.__ask_predictions_delta[-1]
        if side == OrderSide.Buy:
            price = tagInfo.startSliceData.askPrice[0]
            self.__last_long_prediction = outSamplePredict[0]
            self.__open_long_threshold = outSamplePredict[0]
            volume = self.__cal_dynamic_open_quantity(price, side, bid_delta, outSamplePredict[0], tagInfo)
            self.__open_long_times += 1
            if volume is not None:
                price = round(price * open_long_coef, 2)
                self.__order.update({"OpenLong": (price, volume)})
        else:
            price = tagInfo.startSliceData.bidPrice[0]
            self.__last_short_prediction = outSamplePredict[1]
            self.__open_short_threshold = outSamplePredict[1]
            volume = self.__cal_dynamic_open_quantity(price, side, ask_delta, outSamplePredict[1], tagInfo)
            self.__open_short_times += 1
            if volume is not None:
                price = round(price * open_short_coef, 2)
                self.__order.update({"OpenShort": (price, volume)})

    def __cal_dynamic_open_quantity(self, price, side, delta, prediction, tagInfo):
        quantity = 0
        open_vol = 0
        ema = self.__ema_volume()
        vol_min = self.__MAX_QTY_PER_ORDER
        vol_range = self.__MAX_QTY_PER_ORDER * 9

        if side == OrderSide.Buy:
            vol_ratio = self.__cal_vol_ratio(delta, prediction, self.__longTriggerRatio, self.__open_long_times)
            open_vol = vol_min + vol_range * min(1, vol_ratio)
            quantity = min(self._positionMgr.getBuyAvailQty(self.__symbol), self._positionMgr.getSellAvailQty(self.__symbol),
                           max(tagInfo.startSliceData.askVolume[0], 0.5 * ema), open_vol, ema * 1.5)
        elif side == OrderSide.Sell:
            vol_ratio = self.__cal_vol_ratio(delta, prediction, self.__shortTriggerRatio, self.__open_short_times)
            open_vol = vol_min + vol_range * min(1, vol_ratio)
            quantity = min(self._positionMgr.getBuyAvailQty(self.__symbol), self._positionMgr.getSellAvailQty(self.__symbol),
                           max(tagInfo.startSliceData.bidVolume[0], 0.5 * ema), open_vol, ema * 1.5)
        return int(quantity / 100) * 100

    # 计算下单量
    def __order_quantity(self, price, side, tagInfo):
        volume = 0
        ema = self.__ema_volume()
        if side == OrderSide.Buy:
            volume = min(self._positionMgr.getBuyAvailQty(self.__symbol),
                         self._positionMgr.getSellAvailQty(self.__symbol),
                         max(tagInfo.startSliceData.askVolume[0], ema * 0.5),
                         self.__MAX_QTY_PER_ORDER, 1.5 * ema)
        elif side == OrderSide.Sell:
            volume = min(self._positionMgr.getBuyAvailQty(self.__symbol),
                         self._positionMgr.getSellAvailQty(self.__symbol),
                         max(tagInfo.startSliceData.bidVolume[0], ema * 0.5),
                         self.__MAX_QTY_PER_ORDER, 1.5 * ema)
        return int(volume / 100) * 100

    # 计算连续开仓下单量
    def __cal_multi_dynamic_open_quantity(self, side, price, prediction, delta, tagInfo):
        volume = self.__cal_dynamic_open_quantity(price, side, delta, prediction, tagInfo)
        ema = self.__ema_volume()
        if volume is not None:
            net_position = self._positionMgr.getNetPosition(self.__symbol)
            limit = min(20 * self.__MAX_QTY_PER_ORDER, max(4 * ema, 5 * self.__MAX_QTY_PER_ORDER))
            if abs(net_position) + volume > limit:
                volume = limit - abs(net_position)
                if volume <= 0:
                    return None
                else:
                    return int(volume / 100) * 100
            else:
                return volume
        else:
            return None

    # ema成交量
    def __ema_volume(self):
        alpha = 0.95
        ema = 0
        if self.__volume_today is None or len(self.__volume_today) == 0:
            return ema
        length = len(self.__volume_today)
        start = max(0, length - 50)
        ema = self.__volume_today[start]
        for i in range(start + 1, length):
            ema = self.__cal_ema(alpha, ema, self.__volume_today[i])
        return ema + 100

    def __ema_volume_new(self):
        if self.__volume_today is None or len(self.__volume_today) == 0:
            return 0
        else:
            value = self.__volume_today[0]
            length = len(self.__volume_today)
            if length == 1:
                return value
            else:
                sub_list = self.__volume_today[max(0, length - 40) + 1:]
                for new_value in sub_list:
                    value = self.__cal_ema_new(value, new_value)
                return value

    def __cal_ema_new(self, old_ema, value):
        return old_ema + (0.05 * (value - old_ema))

    # 计算开仓阈值
    def __cal_open_trigger(self, delta_open_ma):
        open_th = 0
        if self._positionMgr.isPositionNegative(self.__symbol):
            open_short_threshold = self.__open_short_threshold
            if open_short_threshold is None:
                open_th = self.__shortTriggerRatio
            else:
                open_th = open_short_threshold - delta_open_ma
        if self._positionMgr.isPositionPositive(self.__symbol):
            open_long_threshold = self.__open_long_threshold
            if open_long_threshold is None:
                open_th = self.__longTriggerRatio
            else:
                open_th = open_long_threshold + delta_open_ma
        return open_th

    # 计算平仓阈值，NEW方法
    def __cal_close_trigger(self, delta_close_ma):
        close_th = 0
        if self._positionMgr.isPositionNegative(self.__symbol):
            close_short_threshold = self.__close_short_threshold
            if close_short_threshold is None:
                close_th = self.__shortCloseRatio
            else:
                close_th = close_short_threshold + delta_close_ma
            if close_th > self.__shortCloseRiskRatio:
                close_th = self.__shortCloseRiskRatio
        elif self._positionMgr.isPositionPositive(self.__symbol):
            close_long_threshold = self.__close_long_threshold
            if close_long_threshold is None:
                close_th = self.__longCloseRatio
            else:
                close_th = close_long_threshold - delta_close_ma
            if close_th < self.__longCloseRiskRatio:
                close_th = self.__longCloseRiskRatio
        return close_th

    # 处理平仓信号
    def __process_close_signal(self, outSamplePredict, tagInfo, side):
        close_long_coef = 0.9998
        close_short_coef = 1.0002
        bid0 = tagInfo.startSliceData.bidPrice[0]
        ask0 = tagInfo.startSliceData.askPrice[0]
        close_price = 0

        volume_ema = self.__ema_volume()
        net_position = self._positionMgr.getNetPosition(self.__symbol)
        volume_close = min(abs(net_position), self.__MAX_QTY_PER_ORDER * 10, 2.5 * volume_ema)
        if side == OrderSide.Buy:
            if self.__cum_close_short_pred is None:
                self.__cum_close_short_pred = 2 * outSamplePredict[0]
                self.__cum_close_short_counts = 2
            else:
                self.__cum_close_short_pred += outSamplePredict[0]
                self.__cum_close_short_counts += 1
            if outSamplePredict[0] > self.__longTriggerRatio:
                volume = self.__order_quantity(ask0, OrderSide.Buy, tagInfo)
                self.__open_long_times += 1
                close_price = ask0 * close_short_coef
                if volume is not None:
                    volume += abs(net_position)
                    volume = math.ceil(volume / 100) * 100
                    self.__last_long_prediction = outSamplePredict[0]
                    self.__open_long_threshold = outSamplePredict[0]
                    self.__order.update({"CloseShort": (close_price, volume)})
            else:
                if outSamplePredict[0] > self.__shortCloseRiskRatio:
                    close_price = ask0 * close_short_coef
                elif self.__close_short_threshold is None:
                    close_price = self.__close_price(outSamplePredict, tagInfo)
                else:
                    close_price = ask0
                # volume = math.ceil(volume_close / 100) * 100
                volume = volume_close
                self.__order.update({"CloseShort": (close_price, volume)})
                self.__close_short_threshold = outSamplePredict[0]
        else:
            if self.__cum_close_long_pred is None:
                self.__cum_close_long_pred = 2 * outSamplePredict[1]
                self.__cum_close_long_counts = 2
            else:
                self.__cum_close_long_pred += outSamplePredict[1]
                self.__cum_close_long_counts += 1
            if outSamplePredict[1] < self.__shortTriggerRatio:
                volume = self.__order_quantity(bid0, OrderSide.Sell, tagInfo)
                self.__open_short_times += 1
                close_price = bid0 * close_long_coef
                if volume is not None:
                    volume += abs(net_position)
                    volume = math.ceil(volume / 100) * 100
                    self.__last_short_prediction = outSamplePredict[1]
                    self.__open_short_threshold = outSamplePredict[1]
                    self.__order.update({"CloseLong": (close_price, volume)})
            else:
                if outSamplePredict[1] < self.__longCloseRiskRatio:
                    close_price = bid0 * close_long_coef
                elif self.__close_long_threshold is None:
                    close_price = self.__close_price(outSamplePredict, tagInfo)
                else:
                    close_price = bid0
                # volume = math.ceil(volume_close / 100) * 100
                volume = volume_close
                self.__order.update({"CloseLong": (close_price, volume)})
                self.__close_long_threshold = outSamplePredict[1]

    # 处理连续开仓信号
    def __process_multi_open(self, outSamplePredict, tagInfo, side):
        open_long_coef = 1.0002
        open_short_coef = 0.9998
        bid0 = tagInfo.startSliceData.bidPrice[0]
        ask0 = tagInfo.startSliceData.askPrice[0]
        bid_delta = self.__bid_predictions_delta[-1]
        ask_delta = self.__ask_predictions_delta[-1]
        volume = 0
        open_price = 0

        if side == OrderSide.Buy:
            if self.__cum_open_predictions is None:
                self.__cum_open_predictions = 2 * outSamplePredict[0]
                self.__cum_open_counts = 2
            else:
                self.__cum_open_predictions += outSamplePredict[0]
                self.__cum_open_counts += 1

            open_price = ask0 * open_long_coef
            volume = self.__cal_multi_dynamic_open_quantity(side, ask0, outSamplePredict[0], bid_delta, tagInfo)
            if volume is not None:
                self.__order.update({"OpenLong": (open_price, volume)})
            self.__open_long_threshold = outSamplePredict[0]
            self.__open_long_times += 1
        else:  # OrderSide.Sell
            if self.__cum_open_predictions is None:
                self.__cum_open_predictions = 2 * outSamplePredict[1]
                self.__cum_open_counts = 2
            else:
                self.__cum_open_predictions += outSamplePredict[1]
                self.__cum_open_counts += 1

            open_price = bid0 * open_short_coef
            volume = self.__cal_multi_dynamic_open_quantity(side, bid0, outSamplePredict[1], ask_delta, tagInfo)
            if volume is not None:
                self.__order.update({"OpenShort": (open_price, volume)})
            self.__open_short_threshold = outSamplePredict[1]
            self.__open_short_times += 1

    # 计算平仓价格
    def __close_price(self, outSamplePredict, tagInfo):
        bid = outSamplePredict[0]
        ask = outSamplePredict[1]
        bid0 = tagInfo.startSliceData.bidPrice[0]
        ask0 = tagInfo.startSliceData.askPrice[0]
        price = 0

        if self._positionMgr.isPositionPositive(self.__symbol):
            if ask < self.__shortTriggerRatio:
                price = bid0
            else:
                price = max(ask0 - 0.02, bid0)
        elif self._positionMgr.isPositionNegative(self.__symbol):
            if bid > self.__longTriggerRatio:
                price = ask0
            else:
                price = min(bid0 + 0.02, ask0)
        return price

    def __process_stop_loss(self, side, outSamplePredict, tagInfo):
        ema = self.__ema_volume()
        net_position = self._positionMgr.getNetPosition(self.__symbol)
        close_vol = min(abs(net_position), self.__MAX_QTY_PER_ORDER * 5, ema * 2.5)
        if side == OrderSide.Buy:
            price = self.__close_price(outSamplePredict, tagInfo)
            self.__order.update({'CloseShort': (price, close_vol)})
        else:
            price = self.__close_price(outSamplePredict, tagInfo)
            self.__order.update({'CloseLong': (price, close_vol)})

    # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    # some simple helper functions
    # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    def __cal_vol_ratio(self, delta, prediction, base, times):
        return abs(prediction) * abs(delta) / (abs(base) + 0.1) / (times + 1)

    # 计算当前收益率
    def __cal_return(self, price):
        curr_return = 0
        if self._positionMgr.isPositionPositive(self.__symbol):
            open_price = self.__first_long_price
            if open_price is not None and open_price != 0:
                curr_return = (price - open_price) / open_price * 1000
        elif self._positionMgr.isPositionNegative(self.__symbol):
            open_price = self.__first_short_price
            if open_price is not None and open_price != 0:
                curr_return = (open_price - price) / open_price * 1000
        return curr_return

    def __cal_ema(self, alpha, ema, value):
        return alpha * ema + (1 - alpha) * value

    def __cal_ema_delta(self, delta_list):
        delta = 0
        if delta_list is None or len(delta_list) == 0:
            return delta

        length = len(delta_list)
        for i in range(max(0, length - 4), length):
            delta = 0.75 * delta + 0.25 * delta_list[i]
        return delta
    # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

    # onNewTick 数据预处理，从tickData获取当日的volume，以便计算ema成交量
    def __process_tickData(self, tagInfo):
        valid = True  # 标识符，如果行情没有在合理tick，比如9:30:00到9:30:15则会直接return至SignalEvaluate
        tick_timestamp = tagInfo.startTimeStamp
        tick_datetime = dt.datetime.fromtimestamp(tick_timestamp)
        if len(self.__volume_today) == 0:
            date_index = 0
            for i in range(len(self.__tickData)):
                if dt.datetime.fromtimestamp(self.__tickData[i]["TimeStamp"][0]).date() == tick_datetime.date():
                    date_index = i
                    break
            tick_index = 0
            for i in range(len(self.__tickData[date_index]["TimeStamp"])):
                if self.__tickData[date_index]["TimeStamp"][i] >= tick_timestamp:  # float type >=
                    tick_index = i  # index is first valid
                    break
            start_index = 0
            for i in range(len(self.__tickData[date_index]["TimeStamp"])):
                if dt.datetime.fromtimestamp(
                        self.__tickData[date_index]["TimeStamp"][i]).time() >= self.__start_time_morning:
                    start_index = i
                    break
            for i in range(start_index, tick_index + 1):
                pre_acc_volume = self.__tickData[date_index]["AccVolume"][i - 1]
                cur_acc_volume = self.__tickData[date_index]["AccVolume"][i]
                self.__volume_today.append(cur_acc_volume - pre_acc_volume)
        if self.__last_tagInfo is not None:
            if self.__start_time_morning <= tick_datetime.time() < dt.time(11,30,0) or self.__start_time_afternoon <= tick_datetime.time() < dt.time(14, 57, 0):
                if dt.datetime.fromtimestamp(
                        self.__last_tagInfo.startTimeStamp).time() < self.__start_time_afternoon <= tick_datetime.time():
                    self.__volume_today.append(tagInfo.startSliceData.volume)
                else:
                    pre_acc_volume = self.__last_tagInfo.startSliceData.totalVolume
                    cur_acc_volume = tagInfo.startSliceData.totalVolume
                    self.__volume_today.append(cur_acc_volume - pre_acc_volume)
            else:
                valid = False
        self.__last_tagInfo = tagInfo
        return valid

    # 以下为处理午盘平仓的逻辑
    # 判断时间是否在午盘平仓区间，返回boolean，若True，则可以在onNewTick中，直接返回，不再进行开平仓逻辑的处理
    def __is_close_time_morning(self, tagInfo):
        tick_timestamp = tagInfo.startTimeStamp
        if self.__close_time_morning <= dt.datetime.fromtimestamp(tick_timestamp).time() <= dt.time(11, 30, 0):
            return True
        else:
            return False

    # 若在午盘平仓区间，则处理头寸
    def __process_morning_close(self, symbol, tagInfo):
        if self._positionMgr.isPositionClosed(symbol):
            return
        netPosition = self._positionMgr.getNetPosition(symbol)
        volLimit = netPosition / 5
        ema = self.__ema_volume()
        quantity = min(max(ema * 5, volLimit), netPosition)

        # if netPosition > 0:
        #     positionQty = int(quantity / 100) * 100
        # else:
        #     positionQty = int(-quantity / 100) * 100
        positionQty = abs(int(quantity))

        ask0 = tagInfo.startSliceData.askPrice[0]
        bid0 = tagInfo.startSliceData.bidPrice[0]

        isCloseAtEase = False
        if dt.datetime.fromtimestamp(tagInfo.startTimeStamp).time() < self.__easy_close_time_morning:
            isCloseAtEase = True
        if netPosition > 0:
            if isCloseAtEase:
                price = max(ask0 - 0.02, bid0)
            else:
                price = bid0
            self.__order.update({"CloseLong": (price, positionQty)})
        else:
            if isCloseAtEase:
                price = min(bid0 + 0.02, ask0)
            else:
                price = ask0
            self.__order.update({"CloseShort": (price, positionQty)})

# end of file
