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

from cliff.command import Command
from cryptotrade import exchange
from cryptotrade import trader


class BaseTradeCommand(Command):
    def get_parser(self, prog_name):
        parser = super(BaseTradeCommand, self).get_parser(prog_name)
        parser.add_argument(
            '-b',
            dest='balances',
            action='append',
            metavar='CURRENCY=AMOUNT',
            help='currency balances')
        parser.add_argument(
            '-e',
            dest='exchange',
            required=True,
            choices=exchange.get_active_exchange_names(self.app.cfg),
            help='exchange to trade on')
        parser.add_argument(
            '-s',
            dest='strategy',
            choices=trader.list_strategy_names(),
            help='trading strategy')
        parser.add_argument(
            '-t',
            dest='targets',
            action='append',
            metavar='CURRENCY',
            help='portfolio currencies')
        parser.add_argument(
            '-w',
            dest='weights',
            type=float,
            action='append',
            metavar='WEIGHT',
            help='currency weights (in order of -t)')
        return parser

    def get_balances(self, args):
        if args.balances:
            balances = collections.defaultdict(float)
            for balance in args.balances:
                currency, amount = balance.split('=')
                amount = float(amount)
                balances[currency] = amount
        else:
            balances = exchange.get_global_balance(self.app.cfg)
        return balances
