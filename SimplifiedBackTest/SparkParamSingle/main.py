from Utils.InputManager import InputManager
from Utils.ResultManager import ResultManager
from Utils.ThreadingManager import ThreadingManager
import Utils.HelperFunctions as hf


"""
该版本适用于XQuant的Spark并行计算环境，进行指定（唯一）阈值的多个股票计算，得到回测报告
（报告为信号文件和阈值文件的交集股票，若缺少任一文件则会报错，该股票不会生成报告，但不会影响其他股票的正常运行）
（运行完请留意是否存在traceback)
本版本暂无优化计划，300只股票的预计完成时间为1min

如果不明白参数的意义：
1. signal_csv_dir: 读取数据的路径，以SHARE_21作为参数开头！一般放置于HDFS的 共享文件夹->股票策略交易团队下，若无数据请联系011478和013050进行上传。
2. output_dir: 输出xls报告的根目录，以个人六位工号作为参数开头！具体输出时，会在目录下创建以股票代码为名字的文件夹，（固定名称的）报告则会在下一级生成。
3. executor_str: 执行的交易逻辑。具体写法请联系011478。默认为SignalExecutorTesting，与峰哥执行回测的交易逻辑完全一致，可作为benchmark。
4. trigger_json_dir: 阈值参数目录。确保该目录下的阈值文件命名规则为: symbol + '.json'。
4. symbols: 回测的股票列表，请确保signal_csv_dir中，含有股票列表的信号数据。支持单个股票。
5. init_quantities: 回测的初始股数，与symbols一一对应。如果长度不同，则会报错。支持单个股票。
6. max_tasks: 分配的计算资源/核心数，默认为200，团队最大使用数量200。

如果想要自定义方法：
1. 改变信号的均值求法: SignalManager -> def __pre_process_single
2. 改变回测的风控指标: InputManager -> def __init__ -> mock_trade_para
3. 改变param_reduction方法: InputManager -> def __my_param_reduction 请确保开平参数最终能输出一个矩阵

**4. 改变回测的方式: Please derive from SignalExecutorBase
**5. 改变阈值的评价方式: ResultManager -> def __my_best_param_solution 如果在评价时需要更多的评价指标，可以显示定义构造函数的default_keys

如果疑问请联系: 011478
"""

def main():
    # symbols = ["000001.SZ",#0
    #         "000002.SZ",#1
    #         "000060.SZ",#2
    #         "000063.SZ",#3
    #         "000069.SZ",#4
    #         "000100.SZ",#5
    #         "000157.SZ",#6
    #         "000166.SZ",#7
    #         "000333.SZ",#8
    #         "000338.SZ",#9
    #         "000402.SZ",#10
    #         "000413.SZ",#11
    #         "000415.SZ",#12
    #         "000423.SZ",#13
    #         "000425.SZ",#14
    #         "000503.SZ",#15
    #         "000538.SZ",#16
    #         "000540.SZ",#17
    #         "000559.SZ",#18
    #         "000568.SZ",#19
    #         "000623.SZ",#20
    #         "000625.SZ",#21
    #         "000627.SZ",#22
    #         "000630.SZ",#23
    #         "000651.SZ",#24
    #         "000671.SZ",#25
    #         "000709.SZ",#26
    #         "000723.SZ",#27
    #         "000725.SZ",#28
    #         "000728.SZ",#29
    #         "000768.SZ",#30
    #         "000776.SZ",#31
    #         "000783.SZ",#32
    #         "000786.SZ",#33
    #         "000792.SZ",#34
    #         "000826.SZ",#35
    #         "000839.SZ",#36
    #         "000858.SZ",#37
    #         "000876.SZ",#38
    #         "000895.SZ",#39
    #         "000898.SZ",#40
    #         "000938.SZ",#41
    #         "000959.SZ",#42
    #         "000961.SZ",#43
    #         "000963.SZ",#44
    #         "000983.SZ",#45
    #         "001965.SZ",#46
    #         "001979.SZ",#47
    #         "002007.SZ",#48
    #         "002008.SZ",#49
    #         "002024.SZ",#50
    #         "002027.SZ",#51
    #         "002044.SZ",#52
    #         "002050.SZ",#53
    #         "002065.SZ",#54
    #         "002074.SZ",#55
    #         "002081.SZ",#56
    #         "002085.SZ",#57
    #         "002142.SZ",#58
    #         "002146.SZ",#59
    #         "002153.SZ",#60
    #         "002202.SZ",#61
    #         "002230.SZ",#62
    #         "002236.SZ",#63
    #         "002241.SZ",#64
    #         "002252.SZ",#65
    #         "002294.SZ",#66
    #         "002304.SZ",#67
    #         "002310.SZ",#68
    #         "002352.SZ",#69
    #         "002385.SZ",#70
    #         "002411.SZ",#71
    #         "002415.SZ",#72
    #         "002450.SZ",#73
    #         "002456.SZ",#74
    #         "002460.SZ",#75
    #         "002466.SZ",#76
    #         "002468.SZ",#77
    #         "002470.SZ",#78
    #         "002475.SZ",#79
    #         "002493.SZ",#80
    #         "002500.SZ",#81
    #         "002508.SZ",#82
    #         "002555.SZ",#83
    #         "002558.SZ",#84
    #         "002572.SZ",#85
    #         "002594.SZ",#86
    #         "002601.SZ",#87
    #         "002602.SZ",#88
    #         "002608.SZ",#89
    #         "002624.SZ",#90
    #         "002625.SZ",#91
    #         "002673.SZ",#92
    #         "002714.SZ",#93
    #         "002736.SZ",#94
    #         "002739.SZ",#95
    #         "002797.SZ",#96
    #         "002925.SZ",#97
    #         "300003.SZ",#98
    #         "300015.SZ",#99
    #         "300017.SZ",#100
    #         "300024.SZ",#101
    #         "300027.SZ",#102
    #         "300033.SZ",#103
    #         "300059.SZ",#104
    #         "300070.SZ",#105
    #         "300072.SZ",#106
    #         "300122.SZ",#107
    #         "300124.SZ",#108
    #         "300136.SZ",#109
    #         "300144.SZ",#110
    #         "300251.SZ",#111
    #         "300408.SZ",#112
    #         "300433.SZ",#113
    #         "600000.SH",#114
    #         "600008.SH",#115
    #         "600009.SH",#116
    #         "600010.SH",#117
    #         "600011.SH",#118
    #         "600015.SH",#119
    #         "600016.SH",#120
    #         "600018.SH",#121
    #         "600019.SH",#122
    #         "600023.SH",#123
    #         "600025.SH",#124
    #         "600028.SH",#125
    #         "600029.SH",#126
    #         "600030.SH",#127
    #         "600031.SH",#128
    #         "600036.SH",#129
    #         "600038.SH",#130
    #         "600048.SH",#131
    #         "600050.SH",#132
    #         "600061.SH",#133
    #         "600066.SH",#134
    #         "600068.SH",#135
    #         "600085.SH",#136
    #         "600089.SH",#137
    #         "600100.SH",#138
    #         "600104.SH",#139
    #         "600109.SH",#140
    #         "600111.SH",#141
    #         "600115.SH",#142
    #         "600118.SH",#143
    #         "600153.SH",#144
    #         "600157.SH",#145
    #         "600170.SH",#146
    #         "600176.SH",#147
    #         "600177.SH",#148
    #         "600188.SH",#149
    #         "600196.SH",#150
    #         "600208.SH",#151
    #         "600219.SH",#152
    #         "600221.SH",#153
    #         "600233.SH",#154
    #         "600271.SH",#155
    #         "600276.SH",#156
    #         "600297.SH",#157
    #         "600309.SH",#158
    #         "600332.SH",#159
    #         "600339.SH",#160
    #         "600340.SH",#161
    #         "600346.SH",#162
    #         "600352.SH",#163
    #         "600362.SH",#164
    #         "600369.SH",#165
    #         "600372.SH",#166
    #         "600373.SH",#167
    #         "600376.SH",#168
    #         "600383.SH",#169
    #         "600390.SH",#170
    #         "600398.SH",#171
    #         "600406.SH",#172
    #         "600415.SH",#173
    #         "600436.SH",#174
    #         "600438.SH",#175
    #         "600482.SH",#176
    #         "600487.SH",#177
    #         "600489.SH",#178
    #         "600498.SH",#179
    #         "600516.SH",#180
    #         "600518.SH",#181
    #         "600519.SH",#182
    #         "600522.SH",#183
    #         "600535.SH",#184
    #         "600547.SH",#185
    #         "600549.SH",#186
    #         "600570.SH",#187
    #         "600583.SH",#188
    #         "600585.SH",#189
    #         "600588.SH",#190
    #         "600606.SH",#191
    #         "600637.SH",#192
    #         "600660.SH",#193
    #         "600663.SH",#194
    #         "600674.SH",#195
    #         "600682.SH",#196
    #         "600688.SH",#197
    #         "600690.SH",#198
    #         "600703.SH",#199
    #         "600704.SH",#200
    #         "600705.SH",#201
    #         "600739.SH",#202
    #         "600741.SH",#203
    #         "600795.SH",#204
    #         "600804.SH",#205
    #         "600809.SH",#206
    #         "600816.SH",#207
    #         "600820.SH",#208
    #         "600837.SH",#209
    #         "600867.SH",#210
    #         "600886.SH",#211
    #         "600887.SH",#212
    #         "600893.SH",#213
    #         "600900.SH",#214
    #         "600909.SH",#215
    #         "600919.SH",#216
    #         "600926.SH",#217
    #         "600958.SH",#218
    #         "600959.SH",#219
    #         "600977.SH",#220
    #         "600999.SH",#221
    #         "601006.SH",#222
    #         "601009.SH",#223
    #         "601012.SH",#224
    #         "601018.SH",#225
    #         "601021.SH",#226
    #         "601088.SH",#227
    #         "601099.SH",#228
    #         "601108.SH",#229
    #         "601111.SH",#230
    #         "601117.SH",#231
    #         "601155.SH",#232
    #         "601166.SH",#233
    #         "601169.SH",#234
    #         "601186.SH",#235
    #         "601198.SH",#236
    #         "601211.SH",#237
    #         "601212.SH",#238
    #         "601216.SH",#239
    #         "601225.SH",#240
    #         "601228.SH",#241
    #         "601229.SH",#242
    #         "601238.SH",#243
    #         "601288.SH",#244
    #         "601318.SH",#245
    #         "601328.SH",#246
    #         "601333.SH",#247
    #         "601336.SH",#248
    #         "601360.SH",#249
    #         "601377.SH",#250
    #         "601390.SH",#251
    #         "601398.SH",#252
    #         "601555.SH",#253
    #         "601600.SH",#254
    #         "601601.SH",#255
    #         "601607.SH",#256
    #         "601611.SH",#257
    #         "601618.SH",#258
    #         "601628.SH",#259
    #         "601633.SH",#260
    #         "601668.SH",#261
    #         "601669.SH",#262
    #         "601688.SH",#263
    #         "601718.SH",#264
    #         "601727.SH",#265
    #         "601766.SH",#266
    #         "601788.SH",#267
    #         "601800.SH",#268
    #         "601808.SH",#269
    #         "601818.SH",#270
    #         "601828.SH",#271
    #         "601838.SH",#272
    #         "601857.SH",#273
    #         "601866.SH",#274
    #         "601877.SH",#275
    #         "601878.SH",#276
    #         "601881.SH",#277
    #         "601888.SH",#278
    #         "601898.SH",#279
    #         "601899.SH",#280
    #         "601901.SH",#281
    #         "601919.SH",#282
    #         "601933.SH",#283
    #         "601939.SH",#284
    #         "601958.SH",#285
    #         "601985.SH",#286
    #         "601988.SH",#287
    #         "601989.SH",#288
    #         "601991.SH",#289
    #         "601992.SH",#290
    #         "601997.SH",#291
    #         "601998.SH",#292
    #         "603160.SH",#293
    #         "603260.SH",#294
    #         "603288.SH",#295
    #         "603799.SH",#296
    #         "603833.SH",#297
    #         "603858.SH",#298
    #         "603993.SH"
    #         ]#299
    # init_quantities = [
    #             201252,#0
    #             112347,#1
    #             64858,#2
    #             57971,#3
    #             86355,#4
    #             307377,#5
    #             120481,#6
    #             163288,#7
    #             115384,#8
    #             128865,#9
    #             30674,#10
    #             107991,#11
    #             45454,#12
    #             13138,#13
    #             135951,#14
    #             23098,#15
    #             13171,#16
    #             107802,#17
    #             40080,#18
    #             21506,#19
    #             25066,#20
    #             55555,#21
    #             37625,#22
    #             157004,#23
    #             117268,#24
    #             42056,#25
    #             103503,#26
    #             26881,#27
    #             645161,#28
    #             47101,#29
    #             37262,#30
    #             84104,#31
    #             93873,#32
    #             23264,#33
    #             40760,#34
    #             20930,#35
    #             80385,#36
    #             56629,#37
    #             55084,#38
    #             27630,#39
    #             47008,#40
    #             5810,#41
    #             42579,#42
    #             50738,#43
    #             20714,#44
    #             38051,#45
    #             15133,#46
    #             56787,#47
    #             14324,#48
    #             28192,#49
    #             100418,#50
    #             210755,#51
    #             39033,#52
    #             23666,#53
    #             56577,#54
    #             18442,#55
    #             41560,#56
    #             28957,#57
    #             63547,#58
    #             41773,#59
    #             8653,#60
    #             60526,#61
    #             43918,#62
    #             50527,#63
    #             52742,#64
    #             37141,#65
    #             11093,#66
    #             19010,#67
    #             39682,#68
    #             6822,#69
    #             59880,#70
    #             7285,#71
    #             97495,#72
    #             52910,#73
    #             46583,#74
    #             26607,#75
    #             21754,#76
    #             8034,#77
    #             44722,#78
    #             53062,#79
    #             33980,#80
    #             43103,#81
    #             12100,#82
    #             21613,#83
    #             15806,#84
    #             18258,#85
    #             21596,#86
    #             15576,#87
    #             6923,#88
    #             14245,#89
    #             9677,#90
    #             13642,#91
    #             42067,#92
    #             17079,#93
    #             62189,#94
    #             17361,#95
    #             49212,#96
    #             3049,#97
    #             27332,#98
    #             27272,#99
    #             42098,#100
    #             30163,#101
    #             45045,#102
    #             4820,#103
    #             78512,#104
    #             54413,#105
    #             37477,#106
    #             14974,#107
    #             30078,#108
    #             19623,#109
    #             17951,#110
    #             21865,#111
    #             28074,#112
    #             22845,#113
    #             272435,#114
    #             70532,#115
    #             27777,#116
    #             370967,#117
    #             129815,#118
    #             155472,#119
    #             688694,#120
    #             75187,#121
    #             217678,#122
    #             108695,#123
    #             44169,#124
    #             279552,#125
    #             92281,#126
    #             185130,#127
    #             126742,#128
    #             255912,#129
    #             7607,#130
    #             163306,#131
    #             230202,#132
    #             20491,#133
    #             38617,#134
    #             75757,#135
    #             14416,#136
    #             94890,#137
    #             45977,#138
    #             95385,#139
    #             50946,#140
    #             57894,#141
    #             108695,#142
    #             16902,#143
    #             36813,#144
    #             149700,#145
    #             109427,#146
    #             57591,#147
    #             61141,#148
    #             22163,#149
    #             27243,#150
    #             107260,#151
    #             141509,#152
    #             297927,#153
    #             9057,#154
    #             33666,#155
    #             55795,#156
    #             93750,#157
    #             56896,#158
    #             14326,#159
    #             48179,#160
    #             30621,#161
    #             21474,#162
    #             68886,#163
    #             28409,#164
    #             62344,#165
    #             12858,#166
    #             15000,#167
    #             32991,#168
    #             58072,#169
    #             13404,#170
    #             48966,#171
    #             44311,#172
    #             74931,#173
    #             9156,#174
    #             50761,#175
    #             24108,#176
    #             40431,#177
    #             37406,#178
    #             13498,#179
    #             29823,#180
    #             135642,#181
    #             14096,#182
    #             68587,#183
    #             25239,#184
    #             16791,#185
    #             23166,#186
    #             13485,#187
    #             67811,#188
    #             54692,#189
    #             27801,#190
    #             94108,#191
    #             47169,#192
    #             39827,#193
    #             20770,#194
    #             55624,#195
    #             16592,#196
    #             35971,#197
    #             110208,#198
    #             73863,#199
    #             46082,#200
    #             112660,#201
    #             37313,#202
    #             44117,#203
    #             300829,#204
    #             49786,#205
    #             7868,#206
    #             61728,#207
    #             49638,#208
    #             188937,#209
    #             50484,#210
    #             106837,#211
    #             161113,#212
    #             23056,#213
    #             163960,#214
    #             43774,#215
    #             170542,#216
    #             50314,#217
    #             84056,#218
    #             41666,#219
    #             19719,#220
    #             56684,#221
    #             145781,#222
    #             146471,#223
    #             50074,#224
    #             105540,#225
    #             7790,#226
    #             47864,#227
    #             139925,#228
    #             10162,#229
    #             76388,#230
    #             56719,#231
    #             22550,#232
    #             299560,#233
    #             359504,#234
    #             122549,#235
    #             32630,#236
    #             89700,#237
    #             22321,#238
    #             92250,#239
    #             97142,#240
    #             53827,#241
    #             134075,#242
    #             16173,#243
    #             927109,#244
    #             267393,#245
    #             659898,#246
    #             97087,#247
    #             20639,#248
    #             11704,#249
    #             103950,#250
    #             150139,#251
    #             527240,#252
    #             59808,#253
    #             175202,#254
    #             74512,#255
    #             30536,#256
    #             23734,#257
    #             148437,#258
    #             39946,#259
    #             36644,#260
    #             526315,#261
    #             125786,#262
    #             77629,#263
    #             50872,#264
    #             87476,#265
    #             188039,#266
    #             47219,#267
    #             39949,#268
    #             18078,#269
    #             381250,#270
    #             8968,#271
    #             11547,#272
    #             172936,#273
    #             78828,#274
    #             21699,#275
    #             10760,#276
    #             32703,#277
    #             29146,#278
    #             46904,#279
    #             253521,#280
    #             102611,#281
    #             100000,#282
    #             99614,#283
    #             182005,#284
    #             24711,#285
    #             123400,#286
    #             512129,#287
    #             231707,#288
    #             60060,#289
    #             91743,#290
    #             33840,#291
    #             76013,#292
    #             2297,#293
    #             2116,#294
    #             23148,#295
    #             17376,#296
    #             3802,#297
    #             11235,#298
    #             65104
    #         ]#299

    bt_dir = 'SHARE_21/ModelProduction/20180901_end/bt_info/20181101-20181130/5161001/'
    symbols, init_quantities = hf.get_symbols_quantities_from_json(bt_dir + '5161001_quantity.json')

    signal_csv_dir = '011478/data/'
    output_dir = '011478/TEMP/bt-11-5161001-use-cv-wide-09-10-5161001-triggers/'
    executor_str = 'SignalExecutorTesting'
    trigger_json_dir = '011478/production/triggers/cv-wide-09-10-5161001-triggers/'
    
    input_manager = InputManager(signal_csv_dir=signal_csv_dir, bt_dir=bt_dir, output_dir=output_dir, executor_str=executor_str, trigger_json_dir=trigger_json_dir)
    input_manager.set_symbols(symbols)
    input_manager.set_init_quantity(init_quantities)
    result_manager = ResultManager()
    threading_manager = ThreadingManager(input_manager, result_manager, max_tasks=200)

    threading_manager.start()

    print('done')


if __name__ == '__main__':
    main()
