import flask

from flask_cors import CORS

from main import divide_money_between_assets

app = flask.Flask(__name__)
app.config["DEBUG"] = True


cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/calculator/divide', methods=['POST'])
def divide_money_between_assets(algorithm_initial_data):
    return flask.jsonify(divide_money_between_assets(algorithm_initial_data))


@app.route('/info/assets', methods=['GET'])
def get_assets_list():
    return flask.jsonify(["BTC", "AMZN"])


app.run()
