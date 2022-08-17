class RSIStrategy:
    """Implementation of the RSI Strategy.

    In RSI strategy, a buy signal is triggered when the RSI
    falls below the oversold level, and a sell signal is
    triggered when the RSI rises above the overbought signal.
    J. W. Wilder Jr. suggested the oversold and overbought
    signal to be 30 and 70, respectively, but other values
    (e.g. 20/80) are also used.

    Args:
        stockframe (StockFrame): The StockFrame object of
            historical candlestick data.
        portfolio (Portfolio): The Portfolio object.
        indicator_client (Indicator): The Indicator object
            of current indicators.
        existing_orders (dict[bool]): A dict of existing orders.
            True if there is a pending order, otherwise False.
        oversold_signal (int): The oversold signal. Default: 30.
        overbought_signal (int): The overbought signal. Default: 70.
        period (int): The period for RSI calculations. Default: 14.
    """
    def __init__(self,
                 stockframe,
                 portfolio,
                 indicator_client,
                 existing_orders,
                 oversold_signal=30,
                 overbought_signal=70,
                 period=14):

        self.stockframe = stockframe
        self.portfolio = portfolio
        self.existing_orders = existing_orders
        self.indicator_client = indicator_client

        self.oversold_signal = oversold_signal
        self.overbought_signal = overbought_signal
        self.period = period

    def calculate_buy_sell_signals(self):
        """Calculate buy and sell signals based on RSI Strategy.

        Returns:
            buy_sell_signals (dict[dict]): A dict of buy and sell
                signals with key 'buys' and 'sells'. Each key
                contains a dict of codes with triggered signals
        """
        holdings = self.portfolio.holdings

        buy_sell_signals = {'buys': {}, 'sells': {}}

        code_list = self.stockframe.frame.index.get_level_values(0).unique()

        indicator = 'rsi_' + str(self.period)

        if indicator not in self.stockframe.frame.columns:
            self.indicator_client.rsi(period=self.period)

        last_rows = self.stockframe.code_groups.tail(1)

        print('lastest bars', last_rows)

        for code in code_list:
            if self.existing_orders[code] is False:
                if holdings[code] == 0:
                    if last_rows.loc[code,
                                     indicator].iloc[0] < self.oversold_signal:
                        buy_sell_signals['buys'][code] = last_rows.loc[
                            code].tail(1).reset_index().loc[0].to_dict()

                elif holdings[code] != 0:
                    if last_rows.loc[
                            code, indicator].iloc[0] > self.overbought_signal:
                        buy_sell_signals['sells'][code] = last_rows.loc[
                            code].tail(1).reset_index().loc[0].to_dict()

        return buy_sell_signals
