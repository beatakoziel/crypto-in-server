import json

import pygad
import numpy
import yfinance as yf

from models import GenerationResult, Solution, AlgorithmResult, CryptoData

generations_results = []

fitness_function_lambda = 0.5
chosen_crypto = []
crypto_results = []
period = "2mo"


def fitness_func(solution, sol_indx):
    result = 0
    solution_sum = sum(solution)
    percentage_solution = list(map(lambda x: (x / solution_sum) * 100, solution))
    for index, item in enumerate(crypto_results):
        result += percentage_solution[index] * calculate_lambda_result(fitness_function_lambda, item.risk, item.profit)
    return 1 / result


def calculate_lambda_result(lambda_value, risk, profit):
    return lambda_value * risk - (1 - lambda_value) * profit


def get_crypto_data_grouped_by_month(data):
    data_grouped_by_month = data.groupby(
        [data.index.month,
         data.index.year])
    return data_grouped_by_month


def calculate_crypto_monthly_profits(data_grouped_by_month):
    monthly_profits = []
    for month in data_grouped_by_month:
        daily_profits = calculate_daily_profits(month)
        monthly_profit = calculate_profit(daily_profits)
        monthly_profits.append(monthly_profit)
    return monthly_profits


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
    daily_average_array = array["Open"]
    average = sum(daily_average_array) / len(daily_average_array)
    result = list(map(lambda x: ((x - average) ** 2), daily_average_array))
    return numpy.sqrt((sum(result) / len(daily_average_array)))


fitness_function = fitness_func

num_generations = 5
num_parents_mating = 1
sol_per_pop = 10
num_genes = 2

last_fitness = 0


def callback_generation(ga_instance):
    global last_fitness
    print("Generation = {generation}".format(generation=ga_instance.generations_completed))
    print("Fitness    = {fitness}".format(fitness=ga_instance.best_solution()[1]))
    print("Change     = {change}".format(change=ga_instance.best_solution()[1] - last_fitness))
    last_fitness = ga_instance.best_solution()[1]
    generations_results.append(GenerationResult(ga_instance.generations_completed, ga_instance.best_solution()[1]))


def calculate_ranking(algorithm_initial_data):
    prepare_data_for_algorithm(algorithm_initial_data)
    ga_instance = pygad.GA(num_generations=algorithm_initial_data['generationsNumber'],
                           init_range_low=0,
                           init_range_high=1,
                           num_parents_mating=algorithm_initial_data['parentsMatingNumber'],
                           fitness_func=fitness_function,
                           sol_per_pop=algorithm_initial_data['solutionsPerPopulation'],
                           num_genes=len(algorithm_initial_data['assets']),
                           on_generation=callback_generation,
                           gene_space={'low': 0, 'high': 1},
                           parent_selection_type=algorithm_initial_data['parentSelectionType'],
                           K_tournament=algorithm_initial_data['kTournament'],
                           keep_parents=algorithm_initial_data['keepParents'],
                           crossover_type=algorithm_initial_data['crossoverType'],
                           crossover_probability=algorithm_initial_data['crossoverProbability'],
                           mutation_type=algorithm_initial_data['mutationType'],
                           mutation_probability=algorithm_initial_data['mutationProbability']
                           )
    ga_instance.run()

    return prepare_solution(ga_instance, algorithm_initial_data)


def prepare_solution(ga_instance, algorithm_initial_data):
    solution, solution_fitness, solution_idx = ga_instance.best_solution()
    solution_sum = sum(solution)
    percentage_solution = list(map(lambda x: (x / solution_sum) * 100, solution))
    rounded_percentage_solution = [round(number, 2) for number in percentage_solution]
    print_result(percentage_solution, solution, solution_fitness, solution_idx)
    solution = list(
        map(lambda i_x: Solution(algorithm_initial_data['assets'][i_x[0]], i_x[1],
                                 round(crypto_results[i_x[0]].profit, 2),
                                 round(crypto_results[i_x[0]].risk, 2)),
            enumerate(rounded_percentage_solution)))
    return json.dumps(AlgorithmResult(solution, generations_results), default=lambda o: o.__dict__)


def print_result(percentage_solution, solution, solution_fitness, solution_idx):
    print("Parameters of the best solution : {solution}".format(solution=percentage_solution))
    print("Fitness value of the best solution = {solution_fitness}".format(solution_fitness=solution_fitness))
    print("Index of the best solution : {solution_idx}".format(solution_idx=solution_idx))
    prediction = numpy.sum(solution)
    print("Predicted output based on the best solution : {prediction}".format(prediction=prediction))


def prepare_data_for_algorithm(algorithm_initial_data):
    global fitness_function_lambda, chosen_crypto, period, crypto_results
    fitness_function_lambda = algorithm_initial_data['lambdaValue']
    chosen_crypto = algorithm_initial_data['assets']

    generations_results.clear()
    crypto_results.clear()

    for crypto in chosen_crypto:
        ticker = yf.Ticker(crypto)
        if algorithm_initial_data['periodType'] == "period":
            data = ticker.history(period=algorithm_initial_data['period'])
        else:
            data = ticker.history(start=algorithm_initial_data['startDate'], end=algorithm_initial_data['endDate'])
        data_grouped_by_month = get_crypto_data_grouped_by_month(data)

        monthly_profits = calculate_crypto_monthly_profits(data_grouped_by_month)
        crypto_period_profit = calculate_profit(monthly_profits)

        crypto_period_risk = calculate_risk(data)

        crypto_results.append(CryptoData(crypto, crypto_period_profit, crypto_period_risk))
