import random
import math
from tqdm import tqdm
from utils import import_data, json_methods, node_methods
from utils.comp_format import Solution, NonDominatedSet, CompStore
import matplotlib.pyplot as plt
import os
import pandas as pd

# example: import data from test-example-n4.txt
# print(import_data.main(['test-example-n4']))

# example read data from test-example-n4.json
# print(json_methods.read('test-example-n4'))


class TTP:
    def __init__(self, info,distance, ants_number=10, TSPconstant_Q=1, alpha_pheromone=1, beta_pheromone=1, evaporation_rate=0.5, 
                 loop=100, scalerizing=0, w1=1, plotname='abc'):
        # info: data read from file
        self.info = info
        self.distance = distance
        self.ants_number = ants_number
        print('ants_number', ants_number)
        # initial pheromone
        self.pheromone = [10] * info['DIMENSION']
        # alpha: control the weight of pheromone
        self.alpha = 1
        # beta: control the weight of heuristic
        self.beta = 1
        self.TSPconstant_Q = TSPconstant_Q
        # alpha_pheromone： for time
        self.alpha_pheromone = alpha_pheromone
        # beta_pheromone: for profit
        self.beta_pheromone = beta_pheromone
        self.evaporation_rate = evaporation_rate
        self.loop = loop
        # We have pick_probability to chose the item
        self.pick_probability = 0.99
        self.scalerizing = scalerizing
        self.w1 = w1
        self.plotname = plotname

    def ants_init(self):
        return random.sample(range(self.info['DIMENSION']), self.ants_number)
    def normalize(self,lst):
        min_val = min(lst)
        max_val = max(lst)
        return [(x - min_val) / (max_val - min_val) for x in lst]
    def node_chose(self, i):
        # i: ant start from i-th country
        path = [i]
        unselected_node = [n for n in range(self.info['DIMENSION']) if n != i]

        while len(unselected_node) > 0:
            next_node = node_methods.select_next(
                path, unselected_node, self.info['nodes'], self.pheromone, self.alpha, self.beta)
            next_node_index = next_node['INDEX'] - 1
            path.append(next_node_index)
            unselected_node.remove(next_node_index)

        return path

    
    def item_chose(self, path):
        ret = [[] for _ in range(self.info['DIMENSION'])]
        for i in path:
            sub_items = self.info['node_item'][i]
            if not sub_items:  # Skip this iteration if sub_items is empty
                continue
            pheromone_values = [self.pheromone[item['ASSIGNED_NODE_NUMBER']-1] for item in sub_items]
            total_pheromone = sum(pheromone_values)
            if total_pheromone > 0:
                probabilities = [pheromone / total_pheromone for pheromone in pheromone_values]
            else:
                probabilities = [1 / len(sub_items) for _ in sub_items]  # Equal probabilities if no pheromone
            k = len(sub_items)  # Choose at most the number of items in sub_items
            chosen_items = random.choices(sub_items, probabilities, k=k)  # Choose items based on probabilities
            ret[i] = [1 if item in chosen_items else 0 for item in sub_items]  # Mark chosen items with 1, others with 0

        return ret

    def weight(self, i, node_path, items_selection):
        # i: i-th index of node_path

        w = 0
        for index in range(i):
            node = node_path[index]
            items = self.info['node_item'][node]
            selection = items_selection[node]
            for ind in range(len(items)):
                w += items[ind]['WEIGHT'] * selection[ind]

        return w

    def velocity(self, i, node_path, items_selection):
        # i: i-th node of node_path

        weight = self.weight(i, node_path, items_selection)
        if weight > self.info['CAPACITY_OF_KNAPSACK']:
            return self.info['MIN_SPEED']
        else:
            return self.info['MAX_SPEED'] - weight/self.info['CAPACITY_OF_KNAPSACK'] * (self.info['MAX_SPEED'] - self.info['MIN_SPEED'])

    def calculate_time(self, path, item_selection):
        time = 0
        distance = 0
        for i in range(self.info['DIMENSION']):
            distance += self.distance.loc[path[i],path[(i + 1) % self.info['DIMENSION']]].compute()
            time += distance / self.velocity(i, path, item_selection)


        return round(time, 4)

    def calculate_profit(self, item_selection):
        profit = 0
        for index in range(len(self.info['node_item'])):
            for ind in range(len(self.info['node_item'][index])):
                profit += self.info['node_item'][index][ind]['PROFIT'] * \
                    item_selection[index][ind]

        return profit

    def profit_with_renting_ratio(self, profit, time):
        # caculate profit with renting ratio
        return profit - self.info['RENTING_RATIO'] * time
    
    
    def scale1(self, profit, time):
        # caculate profit with renting ratio
        w2 = self.info['RENTING_RATIO']/self.w1
        return self.w1*profit + math.log(w2/time)
    
    def scale2(self, profit, time):
        # caculate profit with renting ratio
        w2 = self.info['RENTING_RATIO']/self.w1
        return self.w1*profit + math.exp(-w2*time)
    
    def normalize_number(self,num, min_val, max_val):
        return (num - min_val) / (max_val - min_val)
    def update_pheromone(self, path, item_selection, time, profit_RR):
        # path: path of ant
        # item_selection: item selection of ant
        # time: time of ant
        # profit: profit of ant with renting ratio

        # update pheromone
        time_normalised = self.normalize_number(time,0,10000)
        profit_normalised = self.normalize_number(profit_RR,0,10000000)
        #gamma = (self.alpha_pheromone * self.TSPconstant_Q / time) + (self.beta_pheromone * profit_RR)  # caculate gamma which is the scalarising function
        gamma = time_normalised * self.alpha_pheromone + profit_normalised * self.beta_pheromone
        for i in range(len(path)):
            self.pheromone[path[i]] = gamma  # update pheromone with gamma

    def degrade_pheromone(self):
        for i in range(len(self.pheromone)):
            # degrade pheromone with evaporation rate
            self.pheromone[i] -= self.pheromone[i] * self.evaporation_rate

    def once_ants_colony(self):
        ret = []
        ants_init_position = self.ants_init()
        for ant in ants_init_position:
            path = self.node_chose(ant)
            item_selection = self.item_chose(path)
            time = self.calculate_time(path, item_selection)
            profit = self.calculate_profit(item_selection)

            right_result = {
                'path': path,
                'item_selection': item_selection,
                'time': time,
                'profit': profit,
                'profit_with_renting_ratio': self.profit_with_renting_ratio(profit, time)
            }

            # print('path right?', node_methods.right_path(path, self.info['DIMENSION']))
            print('profit', profit)
            
            ret.append(right_result)

        return ret
    
    def plot_pareto(self, obj1, obj2):
        plt.scatter(obj1,obj2)
        plt.title('Pareto Plot Between 2 Objectives')
        plt.xlabel('Profit')
        plt.ylabel('Time')
        plt.show()
        #plt.savefig('/Plot/'+file_name+'pareto.jpg')
        file_path = 'Plot'
        my_file = self.plotname + 'pareto.jpg'
        #plt.savefig(os.path.join(file_path, my_file))
        
    def plot_objective(self, obj, iteration,objective_name):
        plt.plot(iteration, obj, linestyle='-', color='b', label='5')
        plt.title(f'{objective_name} Over Iteration Plot')
        plt.xlabel('Iterations')
        plt.ylabel(f'{objective_name}')
        plt.show()
        file_path = 'Plot'
        my_file = self.plotname + f'{objective_name}.jpg'
        #plt.savefig('/Plot/'+ file_name +'objective.jpg')
        #plt.savefig(os.path.join(file_path, my_file))
        
    def plot_both_objective(self, obj1, obj2, iteration):
        
        time = self.normalize(obj2)
        profit = self.normalize(obj1)
        plt.plot(iteration, profit, linestyle='-', color='b', label='profit')
        plt.plot(iteration,time, linestyle='-', color='r', label='time')
        plt.title('Both Objective Over Iteration Plot')
        plt.xlabel('Iterations')
        plt.ylabel('Objective')
        plt.legend()
        plt.show()
        file_path = 'Plot'
        my_file = self.plotname + 'both_objective.jpg'
        #plt.savefig('/Plot/'+ file_name +'both_objective.jpg')
        #plt.savefig(os.path.join(file_path, my_file))
    def plot_scatter(self, obj1, obj2,itr):
        time = self.normalize(obj2)
        profit = self.normalize(obj1)
        # Create a new figure with a size of 10x10 inches
        plt.figure(figsize=(10, 10))
        plt.scatter(obj1,obj2,itr)
        plt.autoscale(True)
        plt.plot(1,0,1,'ro')
        plt.title('Both Objective Over Iteration Plot')
        plt.xlabel('Profit')
        plt.ylabel('Time')
        plt.grid(True)
        plt.show()
        
    def main(self):
        solution = Solution()
        compstore = CompStore('O', f'{self.info["output_name"]}')
       
        # Create an instance of NonDominatedSet
        non_dominated_set = NonDominatedSet()
        
        run = []
        obj = []
        itr = []
        obj1 = []
        obj2 = []
        ants_init_position = self.ants_init()  # initial ants position
        for ant in tqdm(ants_init_position):  # for each ant
            t = 1  # loop time counter initialisation
            while t < self.loop:  # while loop time counter less than loop time
                path = self.node_chose(ant)  # chose path
                item_selection = self.item_chose(path)  # chose item
                time = self.calculate_time(
                    path, item_selection)  # caculate time
                profit = self.calculate_profit(
                    item_selection)  # caculate profit
                
                self.update_pheromone(
                    path, item_selection, time, profit)  # update pheromone
                self.degrade_pheromone()  # degrade pheromone
                solution.pi = path # append result to run
                solution.z = item_selection
                solution.time = time
                solution.profit = profit
                solution.objectives = [time, profit]
                obj.append(profit)
                itr.append(t)
                obj1.append(profit)
                obj2.append(time)


                t += 1  # loop time counter + 1
           
        non_dominated_set.add(solution)
        self.plot_pareto(obj1,obj2)
        self.plot_objective(obj1, itr, 'profit')
        self.plot_objective(obj2, itr, 'time')
        self.plot_both_objective(obj1, obj2, itr)
        self.plot_scatter(obj1, obj2,itr)
        # Write the non-dominated set to a file
        compstore.write_solution(non_dominated_set.entries)
        compstore.write_objectives(non_dominated_set.entries)
            
        
       


    # test-example-n4, a280-n279, a280-n1395, a280-n2790
ttp = TTP(json_methods.read('pla33810-n338090'), json_methods.read_csv('pla33810-n338090_distance'),ants_number=10, 
          loop=10,
            alpha_pheromone=1,
            beta_pheromone=1,
            evaporation_rate=0.9,
             TSPconstant_Q=10,
             scalerizing=0,
             w1=1,
             plotname='Experiment1')
ttp.main()
