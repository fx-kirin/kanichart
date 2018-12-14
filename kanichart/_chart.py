#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 zenbook <zenbook@zenbook-XPS>
#
# Distributed under terms of the MIT license.

"""

"""
import os, sys
import json
import jinja2
import pandas as pd
import numpy as np
from highcharts import Highstock
from highcharts.highstock.highstock_helper import jsonp_loader

def convert_pandas_datetime_to_float():
    pass

class StockChart(object):
    def __init__(self):
        self.symbols = []
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "files/theme.js")) as f:
            self.theme = f.read()
        self.number_of_candlestick_charts = 0
    
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
            self.number_of_candlestick_charts += 1
    
    def plot(self, title=False, width=600, height=300, load_js=None, js_sources=[]):
        chart_height = (height + 50)*self.number_of_candlestick_charts - 50 + 200
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
        
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "files/load.jinja")) as f:
            load_tempate = jinja2.Template(f.read())
            
        options = {
            'rangeSelector': {
                'buttons': [
                {
                    'type': 'minute',
                    'count': 180,
                    'text': '3h'
                },{
                    'type': 'minute',
                    'count': 360,
                    'text': '6h'
                }, {
                    'type': 'minute',
                    'count': 720,
                    'text': '12h'
                }, {
                    'type': 'minute',
                    'count': 60*24,
                    'text': '1d'
                }, {
                    'type': 'minute',
                    'count': 60*48,
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
                'inputEnabled' : False
                },

            'plotOptions':{
                'series': {
                    'turboThreshold:' : 0,
                    'dataGrouping' : {
                        'enabled' : False,
                    },
                    'animation': False,
                },
                
                'scatter': {
                    'turboThreshold:' : 0,
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
                'height' : 20
            },
            'chart' : {
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
            options['title'] = {'text' : title}
            
        if load_js:
            load_js = load_tempate.render(symbols=self.symbols)
            options['event']['load'] = load_js
        
        idx = -1
        current_y = -height
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
                        'top' : '%dpx'%(current_y),
                        'height': '%dpx'%(height),
                        'lineWidth': 2,
                        'offset': 0,
                })

            if chart_type == 'candlestick':
                H.add_data_set(data, chart_type, symbol, yAxis = idx, dataGrouping = {})
            elif chart_type == 'line':
                H.add_data_set(data, chart_type, symbol, yAxis = idx, dataGrouping = {})
            elif chart_type == 'scatter':
                H.add_data_set(data, chart_type, symbol, yAxis = idx, dataGrouping = {}, turboThreshold=0)
            
        H.set_dict_options(options)
        H.add_JSscript(self.theme, "head")
        for js_source in js_sources:
            H.add_JSsource(js_source)
        return H

class CandlestickCharts(object):
    """View Chart"""
    def __init__(self):
        self.symbols = []
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "files/theme.js")) as f:
            self.theme = f.read()
    
    def add_chart(self, symbol, data):
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
        else:
            raise RuntimeError("data parameter must be pandas DataFrame or list.")
        
        self.symbols.append((symbol, data))
    
    def plot(self, title=False, width=600, height=300, load_js=None, js_sources=[]):
        chart_height = (height + 50)*len(self.symbols) - 50 + 200
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
        
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "files/load.jinja")) as f:
            load_tempate = jinja2.Template(f.read())
            
        options = {
            'rangeSelector': {
                'buttons': [
                {
                    'type': 'minute',
                    'count': 180,
                    'text': '3h'
                },{
                    'type': 'minute',
                    'count': 360,
                    'text': '6h'
                }, {
                    'type': 'minute',
                    'count': 720,
                    'text': '12h'
                }, {
                    'type': 'minute',
                    'count': 60*24,
                    'text': '1d'
                }, {
                    'type': 'minute',
                    'count': 60*48,
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
                'inputEnabled' : False
                },

            'plotOptions':{
                'series': {
                    'turboThreshold:' : 0,
                    'dataGrouping' : {
                        'enabled' : False,
                    },
                    'animation': False,
                },
            },
            'navigator': {
                'enabled': True,
                'height' : 20
            },
            'chart' : {
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
            options['title'] = {'text' : title}
            
        if load_js:
            load_js = load_tempate.render(symbols=self.symbols)
            options['event']['load'] = load_js
        
        symbol_data = {}
        current_y = 50
        for idx, (symbol, data) in enumerate(self.symbols):
            symbol_data[symbol] = data
            
            options['yAxis'].append({
                    'labels': {
                        'align': 'right',
                        'x': -3
                    },
                    'title': {
                        'text': 'OHLC'
                    },
                    'top' : '%dpx'%(current_y),
                    'height': '%dpx'%(height),
                    'lineWidth': 2,
                    'offset': 0,
            })

            H.add_data_set(data, 'candlestick', symbol, yAxis = idx, dataGrouping = {
                            }
            )
            current_y += height + 50
            
        H.set_dict_options(options)
        H.add_JSscript(self.theme, "head")
        for js_source in js_sources:
            H.add_JSsource(js_source)
        return H
    
class LineCharts(object):
    """View Chart"""
    def __init__(self, width=1100):
        self.symbols = []
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "files/theme.js")) as f:
            self.theme = f.read()
    
    def add_chart(self, symbol, data):
        if isinstance(data, list):
            pass
        elif isinstance(data, pd.Series):
            data = data.copy()
            if isinstance(data.index, pd.DatetimeIndex):
                data.index = data.index.values.astype(np.int64) // 10 ** 6
            index = data.index.values
            values = data.tolist()
            data = [[int(i), v] for i, v in zip(index, values)]
        self.symbols.append((symbol, data))
    
    def plot(self, title=False, width=600, height=300, load_js=None, js_sources=[]):
        chart_height = (height + 50)*1 - 50 + 200
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
        
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "files/load.jinja")) as f:
            load_tempate = jinja2.Template(f.read())
            
        options = {
            'rangeSelector': {
                'buttons': [
                {
                    'type': 'minute',
                    'count': 180,
                    'text': '3h'
                },{
                    'type': 'minute',
                    'count': 360,
                    'text': '6h'
                }, {
                    'type': 'minute',
                    'count': 720,
                    'text': '12h'
                }, {
                    'type': 'minute',
                    'count': 60*24,
                    'text': '1d'
                }, {
                    'type': 'minute',
                    'count': 60*48,
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
                'inputEnabled' : False
                },

            'plotOptions':{
                'series': {
                    'turboThreshold:' : 0,
                    'dataGrouping' : {
                        'enabled' : False,
                    },
                    'animation': False
                }
            },
            'navigator': {
                'enabled': True,
                'height' : 20
            },
            'chart' : {
                'animation': False,
            },
            
            'legend': {
                'enabled': True,
            },
            'yAxis': [],
            
            'title': {
                'text': '',
                'style': {
                    'display': 'none'
                }
            },
        }
        if title:
            options['title'] = {'text' : title}
            
        if load_js:
            load_js = load_tempate.render(symbols=self.symbols)
            options['event']['load'] = load_js
        
        symbol_data = {}
        for idx, (symbol, data) in enumerate(self.symbols):
            symbol_data[symbol] = data
            
            options['yAxis'].append({
                    'labels': {
                        'align': 'right',
                        'x': -3
                    },
                    'title': {
                        'text': 'y'
                    },
                    'lineWidth': 2,
                    'offset': 0,
            })

            H.add_data_set(data, 'line', symbol, dataGrouping = {})
            
        H.set_dict_options(options)
        H.add_JSscript(self.theme, "head")
        for js_source in js_sources:
            H.add_JSsource(js_source)
        return H
