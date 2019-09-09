#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 zenbook <zenbook@zenbook-XPS>
#
# Distributed under terms of the MIT license.

"""

"""
import os

import jinja2
import numpy as np
import pandas as pd

from kani_highcharts import Highstock


def convert_pandas_datetime_to_float():
    pass


class StockChart(object):
    def __init__(self):
        self.symbols = []
        self.jsonp_symbols = []
        self.is_jsonp_enabled = False
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "files/theme.js")) as f:
            self.theme = f.read()
        self.number_of_charts = 0

    def add_chart(self, chart_type, symbol, data, is_new_chart=True):
        if isinstance(data, list):
            pass
        elif isinstance(data, pd.DataFrame):
            try:
                data = data[['Open', 'High', 'Low', 'Close']].copy()
            except KeyError:
                try:
                    data = data[['open', 'high', 'low', 'close']].copy()
                except KeyError:
                    raise KeyError("data object must have ['Open', 'High', 'Low', 'Close']")
            if isinstance(data.index, pd.DatetimeIndex):
                data.index = data.index.values.astype(np.int64) // 10 ** 6
            index = data.index.values
            values = data.values.tolist()
            data = [[int(i), o, h, l, c] for i, (o, h, l, c) in zip(index, values)]
            data
        elif isinstance(data, pd.Series):
            data = data.copy()
            if isinstance(data.index, pd.DatetimeIndex):
                data.index = data.index.values.astype(np.int64) // 10 ** 6
            index = data.index.values
            values = data.tolist()
            data = [[int(i), v] for i, v in zip(index, values)]
        else:
            raise RuntimeError("data parameter must be pandas DataFrame or list.")

        self.symbols.append((chart_type, symbol, data, is_new_chart))
        if is_new_chart:
            self.number_of_charts += 1

    def add_chart_from_jsonp(self, chart_type, symbol, url, is_new_chart=True):
        self.jsonp_symbols.append((chart_type, symbol, url, is_new_chart))
        self.is_jsonp_enabled = True
        if is_new_chart:
            self.number_of_charts += 1

    def plot(self, title=False, width=600, height=300, load_js=None, js_sources=[]):
        chart_height = (height + 50) * self.number_of_charts - 50 + 200
        H = Highstock(width=width, height=chart_height)
        H.JSsource = [
            'https://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'https://code.highcharts.com/stock/6/highstock.js',
            'https://code.highcharts.com/stock/6/modules/exporting.js',
            'https://code.highcharts.com/6/highcharts-more.js',
        ]
        groupingUnits = [
            ['hour', [60]],
        ]

        options = {
            'rangeSelector': {
                'buttons': [
                    {
                        'type': 'minute',
                        'count': 180,
                        'text': '3h'
                    }, {
                        'type': 'minute',
                        'count': 360,
                        'text': '6h'
                    }, {
                        'type': 'minute',
                        'count': 720,
                        'text': '12h'
                    }, {
                        'type': 'minute',
                        'count': 60 * 24,
                        'text': '1d'
                    }, {
                        'type': 'minute',
                        'count': 60 * 48,
                        'text': '2d'
                    }, {
                        'type': 'second',
                        'count': 1,
                        'text': '1s'
                    }, {
                        'type': 'second',
                        'count': 10,
                        'text': '10s'
                    }
                ],
                'selected': 4,
                'inputEnabled': False
            },

            'plotOptions': {
                'series': {
                    'turboThreshold:': 0,
                    'dataGrouping': {
                        'enabled': False,
                    },
                    'animation': False,
                },

                'scatter': {
                    'turboThreshold:': 0,
                    'marker': {
                        'radius': 5,
                        'symbol': 'circle',
                        'states': {
                            'hover': {
                                'enabled': True,
                                'lineColor': 'rgb(100,100,100)'
                            }
                        }
                    },
                    'tooltip': {
                        'pointFormat': '{series.name} x:{point.x}, y:{point.y}'
                        #'pointFormatter': """
                        #function () { debugger; }
                        #"""
                    },
                    'states': {
                        'hover': {
                            'marker': {
                                'enabled': False
                            }
                        }
                    },
                },
            },
            'navigator': {
                'enabled': True,
                'height': 20
            },
            'chart': {
                'animation': False,
            },
            'title': {
                'text': '',
                'style': {
                    'display': 'none'
                }
            },

            'legend': {
                'enabled': True,
            },
            'yAxis': []
        }
        if title:
            options['title'] = {'text': title}

        if load_js:
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "files/load.jinja")) as f:
                load_tempate = jinja2.Template(f.read())
            load_js = load_tempate.render(symbols=self.symbols)
            options['event']['load'] = load_js

        idx = -1
        current_y = -height
        if self.is_jsonp_enabled:
            for chart_type, symbol, url, is_new_chart in self.jsonp_symbols:
                if is_new_chart:
                    idx += 1
                    current_y += height + 50
                    options['yAxis'].append({
                        'labels': {
                            'align': 'right',
                            'x': -3
                        },
                        'title': {
                            'text': 'y'
                        },
                        'top': '%dpx' % (current_y),
                        'height': '%dpx' % (height),
                        'lineWidth': 2,
                        'offset': 0,
                    })
                if chart_type == 'candlestick':
                    H.add_data_from_jsonp(url, chart_type, symbol, yAxis=idx, dataGrouping={})
                elif chart_type == 'line':
                    H.add_data_from_jsonp(url, chart_type, symbol, yAxis=idx, dataGrouping={})
                elif chart_type == 'scatter':
                    H.add_data_from_jsonp(url, chart_type, symbol, yAxis=idx, dataGrouping={}, turboThreshold=0)
        else:
            for chart_type, symbol, data, is_new_chart in self.symbols:
                if is_new_chart:
                    idx += 1
                    current_y += height + 50
                    options['yAxis'].append({
                        'labels': {
                            'align': 'right',
                            'x': -3
                        },
                        'title': {
                            'text': 'y'
                        },
                        'top': '%dpx' % (current_y),
                        'height': '%dpx' % (height),
                        'lineWidth': 2,
                        'offset': 0,
                    })

                if chart_type == 'candlestick':
                    H.add_data_set(data, chart_type, symbol, yAxis=idx, dataGrouping={})
                elif chart_type == 'line':
                    H.add_data_set(data, chart_type, symbol, yAxis=idx, dataGrouping={})
                elif chart_type == 'scatter':
                    H.add_data_set(data, chart_type, symbol, yAxis=idx, dataGrouping={}, turboThreshold=0)

        H.set_dict_options(options)
        H.add_JSscript(self.theme, "head")
        for js_source in js_sources:
            H.add_JSsource(js_source)
        return H


class CandlestickCharts(StockChart):
    def add_chart(self, symbol, data, is_new_chart=True):
        super(CandlestickCharts, self).add_chart('line', symbol, data, is_new_chart)


class LineCharts(StockChart):
    def add_chart(self, symbol, data, is_new_chart=True):
        super(LineCharts, self).add_chart('line', symbol, data, is_new_chart)
