class Indicators:
    """Implementation of common technical indicators.

    Args:
        stockframe (StockFrame): A stockframe object for which the
            indicators are calculated.
    """
    def __init__(self, stockframe):
        self.stockframe = stockframe
        self.code_groups = stockframe.code_groups
        self.current_indicators = {}
        self.frame = stockframe.frame
        self.code_list = stockframe.frame.index.get_level_values(0).to_list()

    def change_in_price(self, indicator='change_in_price'):
        """Calculate the change in price.

        The change in price is the difference between adjacent close
        prices.

        Args:
            indicator (str): The name of the indicator. Default:
                change_in_price.
        """
        self.frame[indicator] = self.code_groups['close'].transform(
            lambda x: x.diff())

    def rsi(self, period=14, ema=True):
        """Calculate the Relative Strength Index (RSI).

        Args:
            period (int): The period of RSI calculation. Default: 14.
            ema (bool): Whether to use exponential moving averages for
                RSI calculation. Default: True.
        """
        if not isinstance(period, int):
            raise TypeError(f'Only int type is supported for period, '
                            f'but got {type(period)}')
        assert period > 0, (f'period must be greater than 0, '
                            f'but got {period}')

        locals_data = locals()
        del locals_data['self']

        indicator = 'rsi_' + str(period)

        self.current_indicators[indicator] = {}
        self.current_indicators[indicator]['args'] = locals_data
        self.current_indicators[indicator]['func'] = self.rsi

        if 'change_in_price' not in self.frame.columns:
            self.change_in_price()

        self.frame['up'] = self.code_groups['change_in_price'].transform(
            lambda x: x.clip(lower=0))

        self.frame['down'] = self.code_groups['change_in_price'].transform(
            lambda x: -1 * x.clip(upper=0))

        if ema:
            self.frame['ma_up'] = self.code_groups['up'].transform(
                lambda x: x.ewm(span=period, adjust=True, min_periods=period
                                ).mean())

            self.frame['ma_down'] = self.code_groups['down'].transform(
                lambda x: x.ewm(span=period, adjust=True, min_periods=period
                                ).mean())
        else:
            self.frame['ma_up'] = self.code_groups['up'].transform(
                lambda x: x.rolling(window=period, adjust=False).mean())

            self.frame['ma_down'] = self.code_groups['down'].transform(
                lambda x: x.rolling(window=period, adjust=False).mean())

        relative_strength = self.frame['ma_up'] / self.frame['ma_down']
        relative_strength_index = 100.0 - (100.0 / (1.0 + relative_strength))

        self.frame[indicator] = relative_strength_index

        self.frame.drop(
            labels=['ma_up', 'ma_down', 'down', 'up', 'change_in_price'],
            axis=1,
            inplace=True)

    def sma(self, period=20):
        """Calculate the Simple Moving Average (SMA).

        Args:
            period (int): The period of SMA calculation. Default: 20.
        """
        if not isinstance(period, int):
            raise TypeError(f'Only int type is supported for period, '
                            f'but got {type(period)}')
        assert period > 0, (f'period must be greater than 0, '
                            f'but got {period}')

        locals_data = locals()
        del locals_data['self']

        indicator = 'sma_' + str(period)

        self.current_indicators[indicator] = {}
        self.current_indicators[indicator]['args'] = locals_data
        self.current_indicators[indicator]['func'] = self.sma

        self.frame[indicator] = self.code_groups['close'].transform(
            lambda x: x.rolling(window=period).mean())

    def ema(self, period=20, adjust=True):
        """Calculate the Exponential Moving Average (EMA).

        The decay is specified by period in terms of span:
            alpha = 2 / (span + 1) for span >= 1.
        The min_periods in ema calculation is equal to the period.

        Args:
            period (int): The period of EMA calculation. Default: 20.
            adjust (bool): Whether to divide by decaying adjustment
                factor in beginning periods to account for imbalance
                in relative weightings. Default: True.
        """
        if not isinstance(period, int):
            raise TypeError(f'Only int type is supported for period, '
                            f'but got {type(period)}')
        assert period > 0, (f'period must be greater than 0, '
                            f'but got {period}')

        locals_data = locals()
        del locals_data['self']

        indicator = 'ema_' + str(period)

        self.current_indicators[indicator] = {}
        self.current_indicators[indicator]['args'] = locals_data
        self.current_indicators[indicator]['func'] = self.ema

        self.frame[indicator] = self.code_groups['close'].transform(
            lambda x: x.ewm(span=period, adjust=adjust, min_periods=period
                            ).mean())

    def macd(self,
             fast_length=12,
             slow_length=26,
             signal_length=9,
             adjust=False,
             indicator='macd'):
        """Calculate the Moving Average Convergence Divergence (MACD).

        Args:
            fast_length (int): The period of the fast EMA. Default: 12.
            slow_length (int): The period of the slow EMA. Default: 26.
            signal_length (int): The period of the signal line. Default: 9.
            adjust (bool): Whether to divide by decaying adjustment
                factor in beginning periods to account for imbalance
                in relative weightings when calculating EMAs.
                Default: False.
            indicator (str): The name of the indicator. Default: macd.
        """
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

        self.frame['fast_ema'] = self.code_groups['close'].transform(
            lambda x: x.ewm(span=fast_length,
                            min_periods=fast_length,
                            adjust=adjust).mean())
        self.frame['slow_ema'] = self.code_groups['close'].transform(
            lambda x: x.ewm(span=slow_length,
                            min_periods=slow_length,
                            adjust=adjust).mean())

        self.frame['macd'] = self.frame['fast_ema'] - self.frame['slow_ema']

        for code in self.code_list:
            self.frame.loc[code, 'signal'] = list(self.frame.loc[
                code,
                'macd'].transform(lambda x: x.ewm(span=signal_length,
                                                  min_periods=signal_length,
                                                  adjust=adjust).mean()))

        self.frame['histogram'] = self.frame['macd'] - self.frame['signal']

        self.frame.drop(labels=['fast_ema', 'slow_ema'], axis=1, inplace=True)

    def bollinger_bands(self, period=20, indicator='bollinger_bands'):
        """Calculate the Bollinger Bands.

        Args:
            period (int): The period of SMA for which the Bollinger Bands
                are calculated. Default: 20.
            indicator (str): The name of the indicator.
                Default: bollinger_bands.
        """
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
                              K_period=14,
                              D_period=3,
                              indicator='stochastic_oscillator'):
        """Calculate the Stochastic Oscillator.

        Args:
            K_period (int): The period of K-line (slow SMA).
                Default: 14.
            D_period (int): The period of the D-line (fast SMA).
                Default: 3.
            indicator (str): The name of the indicator.
                Default: stochastic_oscillator.
        """
        if not isinstance(K_period, int):
            raise TypeError(f'Only int type is supported for K_period, '
                            f'but got {type(K_period)}')
        if not isinstance(D_period, int):
            raise TypeError(f'Only int type is supported for D_period, '
                            f'but got {type(D_period)}')

        assert K_period > 0, (f'K_period must be greater than 0, '
                              f'but got {K_period}')
        assert D_period > 0, (f'D_period must be greater than 0, '
                              f'but got {D_period}')

        locals_data = locals()
        del locals_data['self']

        self.current_indicators[indicator] = {}
        self.current_indicators[indicator]['args'] = locals_data
        self.current_indicators[indicator]['func'] = self.stochastic_oscillator

        self.frame['K_period_high'] = self.code_groups['high'].transform(
            lambda x: x.rolling(K_period).max())
        self.frame['K_period_low'] = self.code_groups['low'].transform(
            lambda x: x.rolling(K_period).min())

        self.frame['%K'] = 100 * (
            self.frame['close'] - self.frame['K_period_low']) / (
                self.frame['K_period_high'] - self.frame['K_period_low'])

        for code in self.code_list:
            self.frame.loc[code,
                           '%D'] = list(self.frame.loc[code, '%K'].transform(
                               lambda x: x.rolling(window=D_period).mean()))

        self.frame.drop(labels=['K_period_high', 'K_period_low'],
                        axis=1,
                        inplace=True)

    def standard_deviation(self, period=20, indicator='standard_deviation'):
        """Calculate the Standard Deviation.

        Args:
            period (int): The period of SMA for which the standard deviation
                is calculated. Default: 20.
            indicator (str): The name of the indicator.
                Default: standard_deviation.
        """
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
        """Refresh the current indicators after new rows are added."""
        self.code_groups = self.stockframe.code_groups

        for indicator in self.current_indicators:

            indicator_arguments = self.current_indicators[indicator]['args']
            indicator_function = self.current_indicators[indicator]['func']
            indicator_function(**indicator_arguments)
