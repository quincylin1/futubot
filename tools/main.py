import argparse
import pprint

import pandas as pd

from futubot.indicators import Indicators
from futubot.robot import Robot
from utils.config import Config


def parse_args():
    parser = argparse.ArgumentParser(description='Run FutuBot')
    parser.add_argument('config', help='config file path')
    parser.add_argument('--output-dir', help='the directory to save the logs')
    parser.add_argument('--display-all-cols',
                        action='store_true',
                        help='whether to display all columns of stockframe.')
    args = parser.parse_args()

    return args


def main():
    args = parse_args()

    cfg_dict = Config.parse_config(cfg_pth=args.config)
    pprint.pprint(cfg_dict)

    if args.display_all_cols:
        pd.set_option('display.max_columns', None)

    futubot = Robot(**cfg_dict['account'])

    portfolio = futubot.create_portfolio(
        stocks_of_interest=cfg_dict['stocks_of_interest'])
    pprint.pprint(portfolio.positions)

    historical_quotes = futubot.get_historical_quotes(
        **cfg_dict['historical_quote_dates'], )

    stockframe = futubot.create_stockframe(data=historical_quotes)
    print(stockframe.frame)

    pprint.pprint(portfolio.calculate_portfolio_metrics())
    print('')
    pprint.pprint(portfolio.portfolio_info)

    indicator_client = Indicators(stockframe=stockframe)
    # indicators.rsi(**cfg_dict["indicators"]["rsi"])
    indicator_client.rsi()
    indicator_client.sma()
    indicator_client.ema()
    indicator_client.ema()
    indicator_client.bollinger_bands()
    indicator_client.macd()
    indicator_client.stochastic_oscillator()
    indicator_client.standard_deviation()

    while Robot.is_regular_trading_time():
        print('')

        print('holdings before', portfolio.holdings)

        latest_prices = futubot.get_latest_bar()

        stockframe.add_rows(data=latest_prices)
        indicator_client.refresh()

        existing_orders = futubot.check_existing_orders(
            code_list=portfolio.holdings)
        print('existing_orders', existing_orders)

        StrategyClass = cfg_dict['strategy']['name']

        strategy_client = StrategyClass(stockframe, portfolio,
                                        indicator_client, existing_orders,
                                        **cfg_dict['strategy']['params'])
        buy_sell_signals = strategy_client.calculate_buy_sell_signals()

        order_infos = futubot.execute_signals(
            buy_sell_signals=buy_sell_signals)
        pprint.pprint(order_infos)

        portfolio.update_positions(order_infos=order_infos)

        print('holdings after', portfolio.holdings)

        last_bar_timestamp = stockframe.frame.tail(1).index.get_level_values(1)
        futubot.wait_till_next_bar(last_bar_timestamp=last_bar_timestamp)

    # Check portfolio metrics after end of trading day
    pprint.pprint(portfolio.calculate_portfolio_metrics())
    print('')
    pprint.pprint(portfolio.portfolio_info)

    futubot.cancel_all_orders()
    print('Outside regular trading hours, press Ctrl-C to exit.')


if __name__ == '__main__':
    main()
