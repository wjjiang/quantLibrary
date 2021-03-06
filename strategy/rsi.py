if __name__ == '__main__':
    import sys
    sys.path.append("..")
    from pyalgotrade import bar
    from pyalgotrade import plotter

from pyalgotrade import strategy
from pyalgotrade.talibext import indicator
from pyalgotrade.technical import rsi

class RSIReversal(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, rsiPeriod):
        strategy.BacktestingStrategy.__init__(self, feed)
        self.__instrument = instrument
        self.__position = None
        # We'll use adjusted close values instead of regular close values.
        self.setUseAdjustedValues(True)
        self.__prices = feed[instrument].getPriceDataSeries()
        self.__position = None
        self.__rsiPeriod = int(rsiPeriod)
        self.__rsi = indicator.RSI(self.__prices, self.__rsiPeriod)
        #self.__rsi = rsi.RSI(self.__prices, self.__rsiPeriod)

    def getRSI(self):
        return self.__rsi

    def onEnterCanceled(self, position):
        self.__position = None

    def onExitOk(self, position):
        self.__position = None

    def onExitCanceled(self, position):
        # If the exit was canceled, re-submit it.
        self.__position.exitMarket()

    def onBars(self, bars):
        # If a position was not opened, check if we should enter a long position.
        if self.__rsi[-1] is None:
            return

        if self.__position is not None:
             if not self.__position.exitActive() and self.__rsi[-1] > 80:
                self.__position.exitMarket()

        if self.__position is None:
            if self.__rsi[-1] < 20:
                shares = int(self.getBroker().getCash() * 0.9 / bars[self.__instrument].getPrice())
                # Enter a buy market order. The order is good till canceled.
                self.__position = self.enterLong(self.__instrument, shares, True)
                print bars[self.__instrument].getDateTime(), bars[self.__instrument].getPrice()


if __name__ == "__main__":
    strat = RSIReversal
    instrument = '510180.SH'
    fromDate = '20100416'
    toDate = '20150717'
    period = 6
    plot = True

#############################################don't change ############################33
    import utility.windutility as wu
    from utility import dataframefeed

    data = wu.wsd(instrument, 'open, high, low, close, volume, adjfactor', fromDate, toDate)
    data['adjclose'] = data['close'] * data['adjfactor'] / data['adjfactor'][-1]
    feed = dataframefeed.Feed()
    feed.addBarsFromDataFrame(instrument, data)
    strat = strat(feed, instrument, period)

    if plot:
            plt = plotter.StrategyPlotter(strat, True, True, True)
           # rsi = strat.getRSI()
#          #  print type(ma1)
            # plt.getInstrumentSubplot('indicator').addDataSeries("rsi", rsi)
            # position = strat.getTest()
            # plt.getOrCreateSubplot("position").addDataSeries("position", position)

    strat.run()

    if plot:
        plt.plot()