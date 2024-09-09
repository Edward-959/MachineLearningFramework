import json
import multiprocessing
import queue
import time
from collections import deque
from typing import Deque

from ModelSystem.SignalEvaluate import SignalEvaluate
from Utils.HelperFunctions import *
from Utils.InputManager import *
from Utils.ResultManager import ResultManager


def pool_func_not_cross_valid(pid, symbol, input_manager: 'InputManager', params_list, show=None):
    input_manager.prepare_input_with_symbol(symbol)
    inputs = input_manager.get_input(symbol, 'all')

    results = []
    for trigger_dict in params_list:
        se = SignalEvaluate(inputs, [(inputs.signal_data, trigger_dict)])
        result = se.evaluate(show)
        results.append(result)
        print('pid: ' + str(pid) + ' ' + symbol + ' ' + str(trigger_dict))
    return results


def pool_func_cross_valid(pid, symbol, input_manager: 'InputManager', params_list, show=None):
    input_manager.prepare_input_with_symbol(symbol)
    input_first = input_manager.get_input(symbol, 'first_half')
    input_second = input_manager.get_input(symbol, 'second_half')

    results_first = []
    results_second = []
    for trigger_dict in params_list:
        se_first = SignalEvaluate(input_first, [(input_first.signal_data, trigger_dict)])
        result_first = se_first.evaluate(show)
        results_first.append(result_first)
        se_second = SignalEvaluate(input_second, [(input_second.signal_data, trigger_dict)])
        result_second = se_second.evaluate(show)
        results_second.append(result_second)
        print('pid: ' + str(pid) + ' ' + symbol + ' ' + str(trigger_dict))
    return results_first, results_second


def func(symbol, input_manager: 'InputManager', result_manager: 'ResultManager', processes):
    input_manager.prepare_param_set(symbol)
    params = input_manager.get_all_param_dict_from_symbol(symbol)
    splitted_params: List[List[Dict[str, float]]] = split_params(params, processes)
    output_path = input_manager.output_dir
    if input_manager.is_cross_validation():
        future = []
        pool = multiprocessing.Pool(processes=processes)
        pid = 0
        for params_list in splitted_params:
            pid += 1
            future.append(pool.apply_async(pool_func_cross_valid, args=(pid, symbol, input_manager, params_list,)))
        pool.close()
        pool.join()
        first_results = []
        second_results = []
        for result in future:
            first_result, second_result = result.get()
            first_results += first_result
            second_results += second_result
        result_manager.set_results_for_symbol(symbol, first_results)
        trigger_dict_first = result_manager.find_best_param(symbol, output_path, 'first')
        best_open_trigger_first = trigger_dict_first['longTriggerRatio']
        best_close_trigger_first = trigger_dict_first['longCloseRatio']
        best_trigger_dict_first = InputManager.generate_trigger_dict(best_open_trigger_first, best_close_trigger_first)
        result_manager.set_results_for_symbol(symbol, second_results)
        trigger_dict_second = result_manager.find_best_param(symbol, output_path, 'second')
        best_open_trigger_second = trigger_dict_second['longTriggerRatio']
        best_close_trigger_second = trigger_dict_second['longCloseRatio']
        best_trigger_dict_second = InputManager.generate_trigger_dict(best_open_trigger_second, best_close_trigger_second)
        input_manager.prepare_input_with_symbol(symbol)
        inputs = input_manager.get_input(symbol, 'all')
        input_first = input_manager.get_input(symbol, 'first_half')
        input_second = input_manager.get_input(symbol, 'second_half')
        se = SignalEvaluate(input_second, [(input_second.signal_data, best_trigger_dict_first)])
        se.evaluate(show='second')
        se = SignalEvaluate(input_first, [(input_first.signal_data, best_trigger_dict_second)])
        se.evaluate(show='first')
        se = SignalEvaluate(inputs, [(input_first.signal_data, best_trigger_dict_second), (input_second.signal_data, best_trigger_dict_first)])
        se.evaluate(show='merged')
        best_trigger_to_dump = best_trigger_dict_second
    else:
        future = []
        pool = multiprocessing.Pool(processes=processes)
        pid = 0
        for params_list in splitted_params:
            pid += 1
            future.append(pool.apply_async(pool_func_not_cross_valid, args=(pid, symbol, input_manager, params_list,)))
        pool.close()
        pool.join()
        results = []
        for result in future:
            result_list = result.get()
            results += result_list
        result_manager.set_results_for_symbol(symbol, results)
        trigger_dict = result_manager.find_best_param(symbol, output_path, 'all')
        best_open_trigger = trigger_dict['longTriggerRatio']
        best_close_trigger = trigger_dict['longCloseRatio']
        best_trigger_dict = InputManager.generate_trigger_dict(best_open_trigger, best_close_trigger)
        input_manager.prepare_input_with_symbol(symbol)
        inputs = input_manager.get_input(symbol, 'all')
        se = SignalEvaluate(inputs, [(inputs.signal_data, best_trigger_dict)])
        se.evaluate(show='all')
        best_trigger_to_dump = best_trigger_dict
    # DUMP TRIGGER JSON
    json_path = inputs.output_path_dir + 'triggerRatio.json'
    with open(json_path, 'w') as f:
        json.dump(best_trigger_to_dump, f)
    print('Finished ' + symbol)


class ThreadingManager:
    __slots__ = ['__input_manager', '__result_manager', '__result_keys', '__symbol_processes', '__param_processes',
                 '__symbols', '__results']

    def __init__(self, input_manager: 'InputManager', result_manager: 'ResultManager', symbol_processes: int = 2,
                 param_processes: int = 4):
        self.__input_manager = input_manager
        self.__result_manager = result_manager
        self.__result_keys = self.__result_manager.get_keys()
        self.__symbol_processes = symbol_processes
        self.__param_processes = param_processes
        self.__symbols: List[str] = input_manager.get_symbols()
        self.__results: List = []

    def start(self):
        print('Programme is running...')
        start = time.perf_counter() 
        # result_queue = multiprocessing.Queue()
        size = len(self.__symbols)
        q_symbols: queue.Queue[str] = queue.Queue()
        [q_symbols.put(symbol) for symbol in self.__symbols]
        d_process: Deque[multiprocessing.Process] = deque()
        
        while not q_symbols.empty():
            symbol = q_symbols.get()
            p = multiprocessing.Process(target=func, 
                                        args=(symbol, self.__input_manager, self.__result_manager, 
                                              self.__param_processes))
            p.start()
            d_process.append(p)
            if len(d_process) == self.__symbol_processes:
                while True:
                    p = d_process.popleft()
                    p.join(1)
                    if not p.is_alive():
                        break
                    else:
                        d_process.append(p)
            if q_symbols.empty():
                for p in d_process:
                    p.join()
                    
        end = time.perf_counter()
        print('running time: ' + str(round((end - start) / 60, 2)) + 'min')

    def get_results(self):
        return self.__results
