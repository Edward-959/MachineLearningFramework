# -*- coding: utf-8 -*-
"""
Created on 2018/1/2 15:06

@author: 006547
"""
import os
import json
import xlwt


absolutePath = ""
path = absolutePath + 'ModelSaved/'
files = os.listdir(path)
style0 = xlwt.easyxf('font: name Times New Roman')
style1 = xlwt.easyxf(num_format_str='YY-MM-DD: HH-MM-SS')
wb = xlwt.Workbook()
ws = wb.add_sheet('Statistics')
ws.write(0, 0, "ModelFileName", style0)  # 写入时间戳表头
ws.write(0, 1, "ModelTestDate", style0)  # 写入时间戳表头
ws.write(0, 2, "ModelPredRatio", style0)  # 写入时间戳表头

for i in range(files.__len__()):
    if os.path.exists(path+files[i]+'/result.json'):
        with open(path+files[i]+'/result.json', 'r') as f:
            ws.write(i + 1, 0, files[i], style0)
            ws.write(i + 1, 1, files[i][22:51], style0)
            ws.write(i + 1, 2, files[i][52:], style0)
            result = json.load(f)
            keys = sorted(list(result.keys()))
            for j in range(keys.__len__()):
                if i == 0:
                    ws.write(0, j + 3, keys[j], style0)
                if keys[j] != 'order':
                    ws.write(i + 1, j + 3, result[keys[j]], style0)
                else:
                    ws.write(i + 1, j + 3, 'empty', style0)
wb.save(absolutePath+'Statistics'+'.xls')
print("Finish")
