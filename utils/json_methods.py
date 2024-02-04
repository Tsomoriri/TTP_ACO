import json
import os
import numpy as np
import dask.dataframe as dd
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

folder_path = '../dataset_json'


def export(name, data):
    # export json file
    global folder_path

    json_file_path = f'{folder_path}/{name}.json'
    with open(json_file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)


def read(name):
    # read json file
    global folder_path

    json_file_path = f'{folder_path}/{name}.json'
    with open(json_file_path, 'r') as json_file:
        data_dict = json.load(json_file)

    return data_dict

def read_csv(name):

    # read csv file
    global folder_path

    csv_file_path = f'{folder_path}/{name}.csv'
    data = dd.read_csv(csv_file_path,sample=1024**2)
    return data
