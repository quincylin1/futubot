cfg = dict(account=dict(filter_trdmarket='TrdMarket.HK',
                        host='127.0.0.1',
                        port=11111,
                        security_firm='SecurityFirm.FUTUSECURITIES',
                        paper_trading=True,
                        password='******',
                        order_type='limit'),
           stocks_of_interest=['HK.00700', 'HK.09988'],
           historical_quote_dates=dict(start_date='2022-08-08 9:30:00',
                                       end_date='2022-08-08 9:30:00'),
           indicators=dict(rsi=dict(periods=14)),
           strategy=dict(name='RSIStrategy', params=dict()))
