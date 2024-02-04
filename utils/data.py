import pandas as pd
import math
import os
import re
import numpy as np
import time
from joblib import Parallel, delayed
from scipy.spatial.distance import cdist
from scipy.spatial import distance
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

folder_path = '../dataset_json'
catelog = os.listdir(folder_path)[:-1]
print(script_dir)

def calculate_distance(i, coordinates):
    return [distance.euclidean(coordinates[i], coordinates[j]) for j in range(i+1, len(coordinates))]

def main():
    # Read JSON file into a DataFrame
    df = pd.read_json(f'{folder_path}/{file_name}.json')
    print(f'{file_name}.json has been read.')

    # Extract 'node' data
    nodes = df['nodes']

    # Store the coordinates in a list
    coordinates = []
    for n in nodes:
        index = n['INDEX']
        x = n['X']
        y = n['Y']
        coordinates.append((x, y))

    # Initialize a 2D numpy array with zeros
    distance = np.zeros((len(coordinates), len(coordinates)))
    start_time = time.time()

    # Convert coordinates to a NumPy array
    coordinates_np = np.array(coordinates)

    # Calculate the distance matrix
    start_time = time.time()
    distance = cdist(coordinates_np, coordinates_np, 'euclidean')
    end_time = time.time()

    print(f'Elapsed time: {end_time - start_time} seconds')

    # Save the distance array to a CSV file in batches
    batch_size = 4000
    num_batches = math.ceil(distance.shape[0] / batch_size)
    for i in range(num_batches):
        start_index = i * batch_size
        end_index = min((i + 1) * batch_size, distance.shape[0])
        batch_distance = distance[start_index:end_index, :]
        if i == 0:
            np.savetxt(f'{folder_path}/{file_name}_distance.csv', batch_distance, delimiter=',')
        else:
            with open(f'{folder_path}/{file_name}_distance.csv', 'ab') as f:
                np.savetxt(f, batch_distance, delimiter=',')
    
    print(f'{file_name}_distance.csv has been saved.')

if __name__ == "__main__":
    file_name = 'pla33810-n338090'
    main()
