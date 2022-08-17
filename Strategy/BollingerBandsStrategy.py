class BollingerBandsStrategy:
    """Implementation of the Bollinger Bands Strategy.

    The Bollinger Bands strategy relies on mean reversion, which
    assumes that the price eventually reverts back to the mean price
    if it deviates substantially from the mean.

    A buy signal is triggered when the price breaks below the lower
    Bollinger Band, where the price is assumed to rebound.
    Conversely, a sell signal is triggered when the price breaks above
    the upper Bollinger Band, where the price is due for a pull-back.
    A period of 20 is commonly used for Bollinger Bands calculations.

    Args:
        stockframe (StockFrame): The StockFrame object of
            historical candlestick data.
        portfolio (Portfolio): The Portfolio object.
        indicator_client (Indicator): The Indicator object
            of current indicators.
        existing_orders (dict[bool]): A dict of existing orders.
            True if there is a pending order, otherwise False.
        period (int): The period for Bollinger Bands calculations.
            Default: 20.
    """
    def __init__(self,
                 stockframe,
                 portfolio,
                 indicator_client,
                 existing_orders,
                 period=20):

        self.stockframe = stockframe
        self.portfolio = portfolio
        self.existing_orders = existing_orders
        self.indicator_client = indicator_client

        self.period = period

    def calculate_buy_sell_signals(self):
        """Calculate buy and sell signals based on Bollinger Bands Strategy.

        Returns:
            buy_sell_signals (dict[dict]): A dict of buy and sell
                signals with key 'buys' and 'sells'. Each key
                contains a dict of codes with triggered signals
        """
        holdings = self.portfolio.holdings

        buy_sell_signals = {'buys': {}, 'sells': {}}

        code_list = self.stockframe.frame.index.get_level_values(0).unique()

        if 'upper_band' not in self.stockframe.frame.columns or \
                'lower_band' not in self.stockframe.frame.columns:
            self.indicator_client.bollinger_bands(period=self.period,
                                                  indicator='bollinger_bands')

        last_rows = self.stockframe.code_groups.tail(1)

        print('lastest bars', last_rows)

        for code in code_list:
            if self.existing_orders[code] is False:
                if holdings[code] == 0:
                    if last_rows.loc[code, 'close'].iloc[0] < last_rows.loc[
                            code, 'lower_band'].iloc[0]:
                        buy_sell_signals['buys'][code] = last_rows.loc[
                            code].tail(1).reset_index().loc[0].to_dict()

                elif holdings[code] != 0:
                    if last_rows.loc[code, 'close'].iloc[0] > last_rows.loc[
                            code, 'upper_band'].iloc[0]:
                        buy_sell_signals['sells'][code] = last_rows.loc[
                            code].tail(1).reset_index().loc[0].to_dict()

        return buy_sell_signals
