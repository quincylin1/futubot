class MAStrategy:
    """Implementation of the Moving Average (MA) Strategy.

    In MA strategy, a buy signal is triggered when the short-term
    MA crosses above the long-term MA (Golden Cross), indicating an
    uptrend (positive momentum). Conversely, a sell signal is triggered
    when the short-term MA crosses below the long-term MA (Death Cross),
    indicating a downtrend (negative momentum). A period of 20 and 50
    are commonly used for short and long-term MA, respectively.

    Args:
        stockframe (StockFrame): The StockFrame object of
            historical candlestick data.
        portfolio (Portfolio): The Portfolio object.
        indicator_client (Indicator): The Indicator object
            of current indicators.
        existing_orders (dict[bool]): A dict of existing orders.
            True if there is a pending order, otherwise False.
        short_period (int): The period of short-term MA. Default: 20.
        long_period (int): The period of long-term MA. Default: 50.
        is_ema (bool): Whether to use EMA for MA calculations.
            Default: False.
    """
    def __init__(self,
                 stockframe,
                 portfolio,
                 indicator_client,
                 existing_orders,
                 short_period=20,
                 long_period=50,
                 is_ema=False):

        self.stockframe = stockframe
        self.portfolio = portfolio
        self.indicator_client = indicator_client
        self.existing_orders = existing_orders

        self.short_period = short_period
        self.long_period = long_period
        self.is_ema = is_ema

    def calculate_buy_sell_signals(self):
        """Calculate buy and sell signals based on MA Strategy.

        Returns:
            buy_sell_signals (dict[dict]): A dict of buy and sell
                signals with key 'buys' and 'sells'. Each key
                contains a dict of codes with triggered signals
        """
        holdings = self.portfolio.holdings

        buy_sell_signals = {'buys': {}, 'sells': {}}

        code_list = self.stockframe.frame.index.get_level_values(0).unique()

        if self.is_ema:
            ma_short = 'ema_' + str(self.short_period)
            ma_long = 'ema_' + str(self.long_period)

        else:
            ma_short = 'sma_' + str(self.short_period)
            ma_long = 'sma_' + str(self.long_period)

        if ma_short not in self.stockframe.frame.columns:
            if self.is_ema:
                self.indicator_client.ema(period=self.short_period)
            else:
                self.indicator_client.sma(period=self.short_period)

        if ma_long not in self.stockframe.frame.columns:
            if self.is_ema:
                self.indicator_client.ema(period=self.long_period)
            else:
                self.indicator_client.sma(period=self.long_period)

        last_rows = self.stockframe.code_groups.tail(1)

        print('lastest bars', last_rows)

        for code in code_list:
            if self.existing_orders[code] is False:
                if holdings[code] == 0:
                    if last_rows.loc[code,
                                     ma_short][0] > last_rows.loc[code,
                                                                  ma_long][0]:
                        buy_sell_signals['buys'][code] = last_rows.loc[
                            code].tail(1).reset_index().loc[0].to_dict()

                elif holdings[code] != 0:
                    if last_rows.loc[code,
                                     ma_short][0] < last_rows.loc[code,
                                                                  ma_long][0]:
                        buy_sell_signals['sells'][code] = last_rows.loc[
                            code].tail(1).reset_index().loc[0].to_dict()

        return buy_sell_signals
