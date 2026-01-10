#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################
#
# Copyright (C) 2015-2023 Daniel Rodriguez
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import argparse

import quanttrader as trader


class St0(trader.SignalStrategy):
    def __init__(self):
        sma1, sma2 = trader.ind.SMA(period=10), trader.ind.SMA(period=30)
        crossover = trader.ind.CrossOver(sma1, sma2)
        self.signal_add(trader.SIGNAL_LONG, crossover)


class St1(trader.SignalStrategy):
    def __init__(self):
        sma1 = trader.ind.SMA(period=10)
        crossover = trader.ind.CrossOver(self.data.close, sma1)
        self.signal_add(trader.SIGNAL_LONG, crossover)


class StFetcher(object):
    _STRATS = [St0, St1]

    def __new__(cls, *args, **kwargs):
        idx = kwargs.pop('idx')

        obj = cls._STRATS[idx](*args, **kwargs)
        return obj


def runstrat(pargs=None):
    args = parse_args(pargs)

    engine = trader.Engine()
    data = trader.feeds.QuanttraderCSVData(dataname=args.data)
    engine.adddata(data)

    engine.addanalyzer(trader.analyzers.Returns)
    engine.optstrategy(StFetcher, idx=[0, 1])
    results = engine.run(maxcpus=args.maxcpus, optreturn=args.optreturn)

    strats = [x[0] for x in results]  # flatten the result
    for i, strat in enumerate(strats):
        rets = strat.analyzers.returns.get_analysis()
        print('Strat {} Name {}:\n  - analyzer: {}\n'.format(
            i, strat.__class__.__name__, rets))


def parse_args(pargs=None):

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Sample for strategy selection')

    parser.add_argument('--data', required=False,
                        default='../../datas/2005-2006-day-001.txt',
                        help='Data to be read in')

    parser.add_argument('--maxcpus', required=False, action='store',
                        default=None, type=int,
                        help='Limit the numer of CPUs to use')

    parser.add_argument('--optreturn', required=False, action='store_true',
                        help='Return reduced/mocked strategy object')

    return parser.parse_args(pargs)


if __name__ == '__main__':
    runstrat()
