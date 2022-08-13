from .stockframe import StockFrame


class Indicators:
    def __init__(self, stockframe: StockFrame):
        self.stockframe = stockframe
        self.code_groups = stockframe.code_groups
        self.current_indicators = {}
        self.frame = stockframe.frame
        self.code_list = stockframe.frame.index.get_level_values(0).to_list()

    def change_in_price(self, indicator='change_in_price'):

        self.frame[indicator] = self.code_groups['close'].transform(
            lambda x: x.diff())

    def rsi(self, periods=14, ewma=True):

        if not isinstance(periods, int):
            raise TypeError(f'Only int type is supported for periods, '
                            f'but got {type(periods)}')
        assert periods > 0, (f'periods must be greater than 0, '
                             f'but got {periods}')

        locals_data = locals()
        del locals_data['self']

        indicator = 'rsi_' + str(periods)

        self.current_indicators[indicator] = {}
        self.current_indicators[indicator]['args'] = locals_data
        self.current_indicators[indicator]['func'] = self.rsi

        if 'change_in_price' not in self.frame.columns:
            self.change_in_price()

        self.frame['up'] = self.code_groups['change_in_price'].transform(
            lambda x: x.clip(lower=0))

        self.frame['down'] = self.code_groups['change_in_price'].transform(
            lambda x: -1 * x.clip(upper=0))

        if ewma:
            self.frame['ma_up'] = self.code_groups['up'].transform(
                lambda x: x.ewm(span=periods, adjust=True, min_periods=periods
                                ).mean())

            self.frame['ma_down'] = self.code_groups['down'].transform(
                lambda x: x.ewm(span=periods, adjust=True, min_periods=periods
                                ).mean())
        else:
            self.frame['ma_up'] = self.code_groups['up'].transform(
                lambda x: x.rolling(window=periods, adjust=False).mean())

            self.frame['ma_down'] = self.code_groups['down'].transform(
                lambda x: x.rolling(window=periods, adjust=False).mean())

        relative_strength = self.frame['ma_up'] / self.frame['ma_down']
        relative_strength_index = 100.0 - (100.0 / (1.0 + relative_strength))

        self.frame[indicator] = relative_strength_index

        self.frame.drop(
            labels=['ma_up', 'ma_down', 'down', 'up', 'change_in_price'],
            axis=1,
            inplace=True)

    def sma(self, period=20):

        if not isinstance(period, int):
            raise TypeError(f'Only int type is supported for period, '
                            f'but got {type(period)}')
        assert period > 0, (f'periods must be greater than 0, '
                            f'but got {period}')

        locals_data = locals()
        del locals_data['self']

        indicator = 'sma_' + str(period)

        self.current_indicators[indicator] = {}
        self.current_indicators[indicator]['args'] = locals_data
        self.current_indicators[indicator]['func'] = self.sma

        self.frame[indicator] = self.code_groups['close'].transform(
            lambda x: x.rolling(window=period).mean())

    def ema(self, periods=20, adjust=True):

        if not isinstance(periods, int):
            raise TypeError(f'Only int type is supported for periods, '
                            f'but got {type(periods)}')
        assert periods > 0, (f'periods must be greater than 0, '
                             f'but got {periods}')

        locals_data = locals()
        del locals_data['self']

        indicator = 'ema_' + str(periods)

        self.current_indicators[indicator] = {}
        self.current_indicators[indicator]['args'] = locals_data
        self.current_indicators[indicator]['func'] = self.ema

        self.frame[indicator] = self.code_groups['close'].transform(
            lambda x: x.ewm(span=periods, adjust=adjust, min_periods=periods
                            ).mean())

    def macd(self,
             fast_length=12,
             slow_length=26,
             signal_length=9,
             adjust=False,
             indicator='macd'):

        if not isinstance(fast_length, int):
            raise TypeError(f'Only int type is supported for fast_length, '
                            f'but got {type(fast_length)}')
        if not isinstance(slow_length, int):
            raise TypeError(f'Only int type is supported for slow_length, '
                            f'but got {type(slow_length)}')
        if not isinstance(signal_length, int):
            raise TypeError(f'Only int type is supported for signal_length, '
                            f'but got {type(signal_length)}')

        assert fast_length > 0, (f'fast_length must be greater than 0, '
                                 f'but got {fast_length}')
        assert slow_length > 0, (f'slow_length must be greater than 0, '
                                 f'but got {slow_length}')
        assert signal_length > 0, (f'signal_length must be greater than 0, '
                                   f'but got {signal_length}')

        locals_data = locals()
        del locals_data['self']

        self.current_indicators[indicator] = {}
        self.current_indicators[indicator]['args'] = locals_data
        self.current_indicators[indicator]['func'] = self.macd

        self.frame['fast_ewma'] = self.code_groups['close'].transform(
            lambda x: x.ewm(span=fast_length,
                            min_periods=fast_length,
                            adjust=adjust).mean())
        self.frame['slow_ewma'] = self.code_groups['close'].transform(
            lambda x: x.ewm(span=slow_length,
                            min_periods=slow_length,
                            adjust=adjust).mean())

        self.frame['macd'] = self.frame['fast_ewma'] - self.frame['slow_ewma']

        for code in self.code_list:
            self.frame.loc[code, 'signal'] = list(self.frame.loc[
                code,
                'macd'].transform(lambda x: x.ewm(span=signal_length,
                                                  min_periods=signal_length,
                                                  adjust=adjust).mean()))

        self.frame['histogram'] = self.frame['macd'] - self.frame['signal']

        self.frame.drop(labels=['fast_ewma', 'slow_ewma'],
                        axis=1,
                        inplace=True)

    def bollinger_bands(self, period=20, indicator='bollinger_bands'):

        if not isinstance(period, int):
            raise TypeError(f'Only int type is supported for period, '
                            f'but got {type(period)}')
        assert period > 0, (f'period must be greater than 0, '
                            f'but got {period}')

        locals_data = locals()
        del locals_data['self']

        self.current_indicators[indicator] = {}
        self.current_indicators[indicator]['args'] = locals_data
        self.current_indicators[indicator]['func'] = self.bollinger_bands

        self.frame['sma'] = self.code_groups['close'].transform(
            lambda x: x.rolling(window=period).mean())

        self.frame['std'] = self.code_groups['close'].transform(
            lambda x: x.rolling(window=period).std())

        self.frame['upper_band'] = self.frame['sma'] + 2 * self.frame['std']
        self.frame['lower_band'] = self.frame['sma'] - 2 * self.frame['std']

        self.frame.drop(labels=['std'], axis=1, inplace=True)

    def stochastic_oscillator(self,
                              K_periods=14,
                              D_periods=3,
                              indicator='stochastic_oscillator'):

        if not isinstance(K_periods, int):
            raise TypeError(f'Only int type is supported for K_periods, '
                            f'but got {type(K_periods)}')
        if not isinstance(D_periods, int):
            raise TypeError(f'Only int type is supported for D_periods, '
                            f'but got {type(D_periods)}')

        assert K_periods > 0, (f'K_periods must be greater than 0, '
                               f'but got {K_periods}')
        assert D_periods > 0, (f'D_periods must be greater than 0, '
                               f'but got {D_periods}')

        locals_data = locals()
        del locals_data['self']

        self.current_indicators[indicator] = {}
        self.current_indicators[indicator]['args'] = locals_data
        self.current_indicators[indicator]['func'] = self.stochastic_oscillator

        self.frame['K_periods_high'] = self.code_groups['high'].transform(
            lambda x: x.rolling(K_periods).max())
        self.frame['K_periods_low'] = self.code_groups['low'].transform(
            lambda x: x.rolling(K_periods).min())

        self.frame['%K'] = 100 * (
            self.frame['close'] - self.frame['K_periods_low']) / (
                self.frame['K_periods_high'] - self.frame['K_periods_low'])

        for code in self.code_list:
            self.frame.loc[code,
                           '%D'] = list(self.frame.loc[code, '%K'].transform(
                               lambda x: x.rolling(window=D_periods).mean()))

        self.frame.drop(labels=['K_periods_high', 'K_periods_low'],
                        axis=1,
                        inplace=True)

    def standard_deviation(self, period=20, indicator='standard_deviation'):

        if not isinstance(period, int):
            raise TypeError(f'Only int type is supported for period, '
                            f'but got {type(period)}')
        assert period > 0, (f'period must be greater than 0, '
                            f'but got {period}')

        locals_data = locals()
        del locals_data['self']

        self.current_indicators[indicator] = {}
        self.current_indicators[indicator]['args'] = locals_data
        self.current_indicators[indicator]['func'] = self.standard_deviation

        self.frame[indicator] = self.code_groups['close'].transform(
            lambda x: x.rolling(window=period).std())

    def refresh(self):

        self.code_groups = self.stockframe.code_groups

        for indicator in self.current_indicators:

            indicator_arguments = self.current_indicators[indicator]['args']
            indicator_function = self.current_indicators[indicator]['func']
            indicator_function(**indicator_arguments)
