from datetime import datetime, timedelta

import numpy as np
from futu import KLType, SecurityFirm, TrdMarket

from .accounts import Accounts
from .stockframe import StockFrame


class Portfolio(Accounts):
    def __init__(self,
                 host='127.0.0.1',
                 port=11111,
                 filter_trdmarket=TrdMarket.HK,
                 security_firm=SecurityFirm.FUTUSECURITIES,
                 paper_trading=False):
        super(Portfolio, self).__init__(host, port, filter_trdmarket,
                                        security_firm, paper_trading)
        self.positions = {}
        self._holdings = {}
        self.positions_count = 0
        self._portfolio_info = self.get_portfolio_info()
        self.risk_tolerance = 0.0
        self._futu_client = None
        self._historical_prices = []
        self._stockframe_daily = None

    def get_portfolio_info(self):

        portfolio_info = {}

        account_info = self.get_account_info()
        positions_dict = self.get_positions()

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

    @property
    def portfolio_info(self):
        return self._portfolio_info

    def add_position(self, code, stock_name, quantity):

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

        if not isinstance(code, str):
            raise TypeError(f'Only str type is supported for code, '
                            f'but got {type(code)}')

        if code in self.positions:
            del self.positions[code]
            return (True, '{code} was successfully removed.'.format(code=code))
        else:
            return (False,
                    '{code} did not exist in the portfolio'.format(code=code))

    @property
    def holdings(self):

        for code in self.positions.keys():
            self._holdings[code] = self.positions[code]['qty']

        return self._holdings

    # def get_holdings(self):

    #     holdings = {}

    #     for code in self.positions.keys():
    #         holdings[code] = self.positions[code]["qty"]

    #     return holdings

    def update_positions(self, order_infos):

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

        weights = {}
        weights['cash'] = 1.00

        account_info = self.get_account_info()
        total_market_value = account_info['total_assets']

        positions_dict = self.get_positions()

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

        annualized_sharpe_ratio = abs(
            average_returns - risk_free_rate) / standard_deviation * 252**0.5

        return annualized_sharpe_ratio

    def calculate_portfolio_metrics(self):

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

        historical_prices = []

        code_list = list(self.positions.keys())

        end_date = datetime.today()
        start_date = end_date - timedelta(days=365)
        end_date = end_date.strftime('%Y-%m-%d %H:%M:%S')
        start_date = start_date.strftime('%Y-%m-%d %H:%M:%S')

        for code in code_list:

            historical_quotes = self.get_historical_candles(
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
