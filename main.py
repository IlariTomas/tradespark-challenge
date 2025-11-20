
import backtrader as bt
import datetime
import yfinance as yf 
from strategy import MultiStrategy

if __name__ == '__main__':
    cerebro = bt.Cerebro()

    cerebro.addstrategy(MultiStrategy)

    tickers = ['MSFT', 'GOOG', 'AAPL', 'TSLA']

    for ticker in tickers:
        data = bt.feeds.PandasData(dataname=yf.download(ticker, start='2021-01-01', end='2021-12-31', multi_level_index=False))
        cerebro.adddata(data, name=ticker)

    cerebro.broker.setcash(100000.0)
    print(f'Valor Inicial del Portafolio: {cerebro.broker.getvalue():.2f}')
    results = cerebro.run()
    print(f'Valor Final del Portafolio: {cerebro.broker.getvalue():.2f}')