from json import dumps

import flask
from flask import request, json, make_response, jsonify, Response

from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from main import divide_money_between_assets, Solution

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
    return flask.jsonify(["FB", "AMZN"])


app.run()
