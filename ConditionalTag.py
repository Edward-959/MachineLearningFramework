"""
用于找到满足特定条件的Tag，并输出到EXCEL中，便于分析
PickleName为需要分析的文件名称
Condition为特定因子需要满足的条件
Time为开仓时间段需要满足的条件
MainTag为用于避免重复开仓的Tag

@author:006688
"""
import pickle
import xlwt
import datetime as dt


def ConditionalTag(PickleName, Condition, Time=None, MainTag=None):
    outputFactor, outputSubTag, tradingUnderlyingCode, factorName = pickle.load(open(PickleName + '.pickle', 'rb'))
    outputFactorNew = []
    outputSubTagNew = []
    # 记录因子名称在输出因子列表中的对应序号
    factorNo = {}
    for factor in list(Condition.keys()):
        factorNo.update({factor: factorName.index(factor)})
    # 对每个切片的记录依次进行判断
    for i in range(len(outputFactor)):
        outputFactorTemp = []
        outputSubTagTemp = []
        for j in range(len(outputFactor[i])):
            conditionJudge = True
            # 时间条件判断
            if Time is not None:
                time = outputSubTag[i][j]["1min"].startSliceData.time
                if not eval(Time):
                    conditionJudge = False
            # 避免重复开仓
            if MainTag is not None:
                if len(outputSubTagTemp) > 0:
                    if outputSubTag[i][j][MainTag].startSliceData.time <= outputSubTagTemp[-1][MainTag].endSliceData.time:
                        conditionJudge = False
            # 因子值条件判断
            for factor in list(Condition.keys()):
                val = outputFactor[i][j][factorNo[factor]]
                if not eval(Condition[factor]):
                    conditionJudge = False
                    break
            if conditionJudge:
                outputFactorTemp.append(outputFactor[i][j])
                outputSubTagTemp.append(outputSubTag[i][j])
        outputFactorNew.append(outputFactorTemp)
        outputSubTagNew.append(outputSubTagTemp)
    return outputFactorNew, outputSubTagNew, tradingUnderlyingCode, factorName


# 以下为使用方法
# 先运行Main将因子和Tag的计算结果保存成pickle文件
timeCondition = "93000000 < time < 103000000"
factorCondition = {"factorSpeed": "val > 0",
                   "factorPierceNum": "val < 0"}
mainTag = "1min"
pickleName = "strategy1"
factorNew, subTagNew, tradingCode, factorName = ConditionalTag(pickleName, factorCondition, timeCondition, mainTag)

style0 = xlwt.easyxf('font: name Times New Roman, color-index red, bold on')
style1 = xlwt.easyxf(num_format_str='YY/MM/DD HH:MM:SS')

wb = xlwt.Workbook()
sheet = wb.add_sheet("test")
sheet.write(0, 0, "TimeStamp", style0)
column = 0
tagName = list(subTagNew[0][0].keys())
for name in factorName:
    column += 1
    sheet.write(0, column, name, style0)
for name in tagName:
    column += 1
    sheet.write(0, column, name, style0)
for row in range(len(factorNew[0])):
    sheet.write(row + 1, 0, dt.datetime.fromtimestamp(subTagNew[0][row]["1min"].startTimeStamp), style1)
    column = 0
    for factorValue in factorNew[0][row]:
        column += 1
        sheet.write(row + 1, column, factorValue)
    for tag in tagName:
        column += 1
        sheet.write(row + 1, column, subTagNew[0][row][tag].returnRate)
wb.save(pickleName+'.xls')
