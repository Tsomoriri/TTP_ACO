import pandas as pd
import re
import math
import os
# from . import item_methods

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

folder_path = '../dataset'
catelog = os.listdir(folder_path)[:-1]

# If allow,convert string to int or float


def value_convert(value):
    try:
        result = int(value)
    except ValueError:
        try:
            result = float(value)
        except ValueError:
            result = value
    return result

# Process header data


def header_process(header_data):
    # replace "\t"
    header_data = header_data.replace('\t', '', regex=True)
    # split according ':'
    header_data = header_data[0].apply(
        lambda x: pd.Series(x.split(':')).str.strip())
    # process name
    header_data[0] = header_data[0].str.replace(' ', '_')
    # process value
    # header_data[1] = pd.to_numeric(header_data[1], errors='coerce').fillna(header_data[1])
    header_data[1] = header_data[1].apply(value_convert)

    # return dict
    return header_data.set_index(0)[1].to_dict()


def key_process(key):
    match = re.search(r'\((.*?)\)', key)
    ret = []
    if match:
        ret = match.group(1).split(',')

    ret = [item.strip().replace(' ', '_') for item in ret]

    return ret

# Process node data


def node_process(node_data):
    keys = key_process(node_data.iloc[0, 0])

    node_data = node_data.iloc[1:]
    node_data = node_data.replace('\t', ' ', regex=True)
    node_data[keys] = node_data[0].apply(
        lambda x: pd.Series(x.split(' ')).str.strip())

    node_data = node_data.drop(node_data.columns[0], axis=1)
    node_data = node_data.map(value_convert)

    return node_data.to_dict(orient='records')


def caculate_distancee(a, b):
    return round(math.sqrt((a['X'] - b['X'])**2 + (a['Y'] - b['Y'])**2), 4)

# Get distance vector


def distance_vector(coordinate):
    size = len(coordinate)
    return [[caculate_distancee(coordinate[i], coordinate[j]) for j in range(size)] for i in range(size)]


def item_process(item_data):
    keys = key_process(item_data.iloc[0, 0])
    item_data = item_data.iloc[1:]
    item_data = item_data.replace('\t', ' ', regex=True)

    item_data[keys] = item_data[0].apply(
        lambda x: pd.Series(x.split(' ')).str.strip())
    item_data = item_data.drop(item_data.columns[0], axis=1)
    item_data = item_data.map(value_convert)

    return item_data.to_dict(orient='records')

def max_value(items, maximum):
    sort_items = sorted(
        items, key=lambda x: x['PROFIT']/x['WEIGHT'], reverse=True)
    weight = 0
    for i in sort_items:
        weight += i['WEIGHT']
        if weight > maximum:
            return i['PROFIT']/i['WEIGHT']

def item_allocate_node(items, node_length):
    ret = [[] for _ in range(node_length)]
    for item in items:
        # item['heuristic'] = item['PROFIT'] / item['WEIGHT']
        ret[item['ASSIGNED_NODE_NUMBER']-1].append(item)
    return ret

def process_name(name, add, index = 1):
    ret = name.split('-')
    ret.insert(index, add)
    return '-'.join(ret)

# Read data from file
def read_txt(file_name):
    global folder_path

    max_header_index = 9
    ret = {}
    df = pd.read_csv(f'{folder_path}/{file_name}.txt',
                     sep='\\n', header=None, engine='python')

    header = header_process(df.iloc[:max_header_index])
    ret.update(header)

    nodes = node_process(
        df.iloc[max_header_index: max_header_index + ret['DIMENSION']+1])
    # ret['distance_vector'] = distance_vector(nodes)
    ret['nodes'] = nodes

    items = item_process(df.iloc[-(ret['NUMBER_OF_ITEMS'] + 1):])
    # ret['items'] = items
    ret['max_item_value'] = max_value(items, ret['CAPACITY_OF_KNAPSACK'])
    ret['node_item'] = item_allocate_node(items, ret['DIMENSION'])
    ret['output_name'] = process_name(ret['PROBLEM_NAME'], f"n{ret['NUMBER_OF_ITEMS']}")

    return ret

# list is an array, the value should be the name of dataset


def main(list=catelog):
    # list must be an array
    ret = []
    for item in list:
        ret.append(read_txt(item.rstrip('.txt')))
    return ret


if __name__ == "__main__":
    # test-example-n4, a280-n279, a280-n1395, a280-n2790,
    # fnl4461-n4460, fnl4461-n22300, fnl4461-n44600,
    # pla33810-n33809, pla33810-n169045, pla33810-n338090
    # ...
    file_name = 'a280-n279'
    data = main([file_name])

    import json_methods
    json_methods.export(file_name, data[0])
