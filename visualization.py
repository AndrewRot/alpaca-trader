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

    def plot_crossover(self, df, symbol, signal, sma_short, sma_long):
        """
        Generates and saves a candlestick chart with SMA crossover annotations.
        """
        try:
            df_plot = df.copy()
            # If the DataFrame has a multi-index, extract the timestamp index
            if isinstance(df_plot.index, pd.MultiIndex):
                df_plot.index = df_plot.index.get_level_values('timestamp')

            # Ensure the DataFrame index is a DatetimeIndex
            if not isinstance(df_plot.index, pd.DatetimeIndex):
                df_plot.index = pd.to_datetime(df_plot.index)

            # Find the crossover point (the last data point)
            crossover_time = df_plot.index[-1]
            crossover_price = df_plot['close'].iloc[-1]
            
            # Create descriptive title
            signal_desc = "Golden Cross" if signal == 'buy' else "Death Cross"
            title = (f'{symbol} ({df_plot.index.name}) - {signal_desc} Signal\n'
                    f'SMA({sma_short}) crosses {signal} SMA({sma_long}) at {crossover_time.strftime("%Y-%m-%d %H:%M")}')

            # Prepare SMA plots
            ap = [
                mpf.make_addplot(df_plot[f'sma_short'], color='blue', width=0.7),
                mpf.make_addplot(df_plot[f'sma_long'], color='orange', width=0.7),
            ]

            # Add an arrow indicating the crossover point
            crossover_marker = [crossover_price * 0.98] if signal == 'buy' else [crossover_price * 1.02]
            crossover_plot = mpf.make_addplot(pd.Series(crossover_marker, index=[crossover_time]), 
                                            type='scatter', 
                                            marker='^' if signal == 'buy' else 'v', 
                                            color='green' if signal == 'buy' else 'red', 
                                            markersize=100)
            ap.append(crossover_plot)

            # Generate and save the file
            filename = os.path.join(self.output_dir, f'{symbol.replace("/", "-")}.png')

            mpf.plot(
                df_plot,
                type='candle',
                style='yahoo',
                title=title,
                ylabel='Price ($)',
                addplot=ap,
                figsize=(15, 7),
                savefig=filename
            )
            logger.info(f'Saved visualization chart to {filename}')
        except Exception as e:
            logger.error(f'Error generating plot for {symbol}: {e}')
