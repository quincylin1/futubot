class MAStrategy:
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
                self.indicator_client.ema(periods=self.short_period)
            else:
                self.indicator_client.sma(period=self.short_period)

        if ma_long not in self.stockframe.frame.columns:
            if self.is_ema:
                self.indicator_client.ema(periods=self.long_period)
            else:
                self.indicator_client.sma(period=self.long_period)

        last_rows = self.stockframe.code_groups.tail(1)

        print(last_rows)

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
