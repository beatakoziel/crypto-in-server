from json import dumps

import flask
from flask import request, Response

from flask_cors import CORS

from main import calculate_ranking

app = flask.Flask(__name__)
app.config["DEBUG"] = True

cors = CORS(app, resources={"/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/calculator/divide', methods=['POST'])
def calculate():
    algorithm_initial_data = request.json
    response = calculate_ranking(algorithm_initial_data)
    return Response(response)


@app.route('/info/assets', methods=['GET'])
def get_assets_list():
    return flask.jsonify(
        ["BTC-USD", "ETH-USD", "DOGE-USD", "SHIB-USD", "DOT-USD", "AMZN", "DLTR", "LUNA-USD", "MANA-USD"])


@app.route('/info/periods', methods=['GET'])
def get_periods_list():
    return flask.jsonify(
        ["1mo", "3mo", "6mo", "1y", "2y", "5y", "10y"])


app.run()
