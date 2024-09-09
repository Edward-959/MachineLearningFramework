import System.ReadDataFile
from VolatilityCompute import AssistFunction
import datetime as dt
import xlrd
import xlwt
from quantAPI import *
from quantEnum import *

tradeDatesFile = 'S:\TradeDates.txt'
# 读入记录日期的文本文件，这个文件中每一行是一个交易日，目前存了2013年初至2017年底的数据；读入后得到一个内容是字符串list
tradeDatesStr = open(tradeDatesFile).read().splitlines()
tradeDatesDT = [dt.datetime.strptime(tradeDatesStr[i], '%Y/%m/%d').date() for i in range(tradeDatesStr.__len__())]

startDate = dt.datetime(2017, 12, 1, 9, 30, 00)  # 注意修改开始日期
endDate = dt.datetime(2018, 1, 12, 14, 57, 00)  # 注意修改结束日期
paraStartDate = dt.date(startDate.year, startDate.month, startDate.day)
paraEndDate = dt.date(endDate.year, endDate.month, endDate.day)

paraFastLag = 10
paraSlowLag = 20

# 新建工作表，每页依次记录每天的平均波段振幅、平均分钟振幅、千三以上波段占比、平均波段价差、成交额、振幅数据
wb = xlwt.Workbook()
newSheets = [wb.add_sheet("AveAmplitude"), wb.add_sheet("AveAmplitudeMin"), wb.add_sheet("PositivePercent"),
             wb.add_sheet("AveAmpPrice"), wb.add_sheet("amt"), wb.add_sheet("swing")]

tradeDates = [t for t in tradeDatesDT if (t >= paraStartDate) and (t <= paraEndDate)]
tradingDays = tradingDay(startDate.year * 10000 + startDate.month * 100 + startDate.day, endDate.year * 10000 + endDate.month * 100 + endDate.day)
for sheet in newSheets:
    for i in range(len(tradingDays)):
        sheet.write(i+1, 0, tradingDays[i])

workbook = xlrd.open_workbook("组合股票.xlsx")  # 要计算的股票文件名称，没有行标题，第一列为股票代码
worksheet = workbook.sheet_by_name(workbook.sheet_names()[0])
Code = worksheet.col(0)

for i in range(len(Code)):
    print(i)
    # 获取指定区间的切片数据，如果该股票无数据，则跳过
    try:
        data = System.ReadDataFile.getData(Code[i].value, startDate, endDate, tradeDates, 2)
    except Exception:
        print(Code[i].value+" 无数据")
        for sheet in newSheets:
            sheet.write(0, i + 1, Code[i].value)
        continue

    result = {'AveAmplitude': [], 'AveAmpPrice': [], 'AveAmplitudeMin': [], 'PositivePercent': [], 'amt': [], 'swing': []}
    temp = []

    for dailyData in data:
        if dailyData is None:
            result['AveAmplitude'].append('NAN')
            result['AveAmplitudeMin'].append('NAN')
            result['PositivePercent'].append('NAN')
        else:
            # 平均每波振幅
            totalNum = 0
            positiveNum = 0
            midPrice = AssistFunction.MidPrice(dailyData["AskP1"], dailyData["BidP1"])
            extremePointInfo = AssistFunction.ExtremePoint(midPrice, paraFastLag, paraSlowLag)
            sumAmplitude = 0
            for info in extremePointInfo:
                sumAmplitude += abs(info[2])
                totalNum += 1
                if abs(info[2]) > 0.003:
                    positiveNum += 1
            if len(extremePointInfo) > 1:
                aveAmplitude = sumAmplitude / (len(extremePointInfo) - 1)
                positivePercent = positiveNum / totalNum
            else:
                aveAmplitude = 0
                positivePercent = 0

            # 平均每分钟振幅
            sumAmplitude = 0
            num = 0
            midPrice = AssistFunction.MidPrice(dailyData["AskP1"], dailyData["BidP1"])
            tempMin = 930
            minOpen = midPrice[0]
            minHigh = midPrice[0]
            minLow = midPrice[0]
            for j in range(1, len(midPrice)):
                if math.floor(dailyData["Time"][j] / 100000) == tempMin and dailyData["Time"][j] <= 145700000:  # 同一分钟
                    if midPrice[j] > minHigh:
                        minHigh = midPrice[j]
                    if midPrice[j] < minLow:
                        minLow = midPrice[j]
                elif math.floor(dailyData["Time"][j] / 100000) > tempMin and dailyData["Time"][
                    j] <= 145700000:  # 新一分钟开始
                    minClose = midPrice[j - 1]
                    amplitude = abs(minClose / minOpen - 1)  # amplitude = minHigh / minLow - 1
                    sumAmplitude += amplitude
                    num += 1
                    minOpen = midPrice[j]
                    minHigh = midPrice[j]
                    minLow = midPrice[j]
                    tempMin = math.floor(dailyData["Time"][j] / 100000)
                else:
                    minClose = midPrice[j - 1]
                    amplitude = abs(minClose / minOpen - 1)
                    sumAmplitude += amplitude
                    num += 1
                    break
            aveAmplitudeMin = sumAmplitude / num
            result['AveAmplitude'].append(aveAmplitude)
            result['AveAmplitudeMin'].append(aveAmplitudeMin)
            result['PositivePercent'].append(positivePercent)
    vwap = hfactor(stockList=[Code[i].value], factorList=[Factors.vwap], dateList=tradingDays)
    amt = hfactor(stockList=[Code[i].value], factorList=[Factors.amt], dateList=tradingDays)
    swing = hfactor(stockList=[Code[i].value], factorList=[Factors.swing], dateList=tradingDays)
    for j in range(len(tradingDays)):
        if vwap[0][0][1][0][j] == 0:
            result['amt'].append('NAN')
            result['swing'].append('NAN')
            result['AveAmpPrice'].append('NAN')
        else:
            result['amt'].append(amt[0][0][1][0][j])
            result['swing'].append(swing[0][0][1][0][j])
            result['AveAmpPrice'].append(vwap[0][0][1][0][j] * result['AveAmplitude'][j])

    for sheet in newSheets:
        sheet.write(0, i+1, Code[i].value)
        for j in range(len(tradingDays)):
            sheet.write(j+1, i+1, result[sheet.name][j])

wb.save("result.xls")  # 注意修改存储名称
