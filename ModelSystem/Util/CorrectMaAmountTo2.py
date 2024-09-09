# -*- coding: utf-8 -*-
AFTERNOON_START_LOCAL = 130015000
AFTERNOON_START_GLOBAL = 130000000


def CorrectMaAmount(outputFactor, outputSubTag, tradingUnderlyingCode, factorMaAmountIndex):
    for ii in range(len(tradingUnderlyingCode)):
        tick_count = 0
        sum_amount = 0
        pre_total_amount = 0
        amount = 0
        isFirst = True
        for i in range(len(outputFactor[ii])):
            # factorSlice = outputFactor[ii][i]
            subTag = outputSubTag[ii][i]
            sliceData = subTag["1minMaxMin"].startSliceData

            if isFirst:
                pre_total_amount = sliceData.totalAmount
                isFirst = False
                continue

            if isValidTime(sliceData):
                tick_count += 1
                amount = sliceData.totalAmount - pre_total_amount
                sum_amount += amount
                value = sum_amount / tick_count
            else:
                if tick_count == 0:
                    value = 0
                else:
                    value = sum_amount / tick_count

            outputFactor[ii][i][factorMaAmountIndex] = value
            pre_total_amount = sliceData.totalAmount

            if sliceData.isLastSlice:
                tick_count = 0
                sum_amount = 0
                pre_total_amount = 0
                amount = 0
                isFirst = True
    return outputFactor


def isValidTime(curr_data):
    time = curr_data.time
    return time <= AFTERNOON_START_GLOBAL or time >= AFTERNOON_START_LOCAL