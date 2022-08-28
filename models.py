import json


class CryptoData:
    def __init__(self, crypto, profit, risk):
        self.crypto = crypto
        self.profit = profit
        self.risk = risk

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)


class Solution:
    def __init__(self, assetName, percentageSolution, profit, risk):
        self.assetName = assetName
        self.percentageSolution = percentageSolution
        self.profit = profit
        self.risk = risk

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
