import mplfinance as mpf
import pandas as pd
from datetime import datetime
import os
from logger import get_logger

logger = get_logger(__name__)

class Visualizer:
    def __init__(self, output_dir='charts'):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def plot_crossover(self, df, symbol, signal):
        """
        Generates and saves a candlestick chart with SMA crossovers.
        """
        try:
            if df.empty or len(df) < 2:
                logger.warning(f"Not enough data to plot for {symbol}.")
                return

            # Ensure the DataFrame index is a DatetimeIndex
            if not isinstance(df.index, pd.DatetimeIndex):
                df.index = pd.to_datetime(df.index)

            # Prepare additional plots for the SMAs
            ap = [
                mpf.make_addplot(df['sma_short'], color='blue', width=0.7),
                mpf.make_addplot(df['sma_long'], color='orange', width=0.7),
            ]

            # Create a title and filename
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            chart_title = f'{symbol} SMA Crossover ({signal.upper()}) - {timestamp}'
            filename = os.path.join(self.output_dir, f'{symbol}_{signal}_crossover_{timestamp}.png')

            # Generate the plot
            mpf.plot(
                df,
                type='candle',
                style='yahoo',
                title=chart_title,
                ylabel='Price ($)',
                addplot=ap,
                volume=True,
                ylabel_lower='Volume',
                savefig=filename
            )
            logger.info(f"Chart saved to {filename}")

        except Exception as e:
            logger.error(f"Error generating plot for {symbol}: {e}")
