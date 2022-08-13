import pandas as pd


class StockFrame:
    def __init__(self, data):
        self.data = data
        self._frame = self.create_frame()
        self._code_groups = None
        # self.code_rolling_groups = self.create_code_rolling_groups()

    @property
    def frame(self):
        return self._frame

    @property
    def code_groups(self):

        self._code_groups = self.frame.groupby(by='code',
                                               as_index=False,
                                               sort=True)

        return self._code_groups

    def create_code_rolling_groups(self, size):

        code_rolling_groups = self.code_groups.rolling(size)
        return code_rolling_groups

    def create_frame(self):

        price_df = pd.DataFrame(data=self.data)
        # price_df = self._parse_datetime_column(price_df=price_df)
        price_df = self._set_multi_index(price_df=price_df)

        return price_df

    def _parse_datetime_column(self, price_df):

        price_df['datetime'] = pd.to_datetime(price_df['time_key'],
                                              origin='unix')

        return price_df

    def _set_multi_index(self, price_df):

        price_df = price_df.set_index(keys=['code', 'time_key'])

        return price_df

    def add_rows(self, data):

        if not isinstance(data, list):
            raise TypeError(f'Only list type is supported for data, '
                            f'but got {type(data)}')

        column_names = ['open', 'close', 'high', 'low', 'volume']

        for quote in data:

            time_stamp = pd.to_datetime(quote['time_key'], origin='unix')

            # MultiIndex dataframe with index (code, time_stamp)
            row_id = (quote['code'], time_stamp)

            row_values = [
                quote['open'],
                quote['close'],
                quote['high'],
                quote['low'],
                quote['volume'],
            ]

            new_row = pd.Series(data=row_values)
            self.frame.loc[row_id, column_names] = new_row.values
            self.frame.sort_index(inplace=True)
