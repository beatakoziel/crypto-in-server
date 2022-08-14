import json

import pygad
import numpy
import yfinance as yf


class CryptoData:
    def __init__(self, crypto, profit, risk):
        self.crypto = crypto
        self.profit = profit
        self.risk = risk

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)


class AlgorithmInitialData:
    def __init__(self, amount, assets, solutionLambda, generationsNumber, solutionsPerPopulation):
        self.amount = amount
        self.assets = assets
        self.solutionLambda = solutionLambda
        self.generationsNumber = generationsNumber
        self.solutionsPerPopulation = solutionsPerPopulation


class Solution:
    def __init__(self, assetName, percentageSolution, moneySolution):
        self.assetName = assetName
        self.percentageSolution = percentageSolution
        self.moneySolution = moneySolution

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)


class GenerationResult:
    def __init__(self, generation, fitness):
        self.generation = generation
        self.fitness = fitness


class AlgorithmResult:

    def __init__(self, solution, generations):
        self.solution = solution
        self.generations_results = generations


generations_results = []


def fitness_func(solution, solution_idx):
    # ustawic liczbe genow na podstawie liczby wybranych aktywow
    solution_lambda = 0.7  # we don't care about the risk
    chosen_crypto = ['AMZN', 'BTC-USD']  # create enum, input from user
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
    return 1 / result


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
num_parents_mating = 1  # Number of solutions to be selected as parents in the mating pool.

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
    generations_results.append(GenerationResult(ga_instance.generations_completed, ga_instance.best_solution()[1]))


def divide_money_between_assets(algorithm_initial_data):
    # Creating an instance of the GA class inside the ga module. Some parameters are initialized within the constructor.
    ga_instance = pygad.GA(num_generations=algorithm_initial_data['generationsNumber'],
                           init_range_low=0,
                           init_range_high=1,
                           num_parents_mating=num_parents_mating,
                           fitness_func=fitness_function,
                           sol_per_pop=2,
                           num_genes=len(algorithm_initial_data['assets']),
                           on_generation=callback_generation,
                           gene_space={'low': 0, 'high': 1})
    ga_instance.run()
    ga_instance.plot_fitness()
    solution, solution_fitness, solution_idx = ga_instance.best_solution()
    solution_sum = sum(solution)
    percentage_solution = list(map(lambda x: (x / solution_sum) * 100, solution))
    rounded_percentage_solution = [round(number) for number in percentage_solution]
    print("Parameters of the best solution : {solution}".format(solution=percentage_solution))
    print("Fitness value of the best solution = {solution_fitness}".format(solution_fitness=solution_fitness))
    print("Index of the best solution : {solution_idx}".format(solution_idx=solution_idx))
    prediction = numpy.sum(solution)
    print("Predicted output based on the best solution : {prediction}".format(prediction=prediction))
    solution = list(
        map(lambda i_x: Solution(algorithm_initial_data['assets'][i_x[0]], i_x[1],
                                 algorithm_initial_data['amount'] * (i_x[1] / 100)),
            enumerate(rounded_percentage_solution)))
    result = json.dumps(AlgorithmResult(solution, generations_results), default=lambda o: o.__dict__)
    generations_results.clear()
    return result
