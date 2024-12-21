import backtrader as bt


class TestStrategy(bt.Strategy):
    params = (
        ("sma_period", 50),
        ("rsi_period", 14),
    )

    def __init__(self):
        self.sma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.sma_period
        )
        self.rsi = bt.indicators.RSI(self.data.close, period=self.params.rsi_period)

    def next(self):
        if self.rsi < 30 and self.data.close[0] > self.sma[0]:
            self.buy()
        elif self.rsi > 70 and self.data.close[0] < self.sma[0]:
            self.sell()
