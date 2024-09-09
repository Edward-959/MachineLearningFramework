import numpy as np


def MidPrice(askP1, bidP1):
    result = []
    for i in range(len(askP1)):
        if askP1[i] == 0:
            value = bidP1[i]
        elif bidP1[i] == 0:
            value = askP1[i]
        else:
            value = (bidP1[i] + askP1[i]) / 2
        result.append(value)
    return result


def EMA(data, paraLag):
    Value = [data[0]]
    for i in range(1, len(data)):
        if paraLag is None or i + 1 <= paraLag:
            newValue = Value[i - 1] + 2 / (i + 2) * (data[i] - Value[i - 1])
        else:
            newValue = Value[i - 1] + 2 / (paraLag + 1) * (data[i] - Value[i - 1])
        Value.append(newValue)
    return Value


def ExtremePoint(midPrice, paraFastLag, paraSlowLag):
    emaPriceFast = EMA(midPrice, paraFastLag)
    emaPriceSlow = EMA(midPrice, paraSlowLag)
    direction = np.array(emaPriceFast) - np.array(emaPriceSlow)
    lastExtremePointInfo = [-1, midPrice[0], 0.]
    extremePointInfo = []
    for i in range(1, len(direction)):
        if direction[i] * direction[i - 1] <= 0 and direction[i] != 0:
            if direction[i] > 0:
                tempDirection = 1
            else:
                tempDirection = -1
            lastExtremePointInfo[0] = -tempDirection
            extremePointInfo.append(lastExtremePointInfo)
            lastExtremePointInfo = [tempDirection, midPrice[i], midPrice[i] / extremePointInfo[-1][1] - 1]
        else:
            if (midPrice[i] - lastExtremePointInfo[1]) * lastExtremePointInfo[0] > 0:
                lastExtremePointInfo[1] = midPrice[i]
            if len(extremePointInfo) >= 1:
                lastExtremePointInfo[2] = lastExtremePointInfo[1] / extremePointInfo[-1][1] - 1
    return extremePointInfo
