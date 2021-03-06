# Copyright 2017 Ihar Hrachyshka <ihar.hrachyshka@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import abc
import collections
import time

import six
from stevedore.enabled import EnabledExtensionManager


@six.add_metaclass(abc.ABCMeta)
class Exchange(object):

    def __init__(self, conf):
        super(Exchange, self).__init__()
        self.conf = conf

    @abc.abstractmethod
    def get_balances(self):
        return NotImplemented

    @abc.abstractmethod
    def get_rate(self):
        return NotImplemented

    @abc.abstractmethod
    def get_candlesticks(self, from_, to_, period, start, end):
        return NotImplemented

    @abc.abstractmethod
    def get_orders(self):
        return NotImplemented

    @abc.abstractmethod
    def cancel_order(self, order):
        return NotImplemented

    @abc.abstractmethod
    def get_fee(self):
        return NotImplemented

    @abc.abstractmethod
    def buy(self, from_, to_, rate, amount):
        return NotImplemented

    @abc.abstractmethod
    def sell(self, from_, to_, rate, amount):
        return NotImplemented

    def get_worth(self, gold, balances=None):
        balances = balances or self.get_balances()

        if gold == 'USD':
            return (self.get_worth('BTC', balances=balances) *
                    self.get_rate('USD', 'BTC'))

        worth = 0
        for currency, amount in balances.items():
            if currency == gold:
                worth += amount
            else:
                converted_amount = amount * self.get_rate(gold, currency)
                worth += converted_amount
        return worth

    def _get_rates(self, type_, gold, other, period, start, end):
        while True:
            res = {
                currency: [
                    candle[type_]
                    for candle in self.get_candlesticks(
                        gold, currency, period, start, end)
                ]
                for currency in other
                if currency != gold
            }
            # sometimes candlesticks get back with zero rates, repeat until
            # succeed
            if all([v != 0.0 for v in res.values()]):
                break
            time.sleep(10)

        for k, v in res.items():
            num_of_rates = len(v)
            break
        res[gold] = [1] * num_of_rates
        return res

    def get_closing_rates(self, gold, other, period, start, end):
        return self._get_rates('close', gold, other, period, start, end)

    def get_opening_rates(self, gold, other, period, start, end):
        return self._get_rates('open', gold, other, period, start, end)


_EXCHANGE_MANAGER = None


def _get_exchange_manager(conf):
    global _EXCHANGE_MANAGER
    if _EXCHANGE_MANAGER is None:
        _EXCHANGE_MANAGER = EnabledExtensionManager(
            'ct.exchanges',
            lambda ext: ext.name in conf)
    return _EXCHANGE_MANAGER


def get_active_exchange_names(conf):
    mgr = EnabledExtensionManager(
        'ct.exchanges',
        lambda ext: ext.name in conf)
    return [ext.name for ext in mgr.extensions]


def get_active_exchanges(conf):
    for ext in _get_exchange_manager(conf).extensions:
        if ext.obj is None and ext.name in conf:
            ext.obj = ext.plugin(conf)
    return [
        ext.obj
        for ext in _get_exchange_manager(conf).extensions
        if ext.obj is not None
    ]


def get_exchange_by_name(conf, name):
    get_active_exchanges(conf)  # load all plugins if not already
    mgr = _get_exchange_manager(conf)
    for ext in mgr.extensions:
        if ext.name == name:
            return ext.obj


def get_global_balance(conf):
    exchanges = get_active_exchanges(conf)
    balance_total = collections.defaultdict(float)
    for ex in exchanges:
        balances = ex.get_balances()
        for currency, amount in balances.items():
            balance_total[currency] += amount
    return balance_total
