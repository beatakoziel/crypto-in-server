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

import pygad
import numpy
import yfinance as yf

"""
Given the following function:
    y = f(w1:w6) = w1x1 + w2x2 + w3x3 + w4x4 + w5x5 + 6wx6
    where (x1,x2,x3,x4,x5,x6)=(4,-2,3.5,5,-11,-4.7) and y=44
What are the best values for the 6 weights (w1 to w6)? We are going to use the genetic algorithm to optimize this function.
"""


class CryptoData:
    def __init__(self, crypto, profit, risk):
        self.crypto = crypto
        self.profit = profit
        self.risk = risk


def fitness_func(solution, solution_idx):
    # fitness = 1.0 / numpy.sum(solution) #maksymalizacja
    #sprawdzenie czy liczba genow zgadza sie z liczbą aktywow do wyliczenia
    solution_lambda = 0.7  # we don't care about the risk
    chosen_crypto = ['FB', 'BTC-USD']  # create enum, input from user
    period = "2mo"  # create enum, input from user
    crypto_results = []
    for crypto in chosen_crypto:
        ticker = yf.Ticker(crypto)
        data = ticker.history(period=period)
        data_grouped_by_month = get_crypto_data_grouped_by_month(data)

        monthly_profits = calculate_crypto_monthly_profits(data_grouped_by_month)
        crypto_period_profit = calculate_profit(monthly_profits)

        crypto_period_risk = calculate_risk(data)

        crypto_results.append(CryptoData(crypto, crypto_period_profit, crypto_period_risk))
    result = 0
    for index, item in enumerate(crypto_results):
        result += solution[index] * (solution_lambda * item.risk - (1 - solution_lambda) * item.profit)
    return 1/result


def calculate_crypto_monthly_profits(data_grouped_by_month):
    monthly_profits = []
    for month in data_grouped_by_month:
        daily_profits = calculate_daily_profits(month)
        monthly_profit = calculate_profit(daily_profits)
        monthly_profits.append(monthly_profit)
    return monthly_profits


def get_crypto_data_grouped_by_month(data):
    data_grouped_by_month = data.groupby(
        [data.index.month,
         data.index.year])  # we have to group by something like month and year, because we can have 05.2022 and 05.2023
    return data_grouped_by_month


def calculate_daily_profits(month):
    daily_profits = []
    for index in range(len(month[1]["Close"])):
        day_close_value = month[1]["Close"][index]
        day_open_value = month[1]["Open"][index]
        daily_profits.append((day_close_value / day_open_value) - 1)
    return daily_profits


def calculate_profit(array):
    # array = numpy.array(arr, dtype=numpy.float64)
    result = (1 + array[0])
    for element in array:
        result *= (1 + element)
    return result - 1


def calculate_risk(array):
    daily_average_array = array["Open"]  # here map array to average of open and close daily value
    average = sum(daily_average_array) / len(daily_average_array)
    result = list(map(lambda x: ((x - average) ** 2), daily_average_array))
    return numpy.sqrt(sum(result) / (len(daily_average_array) - 1))


fitness_function = fitness_func

num_generations = 5  # Number of generations.
num_parents_mating = 7  # Number of solutions to be selected as parents in the mating pool.

# To prepare the initial population, there are 2 ways:
# 1) Prepare it yourself and pass it to the initial_population parameter. This way is useful when the user wants to start the genetic algorithm with a custom initial population.
# 2) Assign valid integer values to the sol_per_pop and num_genes parameters. If the initial_population parameter exists, then the sol_per_pop and num_genes parameters are useless.
sol_per_pop = 10  # Number of solutions in the population.
num_genes = 2

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
                       gene_space={'low': 0, 'high': 1})

# Running the GA to optimize the parameters of the function.
ga_instance.run()

# After the generations complete, some plots are showed that summarize the how the outputs/fitenss values evolve over generations.
ga_instance.plot_fitness()

# Returning the details of the best solution.
solution, solution_fitness, solution_idx = ga_instance.best_solution()
solutionSum = sum(solution)
percentageSolution = list(map(lambda x: (x / solutionSum) * 100, solution))
print("Parameters of the best solution : {solution}".format(solution=percentageSolution))
print("Fitness value of the best solution = {solution_fitness}".format(solution_fitness=solution_fitness))
print("Index of the best solution : {solution_idx}".format(solution_idx=solution_idx))

prediction = numpy.sum(solution)
print("Predicted output based on the best solution : {prediction}".format(prediction=prediction))
