import pprint
import signal
import time
from datetime import datetime, timedelta

import pandas as pd
from futu import KLType, TrdSide

from .portfolio import Portfolio
from .stockframe import StockFrame


class Robot:
    """Implementation of the main logic of FutuBot.

    Args:
        accounts (Accounts): The Accounts object.
        order_type (str): The type of order. Default: limit.
    """
    def __init__(self, accounts, order_type='limit'):

        self.accounts = accounts
        self.trades = {}
        self.historical_quotes = {}
        self.stockframe = None
        self.portfolio = None
        self.order_type = order_type

        signal.signal(signal.SIGINT, self._keyboard_interrupt_handler)

    @staticmethod
    def is_regular_trading_time():
        """Check whether current time is within regular trading time.

        For TrdMarket.HK, the regular trading time of HKEX is from
        HKT 9:30:00 to 16:00:00. Market is temporarily closed from
        12:00:00 to 13:00:00 for lunch break, during which FutuBot is
        put on sleep.

        Returns:
            bool: True if current time is in regular trading time,
                otherwise False (put on sleep if current time is
                within lunch break).

        Examples:
        >>> current_time = HKT 10:00:00
        >>> Robot.is_regular_trading_time()
        True
        >>> current_time = HKT 12:30:00
        >>> Robot.is_regular_trading_time()
        Trading is temporarily pasued during lunch break.
        Sleep time: 1800 s
        >>> current_time = HKT 17:00:00
        >>> Robot.is_regular_trading_time()
        False
        """
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
            print(f'Sleep time: {time_diff} s')
            time.sleep(time_diff)

            return True

        return False

    def create_portfolio(self, stocks_of_interest=None):
        """Create a new portfolio object.

        The function instantiates a Portfolio object and adds instruments
        (stocks) to the portfolio. It first looks for existing stocks from
        the given trading account and adds to the portfolio, and then adds
        the extra stocks specified by the stocks_of_interest that are not
        included in the trading account to the portfolio. If the trading
        account does not hold any existing stock and stocks_of_interest is
        None, a ValueError is raised in order to avoid an empty portfolio.

        Args:
            stocks_of_interest (list[str]): A list of the codes of stocks
                of interest.

        Returns:
            (Portfolio): A futubot.portfolio.Portfolio object containing
                stocks in trading account as well as stocks of interest.

        Examples:
        >>> portfolio = trading_robot.create_portfolio(
            stocks_of_interest=cfg_dict['stocks_of_interest'])
        >>> portfolio
        <futubot.portfolio.Portfolio object at 0x7fc160f86d60>
        >>> portfolio.positions
        {'HK.00700': {'code': 'HK.00700', 'qty': 100.0,
            'stock_name': 'TENCENT'},
         'HK.09988': {'code': 'HK.09988', 'qty': 0,
             'stock_name': 'BABA-SW'}}
        """
        self.portfolio = Portfolio(accounts=self.accounts)

        existing_positions = self.accounts.get_positions()

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
                market_state = self.accounts.get_market_state(
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
        """Create a new stockframe object.

        The function instantiates a new StockFrame object and adds
        the historical candlestick data of all the stocks in the portfolio
        object to it. The StockFrame object contains a frame attribute, which
        is a MultiIndex pd.DataFrame with index (code, time_key) and columns
        open, close, high, low, volume.

        Args:
            data (list[dict]): Candlestick data in portfolio to be
                added to the StockFrame.

        Returns:
            (StockFrame): A futubot.stockframe.StockFrame object containing
                candlestick data for stocks in portfolio.

        Examples:
        >>> stockframe = trading_robot.create_stockframe(data
            =historical_quotes)
        <futubot.stockframe.StockFrame object at 0x7f9979305e80>
        """
        self.stockframe = StockFrame(data=data)

        return self.stockframe

    def get_historical_quotes(self,
                              start_date,
                              end_date,
                              code_list=None,
                              ktype=KLType.K_1M,
                              max_count=1000):
        """Get historical quotes of all stocks in portfolio.

        This function gets the historical candlestick data of
        all the stocks present in the portfolio as a pandas DataFrame.
        The candlestick data are between start_date and end_date with
        ktype candlestick. The dataframe is converted into a list of dicts
        of historical prices.

        Args:
            start_date: The start time in format yyyy-MM-dd HH:mm:ss.
            end_date: The end time in format yyyy-MM-dd HH:mm:ss.
            code_list: The list of code for which historical quotes
                are queried. Default: None, meaning all stocks in
                portfolio are queried.
            ktype (KLType): The type of candlestick. Default: K_1M.
            max_count (int): The maximum number of candlesticks
                returned. Default: 1000.

        Returns:
            historical_prices (list[dict]): A list of dicts of
                historical quotes. The dict contains the following keys
                    time_key (str): Candlestick time in format
                        yyyy-MM-dd HH:mm:ss.
                    code (str): The code of security.
                    open (float): Open price.
                    close (float): Close price.
                    high (float): High price.
                    low (float): Low price.
                    volume (int): Trading volume
        """
        historical_prices = []

        if code_list is None:
            code_list = list(self.portfolio.positions.keys())

        for code in code_list:
            historical_quotes = self.accounts.get_historical_candles(
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
                       code_list=None,
                       ktype=KLType.K_1M,
                       max_count=1000,
                       demo=False,
                       **kwargs):
        """Get the lateest bars of all stocks in portfolio.

        This function gets the last candlestick data of
        all the stocks present in the portfolio as a pandas DataFrame.
        For demo mode, both start_date and end_date must be specified.
        For live mode, the end_time corresponds to the current datetime,
        and the start_time is behind the end_time by a lookback period,
        whose length depends on the type of candlestick specified by ktype.

        Args:
            code_list: The list of code for which historical quotes
                are queried. Default: None, meaning all stocks in
                portfolio are queried.
            ktype (KLType): The type of candlestick. Default: K_1M.
            max_count (int): The maximum number of candlesticks
                returned. Default: 1000.
            demo (bool): Whether to run in demo mode or not. Default:
                False.
            kwargs: Optional keyword arguments. If in demo mode, start_date
                and end_date in format yyyy-MM-dd HH:mm:ss must be provided.

        Returns:
            latest_prices (list[dict]): A list of dicts of
                latest quotes. The dict contains the following keys
                    time_key (str): Candlestick time in format
                        yyyy-MM-dd HH:mm:ss.
                    code (str): The code of security.
                    open (float): Open price.
                    close (float): Close price.
                    high (float): High price.
                    low (float): Low price.
                    volume (int): Trading volume
        """
        if not isinstance(demo, bool):
            raise TypeError(f'Only bool type is supported for demo, '
                            f'but got {type(demo)}')

        latest_prices = []

        if code_list is None:
            code_list = list(self.portfolio.positions.keys())

        if demo is True:
            if 'start_date' not in kwargs or 'end_date' not in kwargs:
                raise KeyError(
                    'kwargs must contain key start_date and end_date')
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

        for code in code_list:
            historical_quotes = self.accounts.get_historical_candles(
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
        """Execute the buy and sell signals.

        This function places buy and sell orders based on
        buy_sell_signals. When a buy signal is present for a given code,
        the function first checks if the current trading account
        exceeds the maximum cash buying power, and then buys one lot of
        stock if there is enough cash buying power. Conversely, when a
        sell signal is present, the function first checks if the account
        exceeds the maximum position selling power, and then sell all
        the current holding if there is sufficient selling power.

        Args:
            buy_sell_signals (dict[dict]): A dict of buy and sell
                signals. The outer dict contains keys 'buys' and 'sells',
                whose values correspond to the codes for which buy/sell
                signals are triggered.

        Returns:
            order_infos (dict[dict]): A dict of order infos. The outer dict
                with keys equal to the codes for which the buy/sell signals
                are present. The inner dict contains keys: trd_side,
                order_type, order_status, order_id, code, stock_name, qty,
                price, create_time, updated_time.
        """
        if not isinstance(buy_sell_signals, dict):
            raise TypeError(
                f'Only dict type is supported for buy_sell_signals, '
                f'but got {type(buy_sell_signals)}')

        pprint.pprint(buy_sell_signals)

        order_infos = {}

        buy_signals = buy_sell_signals['buys']
        sell_signals = buy_sell_signals['sells']

        if buy_signals:
            code_list = list(buy_signals.keys())
            lot_sizes = self.accounts.get_lot_size(code_list=code_list)

            for code in code_list:
                price = buy_signals[code]['close']
                # Only buy one lot
                qty = lot_sizes[code]

                # Check if exceed max buy power:
                max_power = self.accounts.get_max_power(
                    code=code, price=price, order_type=self.order_type)
                if qty < max_power['max_cash_buy']:
                    order_info = self.accounts.place_order(
                        price=price,
                        qty=qty,
                        code=code,
                        order_type=self.order_type,
                        trd_side=TrdSide.BUY)
                    order_infos[code] = order_info

        if sell_signals:
            code_list = list(sell_signals.keys())

            for code in code_list:
                if code not in order_infos:
                    order_infos[code] = {}

                price = sell_signals[code]['close']
                # Sell all current holdings
                qty = self.portfolio.holdings[code]

                # Check if exceed max sell power:
                max_power = self.accounts.get_max_power(
                    code=code, price=price, order_type=self.order_type)
                if qty <= max_power['max_position_sell']:
                    order_info = self.accounts.place_order(
                        price=price,
                        qty=qty,
                        code=code,
                        order_type=self.order_type,
                        trd_side=TrdSide.SELL,
                    )
                    order_infos[code] = order_info

        return order_infos

    def wait_till_next_bar(self, last_bar_timestamp):
        """Wait until the next bar data.

        This function calculates the time difference between
        the current time and the next bar time, which is 60
        seconds after the last bar time, and then puts the
        robot on sleep until the next bar time is reached.

        Args:
            last_bar_timestamp (str): The timestamp of the
                last bar data in format yyyy-MM-dd HH:mm:ss.
        """
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
        """Cancel all pending orders when keyboard is interrupted.

        This function calls the cancel_all_orders() method when Ctrl-C is
        pressed, and puts the robot on sleep forever until Ctrl-C is pressed
        again, after which the program is exited.
        """
        print('Ctrl-C is pressed, cancelling all pending orders now...')

        self.accounts.cancel_all_orders()
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        print('Press Ctrl-C again to exit.')
        # Put the program on sleep forever.
        time.sleep(99999999)
