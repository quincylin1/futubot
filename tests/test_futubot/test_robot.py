from sqlite3 import Timestamp
import pandas as pd
import pytest
from futu import (RET_OK, Market, ModifyOrderOp, OrderType, SecurityFirm,
                  SecurityType, TrdMarket, TrdSide)

from futubot.robot import Robot
from futubot.portfolio import Portfolio
from futubot.stockframe import StockFrame


def test_create_portfolio():
    futubot = Robot(
        host='127.0.0.1',
        port=11111,
        filter_trdmarket=TrdMarket.HK,
        security_firm=SecurityFirm.FUTUSECURITIES,
        paper_trading=True,
    )

    portfolio = futubot.create_portfolio(
        stocks_of_interest=['HK.00001', 'HK.00700']
    )

    assert isinstance(portfolio, Portfolio)
    futubot.close_quote_context()
    futubot.close_trade_context()

def test_create_stockframe():
    futubot = Robot(
        host='127.0.0.1',
        port=11111,
        filter_trdmarket=TrdMarket.HK,
        security_firm=SecurityFirm.FUTUSECURITIES,
        paper_trading=True,
    )

    historical_quotes = futubot.get_historical_quotes(
        start_date='2022-08-08 09:30:00',
        end_date='2022-08-08 10:30:00',
        code_list=['HK.00700']
    )
    stockframe = futubot.create_stockframe(data=historical_quotes)

    assert isinstance(stockframe, StockFrame)
    futubot.close_quote_context()
    futubot.close_trade_context()

def test_get_historical_quotes():
    futubot = Robot(
        host='127.0.0.1',
        port=11111,
        filter_trdmarket=TrdMarket.HK,
        security_firm=SecurityFirm.FUTUSECURITIES,
        paper_trading=True,
    )

    historical_quotes = futubot.get_historical_quotes(
        start_date='2022-08-08 09:30:00',
        end_date='2022-08-08 10:30:00',
        code_list=['HK.00700']
    )

    assert isinstance(historical_quotes, list)

    for key in ['time_key', 'code', 'open', 'close', 'high', 'low', 'volume']:
        assert (key in historical_quotes[0])

    futubot.close_quote_context()
    futubot.close_trade_context()

def test_get_latest_bar():
    futubot = Robot(
        host='127.0.0.1',
        port=11111,
        filter_trdmarket=TrdMarket.HK,
        security_firm=SecurityFirm.FUTUSECURITIES,
        paper_trading=True,
    )

    with pytest.raises(TypeError):
        futubot.get_latest_bar(
            code_list=['Hk.00700'],
            demo='True'
        )

    latest_prices = futubot.get_latest_bar(
        start_date='2022-08-08 09:30:00',
        end_date='2022-08-08 10:30:00',
        code_list=['HK.00700'],
        demo=True
    )

    assert isinstance(latest_prices, list)

    for key in ['time_key', 'code', 'open', 'close', 'high', 'low', 'volume']:
        assert (key in latest_prices[0])

    futubot.close_quote_context()
    futubot.close_trade_context()

def test_execute_signals():
    futubot = Robot(
        host='127.0.0.1',
        port=11111,
        filter_trdmarket=TrdMarket.HK,
        security_firm=SecurityFirm.FUTUSECURITIES,
        paper_trading=True,
    )

    with pytest.raises(TypeError):
        futubot.execute_signals(
            buy_sell_signals=['buys', 'sells']
        )

    portfolio = futubot.create_portfolio(
        stocks_of_interest=['HK.00002']
    )

    order_infos = futubot.execute_signals(
        buy_sell_signals={
            'buys': {'HK.00002': {
                'close': 52.45,
                'high': 52.45,
                'low': 52.4,
                'open': 52.45,
                'rsi_14': 20.091,
                'volume': 7000.0
            }
            },
            'sells': {},
        }
    )

    assert isinstance(order_infos, dict)

    for key in [
            'trd_side', 'order_type', 'order_status', 'order_id', 'code',
            'stock_name', 'qty', 'price', 'create_time', 'updated_time'
    ]:
        assert (key in order_infos['HK.00002'])

    ret, data = futubot.trade_context.modify_order(
        modify_order_op=ModifyOrderOp.CANCEL,
        order_id=order_infos['HK.00002']['order_id'],
        qty=0,
        price=0,
        trd_env=futubot.trd_env)
    if ret == RET_OK:
        print(data)
    else:
        print('Error in cancel_all_orders: ', data)

    futubot.close_quote_context()
    futubot.close_trade_context()


