class MACDCrossOverStrategy:
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
