import unittest


from main import calculate_profit, calculate_crypto_monthly_profits, calculate_risk, calculate_lambda_result

from main import get_crypto_data_grouped_by_month
import yfinance as yf


class TestCalculateProfitMethods(unittest.TestCase):

    def test_get_crypto_data_grouped_by_month(self):
        ticker = yf.Ticker("BTC-USD")
        data = ticker.history(start="2022-01-01", end="2022-03-01")
        grouped_data = get_crypto_data_grouped_by_month(data)
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

if __name__ == '__main__':
    unittest.main()
