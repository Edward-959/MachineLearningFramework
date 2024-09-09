# -*- coding: utf-8 -*-
# @Time    : 2018/7/11 9:01
# @Author  : 011672
# @File    : TransactionDistribution.py
import numpy as np
import math
from System.Factor import Factor


class TransactionDistribution(Factor):
    def __init__(self, para, factorManagement):
        Factor.__init__(self, para, factorManagement)
        self.__data = self.getTradingUnderlyingData(self.getIndexTradingUnderlying()[0])
        factorManagement.registerFactor(self, para)

    def calculate(self):
        if len(self.__data.getContent())<2:
            self.addData([0.5,0,0.5],self.__data.getLastTimeStamp())
            return
        last_bid_0_price=self.__data.getContent()[-2].bidPrice[0]
        last_ask_0_price=self.__data.getContent()[-2].askPrice[0]
        transaction_list=self.__data.getContent()[-1].transactionData
        volume_buy=0
        volume_sell=0
        volume_mid=0
        if len(transaction_list)==0:
            self.addData([0.5,0,0.5],self.__data.getLastTimeStamp())
            return
        for transaction_inform in transaction_list:
            if transaction_inform[3]>=last_ask_0_price:
                volume_buy+=transaction_inform[4]
            elif transaction_inform[3]<=last_bid_0_price:
                volume_sell+=transaction_inform[4]
            else:
                volume_mid+=transaction_inform[4]
        if volume_mid+volume_buy+volume_sell==0:
            self.addData([0.5,0,0.5],self.__data.getLastTimeStamp())
            return
        else:
            result=[volume_buy/(volume_mid+volume_buy+volume_sell),volume_mid/(volume_mid+volume_buy+volume_sell),
                    volume_sell/(volume_mid+volume_buy+volume_sell)]
            self.addData(result, self.__data.getLastTimeStamp())
            return
