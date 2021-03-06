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

import collections

from cached_property import cached_property_with_ttl
from poloniex import poloniex as plx

from cryptotrade import exchange


class MissingPoloniexSection(Exception):
    message = 'Missing [poloniex] section in the configuration file.'


class MissingPoloniexApiKey(Exception):
    message = 'Missing API key or secret in the configuration file.'


class Poloniex(exchange.Exchange):

    CANDLESTICKS = (300, 900, 1800, 7200, 14400, 86400)

    def __init__(self, conf):
        super(Poloniex, self).__init__(conf)
        poloniex_conf = conf.get('poloniex')
        if not poloniex_conf:
            raise MissingPoloniexSection
        for key in ('api_key', 'api_secret'):
            if key not in poloniex_conf:
                raise MissingPoloniexApiKey
        self.api_key = poloniex_conf['api_key'].encode('utf-8')
        self.api_secret = poloniex_conf['api_secret'].encode('utf-8')
        self.private = plx.Poloniex(
            apikey=self.api_key, secret=self.api_secret)

    def get_balances(self):
        balances = self.private.returnBalances()
        res = collections.defaultdict(float)
        res.update({
            # filter out currencies that we don't own
            k: v for k, v in balances.items() if v
        })
        return res

    def get_fee(self):
        return float(self.private.returnFeeInfo()['takerFee'])

    @cached_property_with_ttl(ttl=60)
    def _ticker(self):
        return self.private.returnTicker()

    def get_rate(self, from_, to_):
        if from_ == to_:
            return 1
        ticker = self._ticker
        from_ = from_ if from_ != 'USD' else 'USDT'
        pair = '%s_%s' % (from_, to_)
        return ticker[pair]['highestBid']

    def get_candlesticks(self, from_, to_, period, start, end):
        assert from_ == 'BTC', 'poloneix has pairs for BTC only'
        return self.private.returnChartData(
            '%s_%s' % (from_, to_), period, start=start, end=end)

    def get_orders(self):
        orders = self.private.returnOpenOrders()
        return {
            k: v
            for k, v in orders.items()
            if v
        }

    def cancel_order(self, order):
        self.private.cancelOrder(order['orderNumber'])

    def buy(self, from_, to_, rate, amount):
        # revisit: switch back to .sell api when poloniex library is released
        # with: https://github.com/Aula13/poloniex/pull/1
        currencyPair = '%s_%s' % (from_, to_)
        return self.private._private(
            'buy', currencyPair=currencyPair, rate=rate, amount=amount)

    def sell(self, from_, to_, rate, amount):
        # revisit: switch back to .sell api when poloniex library is released
        # with: https://github.com/Aula13/poloniex/pull/1
        currencyPair = '%s_%s' % (from_, to_)
        return self.private._private(
            'sell', currencyPair=currencyPair, rate=rate, amount=amount)
