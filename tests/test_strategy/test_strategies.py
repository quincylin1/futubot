from futu import SecurityFirm, TrdMarket

from futubot.indicators import Indicators
from futubot.robot import Robot
from Strategy.BollingerBandsStrategy import BollingerBandsStrategy
from Strategy.MACDCrossOverStrategy import MACDCrossOverStrategy
from Strategy.MAStrategy import MAStrategy
from Strategy.RSIStrategy import RSIStrategy


def test_rsi_strategy():
    futubot = Robot(
        host='127.0.0.1',
        port=11111,
        filter_trdmarket=TrdMarket.HK,
        security_firm=SecurityFirm.FUTUSECURITIES,
        paper_trading=True,
    )

    # stocks_of_interest must be a stock not currently held.
    portfolio = futubot.create_portfolio(stocks_of_interest=['HK.00002'])

    period = 14
    indicator = 'rsi_' + str(period)

    historical_quotes = [{
        'time_key': '2022-08-19 10:30:00',
        'code': 'HK.00002',
        'open': 64.6,
        'close': 61.6,
        'high': 70.6,
        'low': 60.1,
        'volume': 30600,
        indicator: 15.0
    }]
    stockframe = futubot.create_stockframe(data=historical_quotes)

    indicator_client = Indicators(stockframe=stockframe)
    existing_orders = {'HK.00002': False}

    strategy_client = RSIStrategy(stockframe=stockframe,
                                  portfolio=portfolio,
                                  indicator_client=indicator_client,
                                  existing_orders=existing_orders)

    buy_sell_signals = strategy_client.calculate_buy_sell_signals()
    assert len(buy_sell_signals['buys']) > 0

    futubot.close_quote_context()
    futubot.close_trade_context()


def test_ma_strategy():
    futubot = Robot(
        host='127.0.0.1',
        port=11111,
        filter_trdmarket=TrdMarket.HK,
        security_firm=SecurityFirm.FUTUSECURITIES,
        paper_trading=True,
    )

    # stocks_of_interest must be a stock not currently held.
    portfolio = futubot.create_portfolio(stocks_of_interest=['HK.00002'])

    short_period = 20
    long_period = 50
    short_period_indicator = 'sma_' + str(short_period)
    long_period_indicator = 'sma_' + str(long_period)

    historical_quotes = [{
        'time_key': '2022-08-19 10:30:00',
        'code': 'HK.00002',
        'open': 64.6,
        'close': 61.6,
        'high': 70.6,
        'low': 60.1,
        'volume': 30600,
        short_period_indicator: 60.0,
        long_period_indicator: 50.0
    }]
    stockframe = futubot.create_stockframe(data=historical_quotes)

    indicator_client = Indicators(stockframe=stockframe)
    existing_orders = {'HK.00002': False}

    strategy_client = MAStrategy(stockframe=stockframe,
                                 portfolio=portfolio,
                                 indicator_client=indicator_client,
                                 existing_orders=existing_orders,
                                 short_period=short_period,
                                 long_period=long_period)

    buy_sell_signals = strategy_client.calculate_buy_sell_signals()
    assert len(buy_sell_signals['buys']) > 0

    short_period = 20
    long_period = 50
    short_period_indicator = 'ema_' + str(short_period)
    long_period_indicator = 'ema_' + str(long_period)

    historical_quotes = [{
        'time_key': '2022-08-19 10:30:00',
        'code': 'HK.00002',
        'open': 64.6,
        'close': 61.6,
        'high': 70.6,
        'low': 60.1,
        'volume': 30600,
        short_period_indicator: 60.0,
        long_period_indicator: 50.0
    }]
    stockframe = futubot.create_stockframe(data=historical_quotes)

    indicator_client = Indicators(stockframe=stockframe)
    existing_orders = {'HK.00002': False}

    strategy_client = MAStrategy(stockframe=stockframe,
                                 portfolio=portfolio,
                                 indicator_client=indicator_client,
                                 existing_orders=existing_orders,
                                 short_period=short_period,
                                 long_period=long_period,
                                 is_ema=True)

    buy_sell_signals = strategy_client.calculate_buy_sell_signals()
    assert len(buy_sell_signals['buys']) > 0

    futubot.close_quote_context()
    futubot.close_trade_context()


def test_macd_crossover_strategy():
    futubot = Robot(
        host='127.0.0.1',
        port=11111,
        filter_trdmarket=TrdMarket.HK,
        security_firm=SecurityFirm.FUTUSECURITIES,
        paper_trading=True,
    )

    # stocks_of_interest must be a stock not currently held.
    portfolio = futubot.create_portfolio(stocks_of_interest=['HK.00002'])

    historical_quotes = [{
        'time_key': '2022-08-19 10:30:00',
        'code': 'HK.00002',
        'open': 64.6,
        'close': 61.6,
        'high': 70.6,
        'low': 60.1,
        'volume': 30600,
        'macd': 34.0,
        'signal': 23.0
    }]
    stockframe = futubot.create_stockframe(data=historical_quotes)

    indicator_client = Indicators(stockframe=stockframe)
    existing_orders = {'HK.00002': False}

    strategy_client = MACDCrossOverStrategy(stockframe=stockframe,
                                            portfolio=portfolio,
                                            indicator_client=indicator_client,
                                            existing_orders=existing_orders)

    buy_sell_signals = strategy_client.calculate_buy_sell_signals()
    assert len(buy_sell_signals['buys']) > 0

    futubot.close_quote_context()
    futubot.close_trade_context()


def test_bollinger_bands_strategy():
    futubot = Robot(
        host='127.0.0.1',
        port=11111,
        filter_trdmarket=TrdMarket.HK,
        security_firm=SecurityFirm.FUTUSECURITIES,
        paper_trading=True,
    )

    # stocks_of_interest must be a stock not currently held.
    portfolio = futubot.create_portfolio(stocks_of_interest=['HK.00002'])

    historical_quotes = [{
        'time_key': '2022-08-19 10:30:00',
        'code': 'HK.00002',
        'open': 64.6,
        'close': 61.6,
        'high': 70.6,
        'low': 60.1,
        'volume': 30600,
        'sma': 63.5,
        'upper_band': 65.0,
        'lower_band': 62.0
    }]
    stockframe = futubot.create_stockframe(data=historical_quotes)

    indicator_client = Indicators(stockframe=stockframe)
    existing_orders = {'HK.00002': False}

    strategy_client = BollingerBandsStrategy(stockframe=stockframe,
                                             portfolio=portfolio,
                                             indicator_client=indicator_client,
                                             existing_orders=existing_orders)

    buy_sell_signals = strategy_client.calculate_buy_sell_signals()
    assert len(buy_sell_signals['buys']) > 0

    futubot.close_quote_context()
    futubot.close_trade_context()
