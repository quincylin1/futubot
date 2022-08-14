import pprint
import signal
import time
from datetime import datetime, timedelta

import pandas as pd
from futu import KLType, SecurityFirm, TrdMarket, TrdSide

from .accounts import Accounts
from .portfolio import Portfolio
from .stockframe import StockFrame


class Robot(Accounts):
    def __init__(self,
                 host='127.0.0.1',
                 port=11111,
                 filter_trdmarket=TrdMarket.HK,
                 security_firm=SecurityFirm.FUTUSECURITIES,
                 paper_trading=False,
                 password='******',
                 order_type='limit'):
        super(Robot, self).__init__(host, port, filter_trdmarket,
                                    security_firm, paper_trading, password)
        self.trades = {}
        self.historical_quotes = {}
        self.stockframe = None
        self.portfolio = None
        self.order_type = order_type

        signal.signal(signal.SIGINT, self._keyboard_interrupt_handler)

    @staticmethod
    def is_regular_trading_time():

        morning_market_start_time = datetime.utcnow().replace(
            hour=1, minute=30, second=00).timestamp()
        morning_market_end_time = datetime.utcnow().replace(
            hour=4, minute=00, second=00).timestamp()

        lunch_break_start_time = datetime.utcnow().replace(
            hour=4, minute=00, second=00).timestamp()
        lunch_break_end_time = datetime.utcnow().replace(
            hour=5, minute=1, second=30).timestamp()

        afternoon_market_start_time = datetime.utcnow().replace(
            hour=5, minute=1, second=30).timestamp()
        afternoon_market_end_time = datetime.utcnow().replace(
            hour=8, minute=00, second=00).timestamp()

        current_time = datetime.utcnow().timestamp()

        print(
            'current_time',
            datetime.fromtimestamp(current_time).strftime('%Y-%m-%d %H:%M:%S'))

        if morning_market_start_time <= current_time <= \
            morning_market_end_time or afternoon_market_start_time \
                < current_time <= afternoon_market_end_time:
            return True

        elif lunch_break_start_time < current_time <= lunch_break_end_time:
            time_diff = datetime.fromtimestamp(
                lunch_break_end_time) - datetime.fromtimestamp(current_time)
            time_diff = int(time_diff.total_seconds())
            print('Trading is temporarily pasued during lunch break.')
            print('Sleep time', time_diff)
            time.sleep(time_diff)

            return True

        return False

    def create_portfolio(self, stocks_of_interest=None):

        self.portfolio = Portfolio(filter_trdmarket=self.filter_trdmarket,
                                   host=self.host,
                                   port=self.port,
                                   security_firm=self.security_firm,
                                   paper_trading=self.paper_trading)

        existing_positions = self.get_positions()

        if stocks_of_interest is None and not existing_positions:
            raise ValueError('Cannot have an empty portfolio.'
                             'Please indicate your stocks of interest!')

        else:
            if existing_positions:

                for code in list(existing_positions.keys()):

                    self.portfolio.add_position(
                        code=code,
                        stock_name=existing_positions[code]['stock_name'],
                        quantity=existing_positions[code]['qty'],
                    )

            if stocks_of_interest is not None:

                market_state = self.get_market_state(
                    code_list=stocks_of_interest)

                for code in stocks_of_interest:
                    if code not in existing_positions:
                        stock_name = market_state[code]['stock_name']
                        self.portfolio.add_position(
                            code=code,
                            stock_name=stock_name,
                            quantity=0,
                        )

            return self.portfolio

    def create_stockframe(self, data):

        self.stockframe = StockFrame(data=data)

        return self.stockframe

    def get_historical_quotes(self,
                              start_date,
                              end_date,
                              codes=None,
                              ktype=KLType.K_1M,
                              max_count=1000):

        historical_prices = []

        if codes is None:
            codes = self.portfolio.positions.keys()

        for code in codes:
            historical_quotes = self.get_historical_candles(
                code=code,
                start=start_date,
                end=end_date,
                ktype=ktype,
                max_count=max_count)

            for _, candle in historical_quotes.iterrows():
                candle = candle.to_dict()
                historical_price = {}
                historical_price['time_key'] = candle['time_key']
                historical_price['code'] = candle['code']
                historical_price['open'] = candle['open']
                historical_price['close'] = candle['close']
                historical_price['high'] = candle['high']
                historical_price['low'] = candle['low']
                historical_price['volume'] = candle['volume']
                historical_prices.append(historical_price)

        return historical_prices

    def get_latest_bar(self,
                       codes=None,
                       ktype=KLType.K_1M,
                       max_count=1000,
                       demo=False,
                       **kwargs):

        if not isinstance(demo, bool):
            raise TypeError(f'Only bool type is supported for demo, '
                            f'but got {type(demo)}')

        latest_prices = []

        if codes is None:
            codes = self.portfolio.positions.keys()

        if demo is True:
            start_date = kwargs['start_date']
            end_date = kwargs['end_date']

        else:
            if ktype == KLType.K_QUARTER:
                lookback = timedelta(days=90)
            elif ktype == KLType.K_MON:
                lookback = timedelta(days=30)
            elif ktype == KLType.K_DAY:
                lookback = timedelta(days=1)
            else:
                lookback = timedelta(minutes=60)

            end_date = datetime.today()
            start_date = end_date - lookback
            end_date = end_date.strftime('%Y-%m-%d %H:%M:%S')
            start_date = start_date.strftime('%Y-%m-%d %H:%M:%S')

        for code in codes:
            historical_quotes = self.get_historical_candles(
                code=code,
                start=start_date,
                end=end_date,
                ktype=ktype,
                max_count=max_count)

            latest_candle = historical_quotes.iloc[-1]
            latest_candle = latest_candle.to_dict()
            latest_price = {}
            latest_price['time_key'] = latest_candle['time_key']
            latest_price['code'] = latest_candle['code']
            latest_price['open'] = latest_candle['open']
            latest_price['close'] = latest_candle['close']
            latest_price['high'] = latest_candle['high']
            latest_price['low'] = latest_candle['low']
            latest_price['volume'] = latest_candle['volume']
            latest_prices.append(latest_price)

        return latest_prices

    def execute_signals(self, buy_sell_signals):

        if not isinstance(buy_sell_signals, dict):
            raise TypeError(
                f'Only dict type is supported for buy_sell_signals, '
                f'but got {type(buy_sell_signals)}')

        pprint.pprint(buy_sell_signals)

        buy_signals = buy_sell_signals['buys']
        sell_signals = buy_sell_signals['sells']
        order_infos = {}

        if buy_signals:
            codes = list(buy_signals.keys())
            lot_sizes = self.get_lot_size(code_list=codes)

            for code in codes:
                price = buy_signals[code]['close']
                # Only buy one lot
                qty = lot_sizes[code]

                # Check if exceed max buy power:
                max_power = self.get_max_power(code=code,
                                               price=price,
                                               order_type=self.order_type)
                if qty < max_power['max_cash_buy']:
                    order_info = self.place_order(price=price,
                                                  qty=qty,
                                                  code=code,
                                                  order_type=self.order_type,
                                                  trd_side=TrdSide.BUY)
                    order_infos[code] = order_info

        if sell_signals:
            codes = list(sell_signals.keys())

            for code in codes:
                if code not in order_infos:
                    order_infos[code] = {}

                price = sell_signals[code]['close']
                # Sell all current holdings
                qty = self.portfolio.holdings[code]

                # Check if exceed max sell power:
                max_power = self.get_max_power(code=code,
                                               price=price,
                                               order_type=self.order_type)
                if qty <= max_power['max_position_sell']:
                    order_info = self.place_order(
                        price=price,
                        qty=qty,
                        code=code,
                        order_type=self.order_type,
                        trd_side=TrdSide.SELL,
                    )
                    order_infos[code] = order_info

        return order_infos

    def wait_till_next_bar(self, last_bar_timestamp):

        last_bar_timestamp = pd.to_datetime(last_bar_timestamp)

        last_bar_time = last_bar_timestamp.to_pydatetime()[0]
        next_bar_time = last_bar_time + timedelta(seconds=60)
        curr_bar_time = datetime.now()

        next_bar_timestamp = int(next_bar_time.timestamp())
        curr_bar_timestamp = int(curr_bar_time.timestamp())

        time_till_next_bar = next_bar_timestamp - curr_bar_timestamp

        if time_till_next_bar < 0:
            time_till_next_bar = 0

        print('')
        print('=' * 80)
        print('Pausing for the next bar')
        print('-' * 80)
        print('Curr Time: {time_curr}'.format(
            time_curr=curr_bar_time.strftime('%Y-%m-%d %H:%M:%S')))
        print('Next Time: {time_next}'.format(
            time_next=next_bar_time.strftime('%Y-%m-%d %H:%M:%S')))
        print('Time till next bar: {seconds} s'.format(
            seconds=time_till_next_bar))
        print('-' * 80)
        print('')

        time.sleep(time_till_next_bar)

    def _keyboard_interrupt_handler(self, signum, frame):
        print('Ctrl-C is pressed, cancelling all pending orders now...')
        self.cancel_all_orders()
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        print('Press Ctrl-C again to exit.')
        time.sleep(99999999)
