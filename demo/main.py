import argparse
import pprint
import time
from datetime import datetime, timedelta

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
    # indicator_client.rsi(**cfg_dict["indicators"]["rsi"])
    indicator_client.rsi()
    indicator_client.sma()
    indicator_client.ema()
    indicator_client.macd()
    indicator_client.bollinger_bands()
    indicator_client.standard_deviation()
    indicator_client.stochastic_oscillator()

    start_date = cfg_dict['historical_quote_dates']['start_date']
    end_date = cfg_dict['historical_quote_dates']['end_date']

    while True:
        print('')

        print('holdings before', portfolio.holdings)

        # Automatically update endtime
        end_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
        end_date = end_date + timedelta(minutes=1)
        end_date = end_date.strftime('%Y-%m-%d %H:%M:%S')

        latest_prices = futubot.get_latest_bar(start_date=start_date,
                                               end_date=end_date,
                                               demo=True)

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

        time.sleep(5)


if __name__ == '__main__':
    main()
