#
# from pyeasyga import pyeasyga
# import pandas as pd
#
# file_name1 = "Binance_ETHUSDT_d.csv"
# file_name2 = "Binance_BTCUSDT_d.csv"
#
# col_list = ["Name", "Department"]
# raw_data1 = pd.read_csv(file_name1)
# raw_data2 = pd.read_csv(file_name2)
# # data = [('pear', 50), ('apple', 35), ('banana', 40)]
# data = [raw_data1, raw_data2]
# ga = pyeasyga.GeneticAlgorithm(data)
#
#
# def fitness (individual, data):
#     fitness = 0
#     if individual.count(1) == 2:
#         for (selected, (fruit, profit)) in zip(individual, data):
#             if selected:
#                 fitness += profit
#     return fitness
#
# ga.fitness_function = fitness
#
# ga.run()
#
# print(ga.best_individual())

import pygad
import pandas as pd
import numpy

"""
Given the following function:
    y = f(w1:w6) = w1x1 + w2x2 + w3x3 + w4x4 + w5x5 + 6wx6
    where (x1,x2,x3,x4,x5,x6)=(4,-2,3.5,5,-11,-4.7) and y=44
What are the best values for the 6 weights (w1 to w6)? We are going to use the genetic algorithm to optimize this function.
"""

file_name1 = "Binance_ETHUSDT_d.csv"
file_name2 = "Binance_BTCUSDT_d.csv"
col_list = ["Name", "Department"]
raw_data1 = pd.read_csv(file_name1)
raw_data2 = pd.read_csv(file_name2)
function_inputs = [raw_data1, raw_data2]
# function_inputs = [4, -2, 3.5, 5, -11, -4.7]  # Function inputs.
desired_output = 44  # Function output.


def fitness_func(solution, solution_idx):
    # output = numpy.sum(solution * function_inputs)
    zysk = numpy.sum(solution)
    # fitness = 1.0 / numpy.sum(solution) #maksymalizacja
    return zysk


fitness_function = fitness_func

num_generations = 100  # Number of generations.
num_parents_mating = 7  # Number of solutions to be selected as parents in the mating pool.

# To prepare the initial population, there are 2 ways:
# 1) Prepare it yourself and pass it to the initial_population parameter. This way is useful when the user wants to start the genetic algorithm with a custom initial population.
# 2) Assign valid integer values to the sol_per_pop and num_genes parameters. If the initial_population parameter exists, then the sol_per_pop and num_genes parameters are useless.
sol_per_pop = 50  # Number of solutions in the population.
num_genes = len(function_inputs)

last_fitness = 0


def callback_generation(ga_instance):
    global last_fitness
    print("Generation = {generation}".format(generation=ga_instance.generations_completed))
    print("Fitness    = {fitness}".format(fitness=ga_instance.best_solution()[1]))
    print("Change     = {change}".format(change=ga_instance.best_solution()[1] - last_fitness))
    last_fitness = ga_instance.best_solution()[1]


# Creating an instance of the GA class inside the ga module. Some parameters are initialized within the constructor.
ga_instance = pygad.GA(num_generations=num_generations,
                       init_range_low=0,
                       init_range_high=1,
                       num_parents_mating=num_parents_mating,
                       fitness_func=fitness_function,
                       sol_per_pop=sol_per_pop,
                       num_genes=num_genes,
                       on_generation=callback_generation,
                       gene_space=[{'low': 0, 'high': 1}, {'low': 0, 'high': 1}],
                       )

# Running the GA to optimize the parameters of the function.
ga_instance.run()

# After the generations complete, some plots are showed that summarize the how the outputs/fitenss values evolve over generations.
ga_instance.plot_fitness()

# Returning the details of the best solution.
solution, solution_fitness, solution_idx = ga_instance.best_solution()
solutionSum = sum(solution)
percentageSolution = list(map(lambda x: (x / solutionSum)*100, solution))
print("Parameters of the best solution : {solution}".format(solution=percentageSolution))
print("Fitness value of the best solution = {solution_fitness}".format(solution_fitness=solution_fitness))
print("Index of the best solution : {solution_idx}".format(solution_idx=solution_idx))

prediction = numpy.sum(solution)
print("Predicted output based on the best solution : {prediction}".format(prediction=prediction))
