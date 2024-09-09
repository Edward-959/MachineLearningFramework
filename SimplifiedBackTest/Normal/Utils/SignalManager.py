import datetime as dt
import json
import pickle
import pandas as pd
import os
from typing import List

from ModelSystem.Util.SimpleDataConverter import SimpleDataConverter


class SignalManager:
    __slots__ = ['__root', '__symbol', '__dates', '__first_half_dates', '__second_half_dates', '__first_half_data',
                 '__second_half_data', '__tick', '__transaction', '__tick_dict', '__capacity', '__bt_dir']

    def __init__(self, symbol: str, root: str='./stock_data/', bt_dir: str='./stock_data/'):
        self.__root = root
        self.__bt_dir = bt_dir
        self.__symbol = symbol
        self.__get_dates()
        self.__split_dates()
        self.__pre_process_first_half()
        self.__pre_process_second_half()
        # self.__load_stock_data_in_pickle()  # explicitly load to improve performance under multiprocessing
        self.__tick = None
        self.__transaction = None
        self.__tick_dict = None
        self.__load_order_capacity()

    def __get_dates(self) -> None:
        with open(self.__bt_dir + self.__symbol + '/Dates.json', 'r') as f:
            self.__dates: List[str] = json.load(f)['Dates']
            self.__dates.sort()

    def __split_dates(self) -> None:
        length = len(self.__dates)
        half = int(length / 2)
        self.__first_half_dates = self.__dates[: half]
        self.__second_half_dates = self.__dates[half:]

    def __pre_process_first_half(self) -> None:
        self.__first_half_data: pd.DataFrame = None
        for date in self.__first_half_dates:
            filename = self.__symbol + '_' + date + '.csv'
            data = self.__pre_process_single(filename)
            if data is None:
                continue
            if self.__first_half_data is not None:
                self.__first_half_data = pd.concat([self.__first_half_data, data], axis=0)
            else:
                self.__first_half_data = data

    def __pre_process_second_half(self) -> None:
        self.__second_half_data: pd.DataFrame = None
        for date in self.__second_half_dates:
            filename = self.__symbol + '_' + date + '.csv'
            data = self.__pre_process_single(filename)
            if data is None:
                continue
            if self.__second_half_data is not None:
                self.__second_half_data = pd.concat([self.__second_half_data, data], axis=0)
            else:
                self.__second_half_data = data

    def __pre_process_single(self, filename: str) -> pd.DataFrame:
        testname = self.__root + self.__symbol + '/' + filename
        if not os.path.exists(testname):
            print(testname + ' file does not exist. Pass this file.')
            return None
        data = pd.read_csv(testname)
        column_long = data['1minLong'] + data['2minLong'] + data['5minLong']
        column_long /= 3
        data = data.assign(ave_long=column_long)

        column_short = data['1minShort'] + data['2minShort'] + data['5minShort']
        column_short /= 3
        data = data.assign(ave_short=column_short)

        data['Ticktime'] = data['Ticktime'].apply(lambda x: dt.datetime.strptime(x, '%H:%M:%S').time())
        data = SignalManager.average_special_time(data, dt.time(11, 25, 0), dt.time(11, 28, 0), dt.time(11, 30, 0))
        data = SignalManager.average_special_time(data, dt.time(14, 52, 0), dt.time(14, 55, 0), dt.time(14, 57, 0))
        return data

    def load_stock_data_in_pickle(self):
        path = self.__bt_dir + self.__symbol + '/Data.pickle'
        with open(path, 'rb') as f:
            self.__tick, self.__transaction = pickle.load(f)
        data_converter = SimpleDataConverter(self.__tick)
        self.__tick_dict = data_converter.get_data_dict()
        
    def __load_order_capacity(self):
        with open(self.__bt_dir + self.__symbol + '/OrderCapacity.json', 'r') as f:
            self.__capacity = json.load(f)

    @staticmethod
    def average_special_time(data: pd.DataFrame, time1: dt.time, time2: dt.time, time3: dt.time) -> pd.DataFrame:
        filter1 = (data['Ticktime'] >= time1) & (data['Ticktime'] < time2)
        index1 = data.loc[filter1, 'Ticktime'].index
        ave_long1 = (data.loc[index1, '1minLong'] + data.loc[index1, '2minLong']) / 2
        ave_short1 = (data.loc[index1, '1minShort'] + data.loc[index1, '2minShort']) / 2
        data.loc[index1, 'ave_long'] = ave_long1
        data.loc[index1, 'ave_short'] = ave_short1

        filter2 = (data['Ticktime'] >= time2) & (data['Ticktime'] < time3)
        index2 = data.loc[filter2, 'Ticktime'].index
        ave_long2 = data.loc[index2, '1minLong']
        ave_short2 = data.loc[index2, '1minShort']
        data.loc[index2, 'ave_long'] = ave_long2
        data.loc[index2, 'ave_short'] = ave_short2
        return data

    def get_signals(self) -> pd.DataFrame:
        return pd.concat([self.__first_half_data, self.__second_half_data], axis=0)

    def get_signals_from_first_half(self) -> pd.DataFrame:
        return self.__first_half_data

    def get_signals_from_second_half(self) -> pd.DataFrame:
        return self.__second_half_data

    def get_tick(self):
        return self.__tick

    def get_transaction(self):
        return self.__transaction

    def get_tick_dict(self):
        return self.__tick_dict
    
    def get_order_capacity(self):
        return self.__capacity


if __name__ == '__main__':
    data_manager = SignalManager('000333.SZ')
    data_temp = data_manager.get_signals()
    data_temp.to_csv('test.csv')
