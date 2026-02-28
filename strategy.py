import pandas as pd
from alpaca.data.historical import StockHistoricalDataClient, CryptoHistoricalDataClient
from alpaca.data.requests import StockBarsRequest, CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from logger import get_logger
from config import API_KEY, SECRET_KEY
from visualization import Visualizer

logger = get_logger(__name__)

class Strategy:
    def __init__(self, trading_client):
        self.client = trading_client
        # Initialize data clients
        self.stock_data_client = StockHistoricalDataClient(API_KEY, SECRET_KEY)
        self.crypto_data_client = CryptoHistoricalDataClient(API_KEY, SECRET_KEY)
        self.visualizer = Visualizer()
        
        self.symbols = ['SPY', 'BTC/USD']
        self.timeframe = TimeFrame(1, TimeFrameUnit.Minute)
        self.sma_short = 10
        self.sma_long = 30
        self.position_limit = 5
        self.order_size_usd = 100

    def get_bars(self, symbol):
        """Fetches historical bars for a stock or crypto symbol."""
        if '/' in symbol: # It's a crypto pair
            request_params = CryptoBarsRequest(
                symbol_or_symbols=[symbol],
                timeframe=self.timeframe,
                limit=self.sma_long + 5 # Fetch enough data for the longest SMA
            )
            bars = self.crypto_data_client.get_crypto_bars(request_params)
        else: # It's a stock
            request_params = StockBarsRequest(
                symbol_or_symbols=[symbol],
                timeframe=self.timeframe,
                limit=self.sma_long + 5
            )
            bars = self.stock_data_client.get_stock_bars(request_params)
        
        return bars.df

    def check_crossover(self, df):
        """Checks for an SMA crossover."""
        if len(df) < self.sma_long:
            return None # Not enough data

        df['sma_short'] = df['close'].rolling(window=self.sma_short).mean()
        df['sma_long'] = df['close'].rolling(window=self.sma_long).mean()

        # Check for crossover on the last two candles
        sma_short_prev = df['sma_short'].iloc[-2]
        sma_long_prev = df['sma_long'].iloc[-2]
        sma_short_curr = df['sma_short'].iloc[-1]
        sma_long_curr = df['sma_long'].iloc[-1]

        if pd.isna(sma_short_prev) or pd.isna(sma_long_prev):
            return None # SMA not calculated yet

        if sma_short_prev < sma_long_prev and sma_short_curr > sma_long_curr:
            return 'buy' # Golden cross
        elif sma_short_prev > sma_long_prev and sma_short_curr < sma_long_curr:
            return 'sell' # Death cross
        
        return None

    def run(self):
        """
        Implement your trading logic here.
        This method is called every 60 seconds by the main bot loop.
        """
        logger.info("Running SMA Crossover strategy...")
        
        try:
            positions = self.client.get_all_positions()
            existing_positions_symbols = [p.symbol for p in positions]
            
            for symbol in self.symbols:
                logger.info(f"Analyzing {symbol}...")
                
                # 1. Get historical data
                bars_df = self.get_bars(symbol)
                if bars_df.empty:
                    logger.warning(f"No data for {symbol}, skipping.")
                    continue
                
                # 2. Check for signal
                signal = self.check_crossover(bars_df)
                if signal == 'buy':
                    self.visualizer.plot_crossover(bars_df, symbol, signal)
                    logger.info(f"Buy signal for {symbol}.")
                    # 3. Check position limit and if we already have a position
                    if len(positions) >= self.position_limit:
                        logger.warning(f"Position limit of {self.position_limit} reached. Cannot open new position for {symbol}.")
                        continue
                    if symbol in existing_positions_symbols:
                        logger.info(f"Already have a position in {symbol}, not buying again.")
                        continue
                        
                    # 4. Place buy order
                    logger.info(f"Placing ${self.order_size_usd} market buy order for {symbol}.")
                    try:
                        market_order_data = MarketOrderRequest(
                            symbol=symbol,
                            notional=self.order_size_usd,
                            side=OrderSide.BUY,
                            time_in_force=TimeInForce.GTC
                        )
                        self.client.submit_order(order_data=market_order_data)
                        logger.info(f"Market buy order for {symbol} submitted successfully.")
                    except Exception as e:
                        logger.error(f"Failed to submit buy order for {symbol}: {e}")

                elif signal == 'sell':
                    self.visualizer.plot_crossover(bars_df, symbol, signal)
                    logger.info(f"Sell signal for {symbol}.")
                    # 5. Check if we have a position to sell
                    if symbol not in existing_positions_symbols:
                        logger.info(f"No position in {symbol} to sell.")
                        continue
                    
                    # 6. Place sell order (close position)
                    logger.info(f"Closing position for {symbol}.")
                    try:
                        self.client.close_position(symbol)
                        logger.info(f"Position for {symbol} closed successfully.")
                    except Exception as e:
                        logger.error(f"Failed to close position for {symbol}: {e}")
                else:
                    logger.info(f"No signal for {symbol}.")

        except Exception as e:
            logger.error(f"Error running strategy: {e}")