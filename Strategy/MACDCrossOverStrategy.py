class MACDCrossOverStrategy:
    """Implementation of the MACD Crossover Strategy.

    In MACD Crossover strategy, a buy signal is triggered when the
    MACD line crosses above the signal line, indicating an
    uptrend (positive momentum). Conversely, a sell signal is triggered
    when the MACD line crosses below the signal line,
    indicating a downtrend (negative momentum). The MACD line is
    calculated by subtracting the slow MA from fast MA, where
    a period of 12 and 26 are commonly used, respectively.
    The signal line is the EMA of the MACD line, and normally has a
    period of 9.

    Args:
        stockframe (StockFrame): The StockFrame object of
            historical candlestick data.
        portfolio (Portfolio): The Portfolio object.
        indicator_client (Indicator): The Indicator object
            of current indicators.
        existing_orders (dict[bool]): A dict of existing orders.
            True if there is a pending order, otherwise False.
        fast_length (int): The period of fast MA for MACD line.
            Default: 12.
        slow_length (int): The period of slow MA for MACD line.
            Default: 26.
        signal_length (int): The period of signal line.
            Default: 9.
    """
    def __init__(self,
                 stockframe,
                 portfolio,
                 indicator_client,
                 existing_orders,
                 fast_length=12,
                 slow_length=26,
                 signal_length=9,
                 adjust=False):

        self.stockframe = stockframe
        self.portfolio = portfolio
        self.indicator_client = indicator_client
        self.existing_orders = existing_orders

        self.fast_length = fast_length
        self.slow_length = slow_length
        self.signal_length = signal_length
        self.adjust = adjust

    def calculate_buy_sell_signals(self):
        """Calculate buy and sell signals based on MACD Crossover Strategy.

        Returns:
            buy_sell_signals (dict[dict]): A dict of buy and sell
                signals with key 'buys' and 'sells'. Each key
                contains a dict of codes with triggered signals
        """
        holdings = self.portfolio.holdings

        buy_sell_signals = {'buys': {}, 'sells': {}}

        code_list = self.stockframe.frame.index.get_level_values(0).unique()

        if 'macd' not in self.stockframe.frame.columns:
            self.indicator_client.macd(
                fast_length=self.fast_length,
                slow_length=self.slow_length,
                signal_length=self.signal_length,
                adjust=self.adjust,
            )

        last_rows = self.stockframe.code_groups.tail(1)

        print(last_rows)

        for code in code_list:

            if self.existing_orders[code] is False:
                if holdings[code] == 0:
                    if last_rows.loc[code, 'macd'].iloc[0] > last_rows.loc[
                            code, 'signal'].iloc[0]:
                        buy_sell_signals['buys'][code] = last_rows.loc[
                            code].tail(1).reset_index().loc[0].to_dict()

                elif holdings[code] != 0:
                    if last_rows.loc[code, 'macd'].iloc[0] < last_rows.loc[
                            code, 'signal'].iloc[0]:
                        buy_sell_signals['sells'][code] = last_rows.loc[
                            code].tail(1).reset_index().loc[0].to_dict()

        return buy_sell_signals
