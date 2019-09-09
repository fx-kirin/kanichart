"""A separate Flask app that serves fake endpoints for demo purposes."""

# -*- coding: utf-8 -*-

from itertools import combinations
import json
import locale
import os
from datetime import timedelta as td
from datetime import datetime as dt
from random import randrange as rr
from random import choice, random
import requests
import time

from flask import (
    Flask,
    abort,
    request,
    jsonify,
    render_template,
)
from flask_cors import CORS
from flask_cors import cross_origin

app = Flask('endpoints_test')
CORS(app)
app.config['SECRET_KEY'] = 'NOTSECURELOL'
app.debug = True

STRESS_MAX_POINTS = 300

locale.setlocale(locale.LC_ALL, '')

cwd = os.getcwd()


@cross_origin()
@app.route('/ohlc')
def ohlc():
    result = requests.get('https://www.highcharts.com/samples/data/aapl-ohlc.json')
    return result.text


if __name__ == '__main__':
    PORT = int(os.getenv('PORT', 5004))
    HOST = os.getenv('HOST', '0.0.0.0')
    app.run(debug=True, host=HOST, port=PORT)
