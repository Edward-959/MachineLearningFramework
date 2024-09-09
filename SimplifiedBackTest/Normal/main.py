from Utils.InputManager import InputManager
from Utils.ResultManager import ResultManager
from Utils.ThreadingManager import ThreadingManager
import Utils.HelperFunctions as hf


"""
本版本为参数遍历选择最优版本。适合在本地运行（若有数据）以及在XQuant上运行（调度服务器）
如果不明白参数的意义：
1. signal_csv_dir: 读取数据的路径，一般峰哥都会准备好数据，运行前可以先跟他确认。
2. output_dir: 输出xls报告的根目录。具体输出时，会在目录下创建以股票代码为名字的文件夹，（固定名称的）报告则会在下一级生成。
3. executor_str: 执行的交易逻辑。具体写法请联系011478。默认为SignalExecutorTesting，与峰哥执行回测的交易逻辑完全一致，可作为benchmark。
4. symbols: 回测的股票列表，请确保signal_csv_dir中，含有股票列表的信号数据。支持单个股票。
5. init_quantities: 回测的初始股数，与symbols一一对应。如果长度不同，则会报错。支持单个股票。
6. open_triggers: （做多）开仓阈值参数遍历范围。支持单个参数及多个参数。
7. close_triggers: （做多）平仓阈值参数遍历范围。支持单个参数及多个参数。
8. cross_valid: 是否交叉验证。（具体做法请联系013050）
9. param_reduction: 减少不必要的参数遍历。将过大的（做多）开仓阈值去除，以提高回测效率。（如果全部被剔除，则会报错，但不影响其他股票的回测）
10. symbol_processes/param_processes: 股票进程数/单个股票进行参数遍历的进程数。建议两者乘积为2、4、8。

如果想要自定义方法：
1. 改变信号的均值求法: SignalManager -> def __pre_process_single
2. 改变回测的风控指标: InputManager -> def __init__ -> mock_trade_para
3. 改变param_reduction方法: InputManager -> def __my_param_reduction 请确保开平参数最终能输出一个矩阵

**4. 改变回测的方式: Please derive from SignalExecutorBase
**5. 改变阈值的评价方式: ResultManager -> def __my_best_param_solution 如果在评价时需要更多的评价指标，可以显示定义构造函数的default_keys

如果疑问请联系: 011478
"""
def main():
    # symbols = [
    # '000333.SZ',
    # '000513.SZ',
    # '000568.SZ',
    # '000581.SZ',
    # '000651.SZ',
    # '000661.SZ',
    # '000786.SZ',
    # '000858.SZ',
    # '000895.SZ',
    # '000910.SZ',
    # '000963.SZ',
    # '000977.SZ',
    # '000983.SZ',
    # '001979.SZ',
    # '002007.SZ',
    # '002056.SZ',
    # '002241.SZ',
    # '002304.SZ',
    # '002311.SZ',
    # '002384.SZ',
    # '002396.SZ',
    # '002466.SZ',
    # '002475.SZ',
    # '002594.SZ',
    # '002601.SZ',
    # '002624.SZ',
    # '300070.SZ',
    # '300136.SZ',
    # '300498.SZ',
    # '600004.SH',
    # '600009.SH',
    # '600036.SH',
    # '600066.SH',
    # '600196.SH',
    # '600362.SH',
    # '600418.SH',
    # '600498.SH',
    # '600519.SH',
    # '600521.SH',
    # '600549.SH',
    # '600566.SH',
    # '600570.SH',
    # '600703.SH',
    # '600867.SH',
    # '600884.SH',
    # '601088.SH',
    # '601155.SH',
    # '601288.SH',
    # '601318.SH',
    # '601398.SH',
    # '601601.SH',
    # '601899.SH',
    # '603328.SH'
    # ]
    #
    #
    # init_quantities = [
    # 253826,
    # 174834,
    # 128506,
    # 199488,
    # 256596,
    # 67453,
    # 357901,
    # 593468,
    # 155659,
    # 88749,
    # 501403,
    # 451704,
    # 788775,
    # 548975,
    # 448703,
    # 205360,
    # 433646,
    # 135108,
    # 50797,
    # 95263,
    # 319426,
    # 145862,
    # 349009,
    # 335147,
    # 174737,
    # 115117,
    # 360695,
    # 178569,
    # 445258,
    # 342427,
    # 255578,
    # 232326,
    # 239997,
    # 496024,
    # 395173,
    # 677802,
    # 75673,
    # 81528,
    # 1791771,
    # 196441,
    # 67627,
    # 98469,
    # 700391,
    # 983826,
    # 239207,
    # 228122,
    # 136139,
    # 1407281,
    # 1461339,
    # 1653351,
    # 645503,
    # 290135,
    # 104021,
    # ]

    bt_dir = '/app/data/013050/chensf/SingleModel125_20180901_20181030_choose/ModelSignalDataSet/'
    # symbols, init_quantities = hf.get_symbols_quantities_from_json(bt_dir + '5161001_quantity.json')
    signal_csv_dir = '/app/data/013050/chensf/SingleModel125_20180901_20181030_choose/ModelSignalDataSet/'
    output_dir = '/app/data/011478/SimplifiedBackTest/benchmark/'
    executor_str = 'SignalExecutorTesting'
    open_triggers = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 2.0]
    close_triggers = [-1.0, -0.9, -0.8, -0.7, -0.6, -0.5, -0.4, -0.3, -0.2, -0.1, 0, 0.1, 0.2]
    # open_triggers = [0.1, 0.2]
    # close_triggers = [-0.1, -0.2]
    
    input_manager = InputManager(signal_csv_dir=signal_csv_dir, bt_dir=bt_dir, output_dir=output_dir, executor_str=executor_str, cross_valid=True)
    input_manager.set_symbols(symbols)
    input_manager.set_init_quantity(init_quantities)
    input_manager.set_triggers(open_triggers, close_triggers, param_reduction=True)
    result_manager = ResultManager()
    threading_manager = ThreadingManager(input_manager, result_manager, symbol_processes=2, param_processes=4)

    threading_manager.start()

    print('done')


if __name__ == '__main__':
    main()
