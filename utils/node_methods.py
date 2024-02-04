import math
import random


def judge_near(node1, node2, gap):
    return abs(node1['X'] - node2['X']) < gap and abs(node1['Y'] - node2['Y']) < gap


def select_near(node, list, gap=10):
    # gap: Difference from the horizontal and vertical coordinates
    ret = []
    while len(ret) < 1:
        for item in list:
            if judge_near(node, item, gap):
                distance = math.sqrt(
                    (node['X'] - item['X'])**2 + (node['Y'] - item['Y'])**2)
                item['heuristic'] = round(
                    100 if distance == 0 else 1 / distance, 4)

                # if distance == 0:
                #     print('Same coordinates:', node, item)

                ret.append(item)

        gap += 5
    return ret


def caculate_probability(near_list, pheromone, alpha, beta):
    moleculars = []
    for item in near_list:
        moleculars.append(
            (pheromone[item['INDEX'] - 1] ** alpha) * (item['heuristic'] ** beta))

    total = sum(moleculars)

    return [round(x/total, 4) for x in moleculars]


def roulette_wheel_selection(probabilities):
    # items: items list
    # probabilities: selection probability dictionary for each item

    cumulative_prob = 0
    random_num = random.uniform(0, sum(probabilities))

    for i in range(len(probabilities)):
        cumulative_prob += probabilities[i]
        if cumulative_prob >= random_num:
            return i


def select_next(path, unselected_node, node_list, pheromone, alpha, beta):
    #current = node_list[path[len(path) - 1]]
    unselected_node_list = [node_list[i] for i in unselected_node]

    probabilities = [pheromone[node['INDEX'] - 1] for node in unselected_node_list]
    selected = probabilities.index(max(probabilities))

    return unselected_node_list[selected]


def right_path(path, num):
    for i in range(num):
        if i not in path:
            return False
    return True
