import pandas as pd


class StockFrame:
    """Implementation of a dataframe of stock data.

    Args:
        data (list[dict]): A list of historical quotes data
            to be converted to a dataframe.
    """
    def __init__(self, data):
        self.data = data
        self._frame = self.create_frame()
        self._code_groups = None

    @property
    def frame(self):
        """Getter for the frame property."""
        return self._frame

    @property
    def code_groups(self):
        """Setter and getter for the code_groups property.

        The code_groups property groups the stockframe dataframe
        by 'code'.

        Returns:
            (pd.DataFrameGroupBy) -- A pandas DataFrameGroupBy object grouped
                by code.
        """
        self._code_groups = self.frame.groupby(by='code',
                                               as_index=False,
                                               sort=True)

        return self._code_groups

    def create_frame(self):
        """Create a MultiIndex pandas dataframe for data.

        The dataframe has index (code, time_key) and columns:
        'open', 'close', 'high', 'low', 'volume'.

        Returns:
            price_df (pd.DataFrame): A MultiIndex pandas
                dataframe.
        """
        price_df = pd.DataFrame(data=self.data)
        price_df = self._parse_time_key_column(price_df=price_df)
        price_df = self._set_multi_index(price_df=price_df)

        return price_df

    def _parse_time_key_column(self, price_df):
        """Convert time_key column to datetime object.

        This function parses the time_key column to a pandas
        datetime object with origin 'unix'.

        Args:
            price_df (pd.DataFrame): A pandas dataframe of historical
                candlesticks with time_key column of type 'str'.

        Returns:
            price_df (pd.DataFrame): A pandas dataframe of historical
                candlesticks with time_key column of type 'datetime'.
        """
        price_df['time_key'] = pd.to_datetime(price_df['time_key'],
                                              origin='unix')

        return price_df

    def _set_multi_index(self, price_df):
        """Set the index of dataframe to be MultiIndex.

        The index of dataframe is set to be (code, time_key).

        Args:
            price_df (pd.DataFrame): A pandas dataframe with
                default numerical index.

        Returns:
            price_df (pd.DataFrame): A MultiIndex dataframe with
                index (code, time_key).
        """
        price_df = price_df.set_index(keys=['code', 'time_key'])

        return price_df

    def add_rows(self, data):
        """Add new rows to dataframe.

        This function converts the data list into a pandas
        Series and then adds to the existing MultiIndex dataframe as
        new rows.

        Args:
            data (list[dict]): A list of new candlestick data.
        """
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
