import pytest 

from futu import RET_OK, ModifyOrderOp, SecurityFirm, TrdMarket

from futubot.portfolio import Portfolio
from futubot.robot import Robot


def test_get_portfolio_info():
    futubot = Robot(
        host='127.0.0.1',
        port=11111,
        filter_trdmarket=TrdMarket.HK,
        security_firm=SecurityFirm.FUTUSECURITIES,
        paper_trading=True,
    )

    portfolio = futubot.create_portfolio(
        stocks_of_interest=['HK.00700']
    )

    portfolio_info = portfolio.get_portfolio_info()

    assert isinstance(portfolio_info, dict)

    for key in ['total_assets', 'total_market_value', 'cash', 'total_invested_value', 'today_pnl_value']:
        assert (key in portfolio_info)

    futubot.close_quote_context()
    futubot.close_trade_context()

def test_calculate_portfolio_weights():
    futubot = Robot(
        host='127.0.0.1',
        port=11111,
        filter_trdmarket=TrdMarket.HK,
        security_firm=SecurityFirm.FUTUSECURITIES,
        paper_trading=True,
    )

    portfolio = futubot.create_portfolio(
        stocks_of_interest=['HK.00700']
    )

    weights = portfolio.calculate_portfolio_weights()
    assert isinstance(weights, dict)

    futubot.close_quote_context()
    futubot.close_trade_context()

def test_calculate_portfolio_metrics():
    futubot = Robot(
        host='127.0.0.1',
        port=11111,
        filter_trdmarket=TrdMarket.HK,
        security_firm=SecurityFirm.FUTUSECURITIES,
        paper_trading=True,
    )

    code = 'HK.00700'
    portfolio = futubot.create_portfolio(
        stocks_of_interest=[code]
    )

    portfolio_metrics = portfolio.calculate_portfolio_metrics()

    for key in ['weight', 'average_returns', 'weighted_returns', 'standard_deviation_of_returns', 'variance_of_returns', 'covariance_of_returns']:
        assert key in portfolio_metrics[code]

    for key in ['variance', 'average_returns', 'annualized_sharpe_ratio']:
        assert key in portfolio_metrics['portfolio']

    futubot.close_quote_context()
    futubot.close_trade_context()





