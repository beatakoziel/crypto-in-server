import pygad
import numpy
import yfinance as yf


class CryptoData:
    def __init__(self, crypto, profit, risk):
        self.crypto = crypto
        self.profit = profit
        self.risk = risk


class AlgorithmInitialData:
    def __init__(self, amount, assets, solution_lambda, generations_number, solutions_per_population):
        self.amount = amount
        self.assets = assets
        self.solution_lambda = solution_lambda
        self.generations_number = generations_number
        self.solutions_per_population = solutions_per_population


class Solution:
    def __init__(self, asset_name, percentage_solution, money_solution):
        self.asset_name = asset_name
        self.percentage_solution = percentage_solution
        self.money_solution = money_solution


def fitness_func(solution, solution_idx):
    # ustawic liczbe genow na podstawie liczby wybranych aktywow
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


def divide_money_between_assets(algorithm_initial_data):
    # Creating an instance of the GA class inside the ga module. Some parameters are initialized within the constructor.
    ga_instance = pygad.GA(num_generations=algorithm_initial_data.generations_number,
                           init_range_low=0,
                           init_range_high=1,
                           num_parents_mating=num_parents_mating,
                           fitness_func=fitness_function,
                           sol_per_pop=algorithm_initial_data.solutions_per_population,
                           num_genes=len(algorithm_initial_data.assets),
                           on_generation=callback_generation,
                           gene_space={'low': 0, 'high': 1})
    ga_instance.run()
    ga_instance.plot_fitness()
    solution, solution_fitness, solution_idx = ga_instance.best_solution()
    solution_sum = sum(solution)
    percentage_solution = list(map(lambda x: (x / solution_sum) * 100, solution))
    print("Parameters of the best solution : {solution}".format(solution=percentage_solution))
    print("Fitness value of the best solution = {solution_fitness}".format(solution_fitness=solution_fitness))
    print("Index of the best solution : {solution_idx}".format(solution_idx=solution_idx))
    prediction = numpy.sum(solution)
    print("Predicted output based on the best solution : {prediction}".format(prediction=prediction))
    return list(
        map(lambda i, x: Solution(algorithm_initial_data.assets[i], x, algorithm_initial_data.amount * (x / 100)),
            percentage_solution))

