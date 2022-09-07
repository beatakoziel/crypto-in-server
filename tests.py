import unittest

from main import calculate_profit, calculate_crypto_monthly_profits, calculate_risk, calculate_lambda_result, \
    prepare_data_for_algorithm, calculate_ranking

from main import get_crypto_data_grouped_by_month
import yfinance as yf


class TestCalculateProfitMethods(unittest.TestCase):

    def test_get_crypto_data_grouped_by_month(self):
        # given
        ticker = yf.Ticker("BTC-USD")
        data = ticker.history(start="2022-01-01", end="2022-03-01")
        # when
        grouped_data = get_crypto_data_grouped_by_month(data)
        # then
        self.assertEqual(len(grouped_data), 3)

    def test_calculate_crypto_monthly_profits(self):
        ticker = yf.Ticker("BTC-USD")
        data = ticker.history(start="2022-01-01", end="2022-03-01")
        data_grouped_by_month = get_crypto_data_grouped_by_month(data)
        monthly_profits = calculate_crypto_monthly_profits(data_grouped_by_month)
        self.assertEqual(len(monthly_profits), 3)

    def test_calculate_profit(self):
        monthly_profits = [-0.1451765616186651, 0.1333096623068004, -0.03625371694281854]
        general_profit = calculate_profit(monthly_profits)
        self.assertEqual(general_profit, -0.20188743030570167)

    def test_calculate_risk(self):
        ticker = yf.Ticker("BTC-USD")
        data = ticker.history(start="2022-01-01", end="2022-03-01")
        risk = calculate_risk(data)
        self.assertEqual(risk, 3170.6370673714005)

    def test_calculate_lambda_result(self):
        lambda_result = calculate_lambda_result(0.1, 3170.6370673714005, -0.20188743030570167)
        self.assertEqual(lambda_result, 317.2454054244152)

    def test_prepare_data_for_algorithm(self):
        prepare_data_for_algorithm({"lambdaValue": 0.5, "assets": ["BTC-USD"], "period": "1mo", "periodType": "period"})

    def test_calculate_ranking(self):
        result = calculate_ranking({
            "periodType": "period",
            "period": "1mo",
            "startDate": "2021-01-01",
            "endDate": "2022-01-01",
            "assets": [
                "ETH-USD",
                "BTC-USD"
            ],
            "lambdaValue": 0.5,
            "generationsNumber": 10,
            "solutionsPerPopulation": 10,
            "parentsMatingNumber": 1,
            "parentSelectionType": "sss",
            "kTournament": 3,
            "keepParents": -1,
            "crossoverType": "single_point",
            "crossoverProbability": None,
            "mutationType": "random",
            "mutationProbability": None
        })
        self.assertIsNotNone(result)


if __name__ == '__main__':
    unittest.main()
