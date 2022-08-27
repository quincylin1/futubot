from datetime import datetime, timedelta

import numpy as np
from futu import KLType

from .stockframe import StockFrame


class Portfolio:
    """Implementation of user's portfolio.

    The Portfolio class contains important imformation of user's Futu
    account including the total assets, total market value and portfolio
    distribution. It also contains common evaluation metrics for backtesting
    such as total PnL value and Sharpe Ratio.

    Args:
        accounts (Accounts): The Accounts object.
    """
    def __init__(self, accounts):

        self.accounts = accounts
        self.positions = {}
        self._holdings = {}
        self.positions_count = 0
        self._portfolio_info = self.get_portfolio_info()
        self.risk_tolerance = 0.0
        self._futu_client = None
        self._historical_prices = []
        self._stockframe_daily = None

    @property
    def portfolio_info(self):
        """Getter of portfolio_info property."""
        return self._portfolio_info

    @property
    def holdings(self):
        """Getter and setter for holdings property.

        This function sets the values in holdings dict
        to be the current holding quantities of codes in
        portfolio. It also serves as a getter for the holdings
        dict.

        Returns:
            (dict[int | float]): A dict of current holding quantities.
        """
        for code in self.positions.keys():
            self._holdings[code] = self.positions[code]['qty']

        return self._holdings

    def get_portfolio_info(self):
        """Get basic information of portfolio.

        This function gets the basic information of portfolio
        including total assets, available cash, total market
        value of the holdings, total invested value of the holdings
        and the total profit and loss.

        Returns:
            portfolio_info (dict[float]): A dict of portfolio info
                with the following keys:
                    total_assets (float): The total value of assets.
                    cash (float): The available cash buying power.
                    total_market_value (float): The total market value
                        of current holdings.
                    total_invested_value (float): The total invested
                        value of current holdings.
                    total_pnl_value (float): The absolute profit and
                        loss value of current holdings.
        """
        portfolio_info = {}

        account_info = self.accounts.get_account_info()
        positions_dict = self.accounts.get_positions()

        portfolio_info['total_assets'] = account_info['total_assets']
        portfolio_info['total_market_value'] = account_info[
            'total_market_value']
        portfolio_info['cash'] = account_info['cash']

        portfolio_info['total_invested_value'] = account_info['cash']
        if positions_dict:
            for code in positions_dict.keys():
                portfolio_info['total_invested_value'] += (
                    positions_dict[code]['cost_price'] *
                    positions_dict[code]['qty'])

        portfolio_info['today_pnl_value'] = 0.0

        if positions_dict:
            for code in positions_dict.keys():
                portfolio_info['today_pnl_value'] += positions_dict[code][
                    'pnl_value']

        return portfolio_info

    def add_position(self, code, stock_name, quantity):
        """Add a position to the portfolio.

        This function adds the code, name and quantity
        of holding security to the portfolio positions. If
        the code is in stocks of interest but is not currently
        held by the trading account, the holding quantity is
        set to zero.

        Args:
            code (str): The code of security.
            stock_name (str): The name of security.
            quantity (int | float): The holding quantity.

        Returns:
            (dict) A dict of holding positions with keys 'code'
                and values 'code', 'stock_name', 'qty'.
        """
        if not isinstance(code, str):
            raise TypeError(f'Only str type is supported for code, '
                            f'but got {type(code)}')
        if not isinstance(stock_name, str):
            raise TypeError(f'Only str type is supported for stock_name, '
                            f'but got {type(stock_name)}')
        if not isinstance(quantity, (int, float)):
            raise TypeError(
                f'Only int or float type is supported for quantity, '
                f'but got {type(quantity)}')

        assert quantity >= 0, (f'quantity must be greater than or equal to 0, '
                               f'but got {quantity}')

        self.positions[code] = {}
        self.positions[code]['code'] = code
        self.positions[code]['stock_name'] = stock_name
        self.positions[code]['qty'] = quantity
        return self.positions

    def remove_position(self, code):
        """Remove position of code from portfolio.

        Args:
            code (str): The code to be removed from
                portfolio.

        Returns:
            bool: True if code is removed from portfolio,
                otherwise False.
        """
        if not isinstance(code, str):
            raise TypeError(f'Only str type is supported for code, '
                            f'but got {type(code)}')

        if code in self.positions:
            del self.positions[code]
            return (True, '{code} was successfully removed.'.format(code=code))
        else:
            return (False,
                    '{code} did not exist in the portfolio'.format(code=code))

    # def get_holdings(self):
    #     holdings = {}
    #     for code in self.positions.keys():
    #         holdings[code] = self.positions[code]["qty"]
    #     return holdings

    def update_positions(self, order_infos):
        """Update positions in portfolio based on order information.

        This function updates the cost price and holding quantity of
        positions when trading orders are present. Note that we directly
        update the positions dict of the Portfolio object instead
        of updating positions using the Futu API position_list_query()
        since it is found that the API has certain latency and
        therefore does not update the positions in real time.

        Args:
            order_infos (dict[dict]): A dict of order info.
        """
        if not isinstance(order_infos, dict):
            raise TypeError(f'Only dict type is supported for order_infos, '
                            f'but got {type(order_infos)}')

        if order_infos:
            for code in order_infos.keys():
                qty = order_infos[code]['qty']
                cost_price = order_infos[code]['price']
                trd_side = order_infos[code]['trd_side']

                if trd_side == 'SELL':
                    self.positions[code]['qty'] = 0
                else:
                    self.positions[code]['qty'] = qty

                self.positions[code]['cost_price'] = cost_price

    # def update_positions(self):
    #     existing_positions = self.get_positions()
    #     for code in self.positions.keys():
    #         if code not in existing_positions:
    #             # code already been sold
    #             self.positions[code]["qty"] = 0
    #         else:
    #             self.positions[code]["qty"] = existing_positions[code]["qty"]

    def calculate_portfolio_weights(self):
        """Calculate the weights of holdings in portfolio.

        The weight of a given stock is the ratio between the
        market value of the stock and the total market value.
        If the stock is in stocks of interest but is not
        currently held by the account, a zero weight is assigned
        to the stock.

        Returns:
            weights (dict[float]): The weights of holdings in
                portfolio. The keys are the codes of holdings
                and the weights are expressed in ratio terms.
        """
        weights = {}
        weights['cash'] = 1.00

        account_info = self.accounts.get_account_info()
        total_market_value = account_info['total_assets']

        positions_dict = self.accounts.get_positions()

        code_list = list(self.positions.keys())

        for code in code_list:

            if code in positions_dict:

                market_value = positions_dict[code]['market_value']
                weights[code] = round(market_value / total_market_value, 3)

            else:
                weights[code] = 0.0

        for code in code_list:
            weights['cash'] -= weights[code]

        return weights

    def portfolio_variance(self, weights, covariance_matrix):
        """Calculate the portfolio variance.

        The variance of portfolio is a measure of the overall risk
        of portfolio. It is the spread of the actual returns of the
        securities that constitute the portfolio. The formula of
        portfolio variance is:

            portfolio_var = weights^T * covariance_matrix * weights

        where weights^T is the transpose of weights vector.

        Args:
            weights (dict[float]): The weights of holdings in
                portfolio with length n, where n is the number of holdings.
            covariance_matrix (pd.DataFrame): The n x n covariance matrix of
                the log daily returns of holdings in portfolio, where n is
                the number of holdings.

        Returns:
            portfolio_variance (float): The portfolio variance.
        """
        if not isinstance(weights, dict):
            raise TypeError(f'Only dict type is supported for weights, '
                            f'but got {type(weights)}')

        if 'cash' in weights:
            weights.pop('cash')

        sorted_codes = list(weights.keys())
        sorted_codes.sort()

        sorted_weights = np.array([weights[code] for code in sorted_codes])

        portfolio_variance = np.dot(sorted_weights.T,
                                    np.dot(covariance_matrix, sorted_weights))

        return portfolio_variance

    def portfolio_weighted_returns(self, portfolio_metrics):
        """Calculate the total weighted returns of portfolio.

        This function calculates the total returns of portfolio weighted
        by the respective market value of each holding.

        Args:
            portfolio_metrics (dict[dict]): A dict of portfolio metrics.

        Returns:
            portfolio_weighted_returns: The total weighted returns of
                portfolio.
        """
        if not isinstance(portfolio_metrics, dict):
            raise TypeError(
                f'Only dict type is supported for portfolio_metrics, '
                f'but got {type(portfolio_metrics)}')

        portfolio_weighted_returns = 0.0

        for code in self.positions.keys():
            portfolio_weighted_returns += portfolio_metrics[code][
                'weighted_returns']

        return portfolio_weighted_returns

    def annualized_sharpe_ratio(self,
                                average_returns,
                                variance,
                                risk_free_rate=0.00):
        """Calculate the annualized Sharpe Ratio of portfolio.

        The (annualized) Sharpe Ratio is a defined as the (annual)
        average return in excess of risk-free rate per unit of
        volatility. A portfolio with a Sharpe Ratio of 1.5 or greater
        is considered good.

        Args:
            average_returns (float): The average weighted daily return.
            variance (float): The portfolio variance.
            risk_free_rate (float): The rate of return of a zero-risk
                investment (e.g. government bonds). Default: 0.00.

        Returns:
            annaualized_sharpe_ratio (float): The annualized Sharpe Ratio.
        """
        if not isinstance(average_returns, (int, float)):
            raise TypeError(
                f'Only int or float type is supported for average_returns, '
                f'but got {type(average_returns)}')
        if not isinstance(variance, (int, float)):
            raise TypeError(
                f'Only int or float type is supported for variance, '
                f'but got {type(variance)}')
        if not isinstance(risk_free_rate, (int, float)):
            raise TypeError(
                f'Only int or float type is supported for risk_free_rate, '
                f'but got {type(risk_free_rate)}')

        assert variance >= 0, (f'variance must be greater than or equal to 0, '
                               f'but got {variance}')

        standard_deviation = variance**0.5

        # Annualize by multiply by 252 trading days per year.
        annualized_sharpe_ratio = abs(
            average_returns - risk_free_rate) / standard_deviation * 252**0.5

        return annualized_sharpe_ratio

    def calculate_portfolio_metrics(self):
        """Calculate common metrics that measure portfolio performance.

        Returns:
            portfolio_metrics (dict[dict]): A dict of portfolio metrics. The
                outer dict has keys 'portfolio' and 'codes'. For each code, the
                inner dict contains the following keys:
                    average_returns (float): The average log daily return.
                    covariance_of_returns (dict[dict]): The covariance of
                        returns with respect to other holdings.
                    standard_deviation_of_returns (float): The standard
                        deviation of log daily returns.
                    variance_of_returns (float): The variance of log daily
                        returns.
                    weight (float): The weight of holding.
                    weighted_returns (float): The average log daily return
                        multipliednby the weight of holding.
                For the portolio key, the inner dict contains the following
                keys:
                    annualized_sharpe_ratio (float): The annualized Sharpe
                        Ratio of portfolio.
                    average_returns (float): The weighted average return of
                        portfolio.
                    variance (float): The variance of portfolio.
        """
        if not self._stockframe_daily:
            self._get_daily_historical_prices()

        portfolio_weights = self.calculate_portfolio_weights()

        self._stockframe_daily.frame[
            'log_daily_returns'] = self._stockframe_daily.code_groups[
                'close'].transform(lambda x: np.log(x / x.shift()))

        self._stockframe_daily.frame[
            'daily_returns_avg'] = self._stockframe_daily.code_groups[
                'log_daily_returns'].transform(lambda x: x.mean())

        self._stockframe_daily.frame[
            'daily_returns_std'] = self._stockframe_daily.code_groups[
                'log_daily_returns'].transform(lambda x: x.std())

        returns_cov = self._stockframe_daily.frame.unstack(
            level=0)['log_daily_returns'].cov()

        returns_avg = self._stockframe_daily.code_groups[
            'daily_returns_avg'].tail(n=1).to_dict()

        returns_std = self._stockframe_daily.code_groups[
            'daily_returns_std'].tail(n=1).to_dict()

        portfolio_metrics = {}

        portfolio_variance = self.portfolio_variance(
            weights=portfolio_weights, covariance_matrix=returns_cov)

        for (code, last_datetime) in returns_std:

            portfolio_metrics[code] = {}
            portfolio_metrics[code]['weight'] = portfolio_weights[code]
            portfolio_metrics[code]['average_returns'] = returns_avg[(
                code, last_datetime)]
            portfolio_metrics[code]['weighted_returns'] = returns_avg[
                (code, last_datetime)] * portfolio_metrics[code]['weight']
            portfolio_metrics[code][
                'standard_deviation_of_returns'] = returns_std[(code,
                                                                last_datetime)]
            portfolio_metrics[code]['variance_of_returns'] = returns_std[(
                code, last_datetime)]**2
            portfolio_metrics[code]['covariance_of_returns'] = returns_cov.loc[
                [code]].to_dict()

        portfolio_metrics['portfolio'] = {}
        portfolio_metrics['portfolio']['variance'] = portfolio_variance

        portfolio_weighted_returns = self.portfolio_weighted_returns(
            portfolio_metrics)
        portfolio_metrics['portfolio'][
            'average_returns'] = portfolio_weighted_returns

        portfolio_metrics['portfolio'][
            'annualized_sharpe_ratio'] = self.annualized_sharpe_ratio(
                portfolio_weighted_returns, portfolio_variance)

        return portfolio_metrics

    def _get_daily_historical_prices(self, ktype=KLType.K_DAY):
        """Get the daily historical prices of holdings in portfolio.

        The daily historical prices are used to calculate the common
        metrics that measure portfolio performance. The end_date of
        the historical prices is the current date, and the start_date
        is one year behind the end_date.

        Args:
            ktype (KLType): The type of candlestick. Default: K_DAY.

        Returns:
            (StockFrame): A StockFrame object of historical prices of
                all holdings in portfolio.
        """
        historical_prices = []

        code_list = list(self.positions.keys())

        end_date = datetime.today()
        start_date = end_date - timedelta(days=365)
        end_date = end_date.strftime('%Y-%m-%d %H:%M:%S')
        start_date = start_date.strftime('%Y-%m-%d %H:%M:%S')

        for code in code_list:
            historical_quotes = self.accounts.get_historical_candles(
                code=code,
                start=start_date,
                end=end_date,
                ktype=ktype,
            )

            for index, candle in historical_quotes.iterrows():
                candle = candle.to_dict()
                historical_price = {}
                historical_price['time_key'] = candle['time_key']
                historical_price['code'] = candle['code']
                historical_price['open'] = candle['open']
                historical_price['close'] = candle['close']
                historical_price['high'] = candle['high']
                historical_price['low'] = candle['low']
                historical_price['volume'] = candle['volume']
                historical_prices.append(historical_price)

        self._stockframe_daily = StockFrame(data=historical_prices)
        self._stockframe_daily.create_frame()

        return self._stockframe_daily
