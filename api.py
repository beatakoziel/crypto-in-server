from json import dumps

import flask
from flask import request, Response

from flask_cors import CORS

from main import divide_money_between_assets

app = flask.Flask(__name__)
app.config["DEBUG"] = True

cors = CORS(app, resources={"/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/calculator/divide', methods=['POST'])
def calculate():
    algorithm_initial_data = request.json
    response = divide_money_between_assets(algorithm_initial_data)
    return Response(response)


@app.route('/info/assets', methods=['GET'])
def get_assets_list():
    return flask.jsonify(
        ["AAPL", "BTC-USD", "TSLA", "ETH-USD", "MSFT", "NVDA", "DOGE-USD", "JNJ", "INTC", "ABNB", "SHIB-USD", "FRZA",
         "FB", "DOT-USD", "AMZN"])


@app.route('/info/periods', methods=['GET'])
def get_periods_list():
    return flask.jsonify(
        ["1mo", "3mo", "6mo", "1y", "2y", "5y", "10y"])


app.run()
