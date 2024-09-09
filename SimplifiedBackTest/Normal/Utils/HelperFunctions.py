from typing import List, Dict
import json


def get_symbols_quantities_from_json(json_path):
    symbols = []
    init_quantities = []
    with open(json_path, 'r') as f:
        data = json.load(f)
    for symbol in data['quantity'].keys():
        symbols.append(symbol)
        init_quantities.append(data['quantity'][symbol])
    return symbols, init_quantities


def split_params(original_params: List[Dict[str, float]], group_num: int) -> List[List[Dict[str, float]]]:
    splitted_params = []
    if len(original_params) <= group_num:
        for param in original_params:
            splitted_params.append([param])
    else:
        for index in range(group_num):
            splitted_params.append([])
        count = 0
        for param in original_params:
            splitted_params[count].append(param)
            count += 1
            if count >= group_num:
                count = 0
    return splitted_params

# END
