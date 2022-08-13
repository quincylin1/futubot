class BollingerBandsStrategy:
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

        holdings = self.portfolio.holdings

        buy_sell_signals = {'buys': {}, 'sells': {}}

        codes = self.stockframe.frame.index.get_level_values(0).unique()

        if 'upper_band' not in self.stockframe.frame.columns or \
                'lower_band' not in self.stockframe.frame.columns:
            self.indicator_client.bollinger_bands(period=self.period,
                                                  indicator='bollinger_bands')

        last_rows = self.stockframe.code_groups.tail(1)

        print(last_rows)

        for code in codes:
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
