from futu import SecurityFirm, TrdMarket

from futubot.accounts import Accounts
from futubot.indicators import Indicators
from futubot.robot import Robot


def test_change_in_price():
    accounts = Accounts(
        host='127.0.0.1',
        port=11111,
        filter_trdmarket=TrdMarket.HK,
        security_firm=SecurityFirm.FUTUSECURITIES,
        paper_trading=True,
    )
    futubot = Robot(accounts=accounts)

    historical_quotes = futubot.get_historical_quotes(
        start_date='2022-08-08 09:30:00',
        end_date='2022-08-08 12:00:00',
        code_list=['HK.00700'])

    stockframe = futubot.create_stockframe(data=historical_quotes)
    indicator_client = Indicators(stockframe=stockframe)

    indicator_client.change_in_price()
    assert 'change_in_price' in stockframe.frame.columns

    accounts.close_quote_context()
    accounts.close_trade_context()


def test_rsi():
    accounts = Accounts(
        host='127.0.0.1',
        port=11111,
        filter_trdmarket=TrdMarket.HK,
        security_firm=SecurityFirm.FUTUSECURITIES,
        paper_trading=True,
    )
    futubot = Robot(accounts=accounts)

    historical_quotes = futubot.get_historical_quotes(
        start_date='2022-08-08 09:30:00',
        end_date='2022-08-08 12:00:00',
        code_list=['HK.00700'])

    stockframe = futubot.create_stockframe(data=historical_quotes)
    indicator_client = Indicators(stockframe=stockframe)

    period = 14
    indicator_client.rsi(period=period)
    assert ('rsi_' + str(period)) in stockframe.frame.columns

    accounts.close_quote_context()
    accounts.close_trade_context()


def test_sma():
    accounts = Accounts(
        host='127.0.0.1',
        port=11111,
        filter_trdmarket=TrdMarket.HK,
        security_firm=SecurityFirm.FUTUSECURITIES,
        paper_trading=True,
    )
    futubot = Robot(accounts=accounts)

    historical_quotes = futubot.get_historical_quotes(
        start_date='2022-08-08 09:30:00',
        end_date='2022-08-08 12:00:00',
        code_list=['HK.00700'])

    stockframe = futubot.create_stockframe(data=historical_quotes)
    indicator_client = Indicators(stockframe=stockframe)

    period = 20
    indicator_client.sma(period=period)
    assert ('sma_' + str(period)) in stockframe.frame.columns

    accounts.close_quote_context()
    accounts.close_trade_context()


def test_ema():
    accounts = Accounts(
        host='127.0.0.1',
        port=11111,
        filter_trdmarket=TrdMarket.HK,
        security_firm=SecurityFirm.FUTUSECURITIES,
        paper_trading=True,
    )
    futubot = Robot(accounts=accounts)

    historical_quotes = futubot.get_historical_quotes(
        start_date='2022-08-08 09:30:00',
        end_date='2022-08-08 12:00:00',
        code_list=['HK.00700'])

    stockframe = futubot.create_stockframe(data=historical_quotes)
    indicator_client = Indicators(stockframe=stockframe)

    period = 20
    indicator_client.ema(period=period)
    assert ('ema_' + str(period)) in stockframe.frame.columns

    accounts.close_quote_context()
    accounts.close_trade_context()


def test_macd():
    accounts = Accounts(
        host='127.0.0.1',
        port=11111,
        filter_trdmarket=TrdMarket.HK,
        security_firm=SecurityFirm.FUTUSECURITIES,
        paper_trading=True,
    )
    futubot = Robot(accounts=accounts)

    historical_quotes = futubot.get_historical_quotes(
        start_date='2022-08-08 09:30:00',
        end_date='2022-08-08 12:00:00',
        code_list=['HK.00700'])

    stockframe = futubot.create_stockframe(data=historical_quotes)
    indicator_client = Indicators(stockframe=stockframe)

    fast_length = 12
    slow_length = 26
    signal_length = 9
    indicator_client.macd(fast_length=fast_length,
                          slow_length=slow_length,
                          signal_length=signal_length)
    assert 'macd' in stockframe.frame.columns
    assert 'signal' in stockframe.frame.columns
    assert 'histogram' in stockframe.frame.columns

    accounts.close_quote_context()
    accounts.close_trade_context()


def test_bollinger_bands():
    accounts = Accounts(
        host='127.0.0.1',
        port=11111,
        filter_trdmarket=TrdMarket.HK,
        security_firm=SecurityFirm.FUTUSECURITIES,
        paper_trading=True,
    )
    futubot = Robot(accounts=accounts)

    historical_quotes = futubot.get_historical_quotes(
        start_date='2022-08-08 09:30:00',
        end_date='2022-08-08 12:00:00',
        code_list=['HK.00700'])

    stockframe = futubot.create_stockframe(data=historical_quotes)
    indicator_client = Indicators(stockframe=stockframe)

    period = 20
    indicator_client.bollinger_bands(period=period)
    assert 'sma' in stockframe.frame.columns
    assert 'upper_band' in stockframe.frame.columns
    assert 'lower_band' in stockframe.frame.columns

    accounts.close_quote_context()
    accounts.close_trade_context()


def test_stochastic_oscillator():
    accounts = Accounts(
        host='127.0.0.1',
        port=11111,
        filter_trdmarket=TrdMarket.HK,
        security_firm=SecurityFirm.FUTUSECURITIES,
        paper_trading=True,
    )
    futubot = Robot(accounts=accounts)

    historical_quotes = futubot.get_historical_quotes(
        start_date='2022-08-08 09:30:00',
        end_date='2022-08-08 12:00:00',
        code_list=['HK.00700'])

    stockframe = futubot.create_stockframe(data=historical_quotes)
    indicator_client = Indicators(stockframe=stockframe)

    K_period = 14
    D_period = 3
    indicator_client.stochastic_oscillator(K_period=K_period,
                                           D_period=D_period)
    assert '%K' in stockframe.frame.columns
    assert '%D' in stockframe.frame.columns

    accounts.close_quote_context()
    accounts.close_trade_context()


def test_standard_deviation():
    accounts = Accounts(
        host='127.0.0.1',
        port=11111,
        filter_trdmarket=TrdMarket.HK,
        security_firm=SecurityFirm.FUTUSECURITIES,
        paper_trading=True,
    )
    futubot = Robot(accounts=accounts)

    historical_quotes = futubot.get_historical_quotes(
        start_date='2022-08-08 09:30:00',
        end_date='2022-08-08 12:00:00',
        code_list=['HK.00700'])

    stockframe = futubot.create_stockframe(data=historical_quotes)
    indicator_client = Indicators(stockframe=stockframe)

    period = 20
    indicator_client.standard_deviation(period=period)

    assert 'standard_deviation' in stockframe.frame.columns

    accounts.close_quote_context()
    accounts.close_trade_context()
