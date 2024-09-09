from System.StrategyManagement_XQuant import StrategyManagement
from System.Strategy import Strategy
from System.Func_XQuant import execute
import time
import json
import sys
import os
import xquant.tensorflow as xt
import xquant


def createStrategyManagement():
    strategyManagement = StrategyManagement()
    # 输出文件夹路径, 该路径为HDFS中的路径, 且事先必须不存在, here is the default value 
    userdir = getUserDir()
    if(len(userdir)>0):
        strategyManagement.setDstDir(userdir+'/output/' + time.strftime("%Y%m%d%H%M%S", time.localtime()))
    else:
        strategyManagement.setDstDir('/analysis/xquant/006547/output/' + time.strftime("%Y%m%d%H%M%S", time.localtime()))
    # Func.execute是默认值，可以不用设置, 后期如果要使用其他自定义函数, 则在这设置
    strategyManagement.setFunc(execute)
    # 默认按1天切分任务, 如果要加粗切分粒度, 则在这设置
    strategyManagement.setDaysInterval(1)
    return strategyManagement


def createStrategy(para):
   
    # 不用加StrategyManagement参数
    strategy = Strategy()
    strategy.setStrategyName(para["StrategyName"])
    strategy.setTradingUnderlyingCode(para["TradingUnderlyingCode"])
    strategy.setFactorUnderlyingCode(para["FactorUnderlyingCode"])
    strategy.setParaFactor(para["FactorSet"])
    strategy.setParaTag(para["Tag"])
    strategy.setStartDateTime(para["StartDateTime"])
    strategy.setEndDateTime(para["EndDateTime"])
    return strategy


def DataPrepare(factorSetJsonFile):
    with open(factorSetJsonFile, 'r') as file:
        para = json.load(file)
        strategyManagement = createStrategyManagement()
        strategy1 = createStrategy(para)
        # 单击版本中是在构造Strategy的init函数中进行register的, 这里必须额外调用registerStrategy方法
        strategyManagement.registerStrategy(strategy1)
        strategyManagement.start()
        dataPath = strategyManagement.getDstDir()
        print("Factors and Tags output: " + dataPath)
        return dataPath
    raise  Exception('Factors initialization is failed!!!')

def getUserDir():
    for i in range(1, len(sys.argv)):
        if(str(sys.argv[i])=="--user" and i < len(sys.argv)):
            return '/analysis/xquant/'+str(sys.argv[i+1])


def main():
    configJsonfile = "AlgoConfig.py" 
    father_path=os.path.abspath(os.path.realpath(__file__)+os.path.sep+"../")
    paramPath = father_path +"/" + configJsonfile
    print("start generating tags")
    inputDataPath = DataPrepare(paramPath)
    print("start training model")
    #xt.run_tensorflow("tfModel/MainTrainModelNN.py")
    print("end")
