class RSIStrategy:
    def __init__(self,
                 stockframe,
                 portfolio,
                 indicator_client,
                 existing_orders,
                 oversell_signal=30,
                 overbuy_signal=70,
                 period=14):

        self.stockframe = stockframe
        self.portfolio = portfolio
        self.existing_orders = existing_orders
        self.indicator_client = indicator_client

        self.oversell_signal = oversell_signal
        self.overbuy_signal = overbuy_signal
        self.period = period

    def calculate_buy_sell_signals(self):

        holdings = self.portfolio.holdings

        buy_sell_signals = {'buys': {}, 'sells': {}}

        code_list = self.stockframe.frame.index.get_level_values(0).unique()

        indicator = 'rsi_' + str(self.period)

        if indicator not in self.stockframe.frame.columns:
            self.indicator_client.rsi(period=self.period)

        last_rows = self.stockframe.code_groups.tail(1)

        print(last_rows)

        for code in code_list:
            if self.existing_orders[code] is False:
                if holdings[code] == 0:
                    if last_rows.loc[code,
                                     indicator].iloc[0] < self.oversell_signal:
                        buy_sell_signals['buys'][code] = last_rows.loc[
                            code].tail(1).reset_index().loc[0].to_dict()

                elif holdings[code] != 0:
                    if last_rows.loc[code,
                                     indicator].iloc[0] > self.overbuy_signal:
                        buy_sell_signals['sells'][code] = last_rows.loc[
                            code].tail(1).reset_index().loc[0].to_dict()

        return buy_sell_signals
