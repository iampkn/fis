from flask import Flask, jsonify, request, abort
import pandas as pd

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello, World!"


if __name__ == "__main__":
    app.run(debug=True)
