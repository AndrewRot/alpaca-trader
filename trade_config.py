"""
Trade Configuration for the High-Intensity Trading Bot

This file centralizes all the parameters and settings that control the trading strategy, 
making it easy to adjust the bot's behavior without modifying the core logic.
"""

from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from datetime import timedelta

# --- Trading Strategy Parameters ---

# Timeframe for historical data. This determines the granularity of the bars (e.g., 1 minute, 5 minutes, 1 day).
# Options: TimeFrame.Minute, TimeFrame.Hour, TimeFrame.Day
TIME_FRAME = TimeFrame(1, TimeFrameUnit.Minute)

# Short-term Simple Moving Average (SMA) window.
SMA_SHORT_WINDOW = 10

# Long-term Simple Moving Average (SMA) window.
SMA_LONG_WINDOW = 30


# --- Risk Management Parameters ---

# Maximum number of concurrent positions to hold.
POSITION_LIMIT = 5

# The notional size of each order in USD.
ORDER_SIZE_USD = 100


# --- Symbol Universe ---

# Static list of symbols to trade. These are always included in the trading universe.
# Can be a mix of stocks and crypto (e.g., 'SPY', 'BTC/USD').
STATIC_SYMBOLS = ['SPY', 'BTC/USD']

# --- Symbol Refresh Logic ---

# If set to True, the bot will fetch the most active stocks at startup.
# If False, it will only trade the STATIC_SYMBOLS.
DYNAMIC_SYMBOLS_ENABLED = True

# Determines how often the list of dynamic symbols is refreshed.
# For example, timedelta(hours=1) means the list is updated every hour.
# If you want to fetch the list only once at the beginning, you can set this to a very large value
# or adjust the logic in the strategy to only call it once.
# For this implementation, we will fetch once at startup and not refresh.
SYMBOL_REFRESH_INTERVAL = timedelta(days=365) 
