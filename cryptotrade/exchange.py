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


class Exchange(object):
    __metaclass__ = abc.ABCMeta

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
    def cancel_all_orders(self):
        return NotImplemented

    def get_worth(self, gold, balances=None):
        balances = balances or self.get_balances()

        if gold == 'USD':
            return self.get_worth('BTC') * self.get_rate('USD', 'BTC')

        worth = 0
        for currency, amount in balances.items():
            if currency == gold:
                worth += amount
            else:
                converted_amount = amount * self.get_rate(gold, currency)
                worth += converted_amount
        return worth
