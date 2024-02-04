import numpy as np
import random

# Generate TTP problem instance
def generate_instance(n_cities):
    cities = np.random.rand(n_cities, 2) * 100
    weights = np.random.randint(1, 10, size=n_cities)
    profits = np.random.randint(1, 20, size=n_cities)
    knapsack_capacity = sum(weights) // 2
    return cities, weights, profits, knapsack_capacity

# Calculate distances between cities
def calculate_distances(cities):
    n_cities = len(cities)
    distances = np.zeros((n_cities, n_cities))
    for i in range(n_cities):
        for j in range(n_cities):
            distances[i, j] = np.linalg.norm(cities[i] - cities[j])
    return distances

# Initialize pheromones
def initialize_pheromones(n_cities):
    return np.ones((n_cities, n_cities))

# Choose the next city considering the knapsack capacity
def choose_next_city(current_city, pheromones, distances, weights, knapsack_capacity, remaining_items):
    probabilities = []
    for i in remaining_items:
        if weights[i] <= knapsack_capacity:  # Check if adding the item exceeds knapsack capacity
            probabilities.append((pheromones[current_city, i] ** alpha) * ((1 / distances[current_city, i]) ** beta))

    if not probabilities:  # If no valid items can be added to the knapsack, choose randomly
        return random.choice(remaining_items)

    total_prob = sum(probabilities)
    probabilities = [p / total_prob for p in probabilities]
    next_city = np.random.choice(remaining_items, p=probabilities)
    remaining_items.remove(next_city)
    knapsack_capacity -= weights[next_city]
    return next_city

# Update pheromones based on ant paths
def update_pheromones(pheromones, ants, distances, weights, profits):
    pheromones *= (1 - rho)
    for ant in ants:
        total_distance = sum(distances[i, j] for i, j in zip(ant[:-1], ant[1:]))
        total_profit = sum(profits[i] for i in ant)
        pheromone_delta = 1 / total_distance * total_profit
        for i, j in zip(ant[:-1], ant[1:]):
            pheromones[i, j] += pheromone_delta

# Ant Colony Optimization main function
def ant_colony_optimization(n_cities):
    cities, weights, profits, knapsack_capacity = generate_instance(n_cities)
    distances = calculate_distances(cities)
    pheromones = initialize_pheromones(n_cities)
    best_solution = []
    best_profit = 0

    for iteration in range(n_iterations):
        ants = []
        for ant_id in range(n_ants):
            remaining_items = list(range(n_cities))
            current_city = random.choice(remaining_items)
            remaining_items.remove(current_city)
            ant_path = [current_city]

            while remaining_items and knapsack_capacity > 0:
                next_city = choose_next_city(current_city, pheromones, distances, weights, knapsack_capacity, remaining_items)
                ant_path.append(next_city)
                current_city = next_city

            total_profit = sum(profits[i] for i in ant_path)
            if total_profit > best_profit:
                best_profit = total_profit
                best_solution = ant_path

            ants.append(ant_path)

        update_pheromones(pheromones, ants, distances, weights, profits)

    return best_solution, best_profit

# ACO parameters
n_ants = 10
n_iterations = 50
rho = 0.1
alpha = 1
beta = 2

# Run ACO algorithm to solve the TTP problem
n_cities = 20
best_solution, best_profit = ant_colony_optimization(n_cities)

print("Best solution:", best_solution)
print("Best profit:", best_profit)
