import numpy as np
import pandas as pd
from typing import List, Dict
import xlsxwriter
from xquant.pyfile import Pyfile
import System.RemotePrint as rp
import json


class ResultManager:
    def __init__(self, method='default', default_keys=None, is_output_all=False):
        self.__method = method
        if default_keys is None:
            self.__keys = ['annualReturnMV', 'averageTradingReturnRate', 'winRate', 'averagePositionTime',
                           'dayWinningRate', 'timesPerDay']
        else:
            self.__keys = default_keys
        self.__param_result_mat: Dict[str, Dict[str, np.ndarray]] = {}
        self.__open_triggers: Dict[str, List[float]] = {}
        self.__close_triggers: Dict[str, List[float]] = {}

    def get_keys(self):
        return self.__keys

    def set_results_for_symbol(self, symbol: str, results: List[Dict[str, float]]):
        temp_dict = {}
        self.__update_triggers(symbol, results)
        for key in self.__keys:
            self.__set_mat_from_key(symbol, results, temp_dict, key)
        self.__param_result_mat.update({symbol: temp_dict})
        # print(temp_dict)

    def __update_triggers(self, symbol, results):
        open_triggers_set = set()
        close_triggers_set = set()
        for result in results:
            open_trigger = result['longTriggerRatio']
            close_trigger = result['longCloseRatio']
            open_triggers_set.add(open_trigger)
            close_triggers_set.add(close_trigger)
        open_triggers_list = list(open_triggers_set)
        close_triggers_list = list(close_triggers_set)
        open_triggers_list.sort()
        close_triggers_list.sort()
        self.__open_triggers.update({symbol: open_triggers_list})
        self.__close_triggers.update({symbol: close_triggers_list})

    def __set_mat_from_key(self, symbol, results: List[Dict[str, float]], mat_dict, key: str):
        matrix = np.zeros((len(self.__open_triggers[symbol]), len(self.__close_triggers[symbol])))
        matrix[:] = np.nan
        for result in results:
            open_trigger = result['longTriggerRatio']
            close_trigger = result['longCloseRatio']
            open_index = self.__open_triggers[symbol].index(open_trigger)
            close_index = self.__close_triggers[symbol].index(close_trigger)
            value = result[key]
            matrix[open_index, close_index] = value
        mat_dict.update({key: matrix})

    def __output_param_mat(self, symbol: str, best_param: Dict[str, float], output_dir, suffix):
        results = self.__param_result_mat[symbol]
        opens = self.__open_triggers[symbol]
        closes = self.__close_triggers[symbol]
        best_open_index = self.__open_triggers[symbol].index(best_param['longTriggerRatio'])
        best_close_index = self.__close_triggers[symbol].index(best_param['longCloseRatio'])
        best_value_dict = {}
        temp = {}
        for key in results.keys():
            best_value = results[key][best_open_index, best_close_index]
            data = pd.DataFrame(results[key], index=opens, columns=closes)
            temp.update({key: data})
            best_value_dict.update({key: best_value})
        py = Pyfile()
        xls_dir = output_dir + symbol + '/selection_from_' + suffix + '.xlsx'
        if py.exists(xls_dir):
            py.delete(xls_dir)
        with py.open(xls_dir, 'wb') as f:
            writer = pd.ExcelWriter(f, engine='xlsxwriter')
            bold_format = writer.book.add_format({'bold': True})
            for key in temp.keys():
                temp[key].to_excel(writer, sheet_name=key)
                writer.sheets[key].conditional_format(1, 1, len(opens), len(closes), {'type': '3_color_scale'})
                writer.sheets[key].write(0, 0, 'open_thresholds\\close_thresholds')
                writer.sheets[key].write(best_open_index + 1, best_close_index + 1, best_value_dict[key], bold_format)
            writer.save()
        if 'condition' in best_param:
            file_name = output_dir + symbol + '/condition_from_' + suffix + '.json'
            if py.exists(file_name):
                py.delete(file_name)
            with py.open(file_name, 'wb') as f:
                json.dump(best_param['condition'], f)

    def find_best_param(self, symbol: str, output_dir=None, suffix=None) -> Dict[str, float]:
        # py path in normal's HDFS and in Spark's HDFS are different
        import warnings
        warnings.filterwarnings('ignore')
        best_param = self.__find_by_method(symbol)
        if output_dir is not None and suffix is not None:
            self.__output_param_mat(symbol, best_param, output_dir, suffix)
            if 'condition' in best_param and best_param['condition'] == 'condition_rest':
                best_param = {'longTriggerRatio': 999999, 'longCloseRatio': 0, 'condition': 'condition_rest'}
        return best_param
            
    def __find_by_method(self, symbol: str) -> Dict[str, float]:
        if self.__method == 'default':
            return self.__my_best_param_solution(symbol)

    # A SPECIFIC SOLUTION: could be overridden in the future
    def __my_best_param_solution(self, symbol: str) -> Dict[str, float]:
        win_rate_threshold = 0.5
        day_winning_rate_threshold = 0.6

        win_rate: np.ndarray = self.__param_result_mat[symbol]['winRate']
        position_time: np.ndarray = self.__param_result_mat[symbol]['averagePositionTime']
        day_winning_rate: np.ndarray = self.__param_result_mat[symbol]['dayWinningRate']
        annual_return: np.ndarray = self.__param_result_mat[symbol]['annualReturnMV']
        average_return: np.ndarray = self.__param_result_mat[symbol]['averageTradingReturnRate']
        times_daily: np.ndarray = self.__param_result_mat[symbol]['timesPerDay']

        position_time_select: np.ndarray = position_time[annual_return > 0]
        times_daily_select: np.ndarray = times_daily[annual_return > 0]
        if position_time_select.shape[0] == 0:
            position_time_threshold = np.nanmean(position_time)
            times_daily_threshold = np.nanmedian(times_daily)
        else:
            position_time_threshold = np.nanmean(position_time_select)
            times_daily_threshold = np.nanmedian(times_daily_select)
        if position_time_threshold < 12:
            position_time_threshold = 12
        elif position_time_threshold > 30:
            position_time_threshold = 30
            

        position_time_condition = position_time <= position_time_threshold
        win_rate_condition = win_rate >= win_rate_threshold
        day_winning_rate_condition = day_winning_rate >= day_winning_rate_threshold
        times_daily_condition = times_daily >= times_daily_threshold

        if np.nanmax(np.abs(annual_return)) > 0:
            annual_return_score = annual_return / np.nanmax(np.abs(annual_return))
        else:
            annual_return_score = np.zeros(annual_return.shape, np.float32)

        if np.nanmax(np.abs(average_return)) > 0:
            average_return_score = average_return / np.nanmax(np.abs(average_return))
        else:
            average_return_score = np.zeros(average_return.shape, np.float32)

        total_score: np.ndarray = annual_return_score + average_return_score

        condition1 = win_rate_condition & day_winning_rate_condition & times_daily_condition & position_time_condition
        condition2 = day_winning_rate_condition & times_daily_condition & position_time_condition
        condition3 = day_winning_rate_condition & position_time_condition
        condition4 = day_winning_rate_condition

        if condition1.any():
            best_index = self.__my_best_index(condition1, total_score)
            text = 'condition_1'
        elif condition2.any():
            best_index = self.__my_best_index(condition2, total_score)
            text = 'condition_2'
        elif condition3.any():
            best_index = self.__my_best_index(condition3, total_score)
            text = 'condition_3'
        elif condition4.any():
            best_index = self.__my_best_index(condition4, total_score)
            text = 'condition_4'
        else:
            condition = ~np.isnan(annual_return)
            best_index = self.__my_best_index(condition, total_score)
            text = 'condition_rest'

        return {'longTriggerRatio': self.__open_triggers[symbol][best_index[0]],
                'longCloseRatio': self.__close_triggers[symbol][best_index[1]],
                'condition': text}

    # my helper
    def __my_best_index(self, condition: np.ndarray, total_score: np.ndarray):
        index = np.nonzero(condition)
        valid = total_score[index]
        max_index: int = np.nanargmax(valid)
        return index[0][max_index], index[1][max_index]

    def get_results_full(self):
        return self.__param_result_mat

    def clear_all(self):
        self.__param_result_mat = {}
