import flask

from flask_cors import CORS

app = flask.Flask(__name__)
app.config["DEBUG"] = True
CORS(app)


@app.route('/genetics', methods=['GET'])
def home():
    return "hello"


app.run()
