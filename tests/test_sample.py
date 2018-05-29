#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 zenbook <zenbook@zenbook-UX21A>
#

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import unittest
import kanichart as kani
import datetime
import pandas_datareader.data as web

class Test(unittest.TestCase):
    def setUp(self):
        pass


    def tearDown(self):
        pass

    def testName(self):
        start = datetime.datetime(2012, 1, 1)
        end = datetime.datetime(2017, 12, 31)

        df = web.DataReader('SNE', 'morningstar', start, end)
        df.reset_index(level=0, inplace=True)
        
        candle = kani.CandlestickCharts()
        candle.add_chart('SNE', df)
        H = candle.plot()
        H.save_file('candle_chart')
        
        candle = kani.LineCharts()
        candle.add_chart('SNE', df['Open'])
        H = candle.plot()
        H.save_file('line_chart')

if __name__ == '__main__':
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
