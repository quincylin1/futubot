from futubot.accounts import Accounts
from py import code
import pytest 
from futubot.accounts import Accounts
from futu import TrdMarket, SecurityFirm
from futu import TrdSide, OrderType, RET_OK, ModifyOrderOp, Market, SecurityType
import pandas as pd


def test_get_market_state():
    accounts = Accounts(
        host='127.0.0.1',
        port=11111,
        filter_trdmarket=TrdMarket.HK,
        security_firm=SecurityFirm.FUTUSECURITIES,
        paper_trading=True
    )

    with pytest.raises(TypeError):
        accounts.get_market_state('HK.00700')
    
    code_list = ['HK.00700', 'HK.00001']
    market_state = accounts.get_market_state(code_list)
    assert isinstance(market_state, dict)

    for key in ['stock_name', 'market_state']:
        assert (key in market_state[code_list[0]])

    accounts.close_quote_context()
    accounts.close_trade_context()

def test_get_account_list():
    accounts = Accounts(
        host='127.0.0.1',
        port=11111,
        filter_trdmarket=TrdMarket.HK,
        security_firm=SecurityFirm.FUTUSECURITIES,
        paper_trading=True
    )
    
    account_list = accounts.get_account_list()
    assert isinstance(account_list, dict)

    accounts.close_quote_context()
    accounts.close_trade_context()

def test_get_account_info():
    accounts = Accounts(
        host='127.0.0.1',
        port=11111,
        filter_trdmarket=TrdMarket.HK,
        security_firm=SecurityFirm.FUTUSECURITIES,
        paper_trading=True
    )
    
    account_info = accounts.get_account_info()
    assert isinstance(account_info, dict)

    for key in ['power', 'max_power_short', 'net_cash_power', 'total_assets', 'cash', 'total_market_value']:
        assert (key in account_info)
    
    accounts.close_quote_context()
    accounts.close_trade_context()

def test_get_historical_candles():
    accounts = Accounts(
        host='127.0.0.1',
        port=11111,
        filter_trdmarket=TrdMarket.HK,
        security_firm=SecurityFirm.FUTUSECURITIES,
        paper_trading=True
    )

    with pytest.raises(TypeError):
        accounts.get_historical_candles(
            code=700,
            start='2022-08-08 09:30:00',
            end='2022-08-08 10:30:00'
            )
    with pytest.raises(TypeError):
        accounts.get_historical_candles(
            code='HK.00700',
            start=120000,
            end='2022-08-08 10:30:00'
            )
    with pytest.raises(TypeError):
        accounts.get_historical_candles(
            code='HK.00700',
            start='2022-08-08 09:30:00',
            end=120000
            )
    with pytest.raises(TypeError):
        accounts.get_historical_candles(
            code='HK.00700',
            start='2022-08-08 09:30:00',
            end='2022-08-08 10:30:00',
            ktype=1
            )
    with pytest.raises(TypeError):
        accounts.get_historical_candles(
            code='HK.00700',
            start='2022-08-08 09:30:00',
            end='2022-08-08 10:30:00',
            max_count='1000'
            )
    historical_quotes = accounts.get_historical_candles(
        code='HK.00700',
            start='2022-08-08 09:30:00',
            end='2022-08-08 10:30:00',
    )

    assert isinstance(historical_quotes, pd.DataFrame)
    accounts.close_quote_context()
    accounts.close_trade_context()

def test_get_positions():
    accounts = Accounts(
        host='127.0.0.1',
        port=11111,
        filter_trdmarket=TrdMarket.HK,
        security_firm=SecurityFirm.FUTUSECURITIES,
        paper_trading=True
    )

    with pytest.raises(TypeError):
        accounts.get_positions(
            code=700
        )
    
    code = 'HK.00700'
    positions_dict = accounts.get_positions(
        code=code
    )

    assert isinstance(positions_dict, dict)

    for key in ['code', 'position_side', 'stock_name', 'qty', 'cost_price', 'market_value', 'current_price', 'pnl_ratio', 'pnl_value']:
        assert (key in positions_dict[code])


    accounts.close_quote_context()
    accounts.close_trade_context()

def test_unlock_trade():
    accounts = Accounts(
        host='127.0.0.1',
        port=11111,
        filter_trdmarket=TrdMarket.HK,
        security_firm=SecurityFirm.FUTUSECURITIES,
        paper_trading=True
    )

    with pytest.raises(TypeError):
        accounts.unlock_trade(
            password=123456
        )
    with pytest.raises(TypeError):
        accounts.unlock_trade(
            password='******',
            is_unlock='True'
        )

    unlock_state = accounts.unlock_trade(
        password='******',
        is_unlock=True
    )
    assert unlock_state == False

    accounts.close_quote_context()
    accounts.close_trade_context()
            
def test_place_order():
    accounts = Accounts(
        host='127.0.0.1',
        port=11111,
        filter_trdmarket=TrdMarket.HK,
        security_firm=SecurityFirm.FUTUSECURITIES,
        paper_trading=True
    )

    with pytest.raises(TypeError):
        accounts.place_order(
            price='100.0',
            qty=100.0,
            code='HK.00700',
            trd_side=TrdSide.BUY,
            order_type=OrderType.NORMAL
        )
    with pytest.raises(TypeError):
        accounts.place_order(
            price=100.0,
            qty='100.0',
            code='HK.00700',
            trd_side=TrdSide.BUY,
            order_type=OrderType.NORMAL
        )
    with pytest.raises(TypeError):
        accounts.place_order(
            price=100.0,
            qty=100.0,
            code=700,
            trd_side=TrdSide.BUY,
            order_type=OrderType.NORMAL
        )
    with pytest.raises(TypeError):
        accounts.place_order(
            price=100.0,
            qty=100.0,
            code='HK.00700',
            trd_side=1,
            order_type=OrderType.NORMAL
        )
    with pytest.raises(TypeError):
        accounts.place_order(
            price=100.0,
            qty=100.0,
            code='HK.00700',
            trd_side=TrdSide.BUY,
            order_type=1
        )

    order_info = accounts.place_order(
        price=100.0,
        qty=100.0,
        code='HK.00700',
        trd_side=TrdSide.BUY,
        order_type=OrderType.NORMAL
    )
    assert isinstance(order_info, dict)

    for key in ['trd_side', 'order_type', 'order_status', 'order_id', 'code', 'stock_name', 'qty', 'price', 'create_time', 'updated_time']:
        assert (key in order_info)

    ret, data = accounts.trade_context.modify_order(
                            modify_order_op=ModifyOrderOp.CANCEL,
                            order_id=order_info['order_id'],
                            qty=0,
                            price=0,
                            trd_env=accounts.trd_env)
    if ret == RET_OK:
        print(data)
    else:
        print('Error in cancel_all_orders: ', data)

    
    accounts.close_quote_context()
    accounts.close_trade_context()

def test_get_lot_size():
    accounts = Accounts(
        host='127.0.0.1',
        port=11111,
        filter_trdmarket=TrdMarket.HK,
        security_firm=SecurityFirm.FUTUSECURITIES,
        paper_trading=True
    )

    with pytest.raises(TypeError):
        accounts.get_lot_size(
            code_list='HK.00700',
            market=Market.HK,
            stock_type=SecurityType.STOCK
        )
    with pytest.raises(TypeError):
        accounts.get_lot_size(
            code_list=['HK.00700'],
            market=1,
            stock_type=SecurityType.STOCK
        )
    with pytest.raises(TypeError):
        accounts.get_lot_size(
            code_list=['HK.00700'],
            market=Market.HK,
            stock_type=1
        )

    lot_sizes = accounts.get_lot_size(
        code_list=['HK.00700']
    )
    assert isinstance(lot_sizes, dict)
    
    accounts.close_quote_context()
    accounts.close_trade_context()

def test_check_today_orders():
    accounts = Accounts(
        host='127.0.0.1',
        port=11111,
        filter_trdmarket=TrdMarket.HK,
        security_firm=SecurityFirm.FUTUSECURITIES,
        paper_trading=True
    )

    with pytest.raises(TypeError):
        accounts.check_today_orders(
            code=700,
        )
    with pytest.raises(TypeError):
        accounts.check_today_orders(
            code=['HK.00700'],
            status_filter_list='SUBMITTED'
        )

    today_orders = accounts.check_today_orders(
        code='HK.00700'
    )
    assert isinstance(today_orders, pd.DataFrame)

    accounts.close_quote_context()
    accounts.close_trade_context()

def test_check_existing_orders():
    accounts = Accounts(
        host='127.0.0.1',
        port=11111,
        filter_trdmarket=TrdMarket.HK,
        security_firm=SecurityFirm.FUTUSECURITIES,
        paper_trading=True
    )

    with pytest.raises(TypeError):
        accounts.check_existing_orders(
            code_list=700,
        )

    code_list = ['HK.00700']
    existing_orders = accounts.check_existing_orders(
        code_list=code_list
    )
    assert isinstance(existing_orders, dict)
    assert isinstance(existing_orders[code_list[0]], bool)

    accounts.close_quote_context()
    accounts.close_trade_context()

def test_get_max_power():
    accounts = Accounts(
        host='127.0.0.1',
        port=11111,
        filter_trdmarket=TrdMarket.HK,
        security_firm=SecurityFirm.FUTUSECURITIES,
        paper_trading=True
    )

    with pytest.raises(TypeError):
        accounts.get_max_power(
            code=700,
            price=350.0,
            order_type=OrderType.NORMAL
        )
    with pytest.raises(TypeError):
        accounts.get_max_power(
            code='HK.00700',
            price='350.0',
            order_type=OrderType.NORMAL
        )
    with pytest.raises(TypeError):
        accounts.get_max_power(
            code='HK.00700',
            price=350.0,
            order_type=1
        )

    code = 'HK.00700'
    price = 350.0

    max_power = accounts.get_max_power(
        code=code,
        price=price
    )
    assert isinstance(max_power, dict)
    
    for key in ['max_cash_buy', 'max_cash_and_margin_buy', 'max_position_sell', 'max_sell_short', 'max_buy_back']:
        assert (key in max_power)

    accounts.close_quote_context()
    accounts.close_trade_context()