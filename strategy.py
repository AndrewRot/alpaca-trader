import pandas as pd
from alpaca.data.historical import StockHistoricalDataClient, CryptoHistoricalDataClient
from alpaca.data.requests import StockBarsRequest, CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from logger import get_logger
from config import API_KEY, SECRET_KEY
from visualization import Visualizer
from market_scanner import get_most_active_stocks
from datetime import datetime, timedelta
import trade_config as tc

logger = get_logger(__name__)

class Strategy:
    def __init__(self, trading_client):
        self.client = trading_client
        self.stock_data_client = StockHistoricalDataClient(API_KEY, SECRET_KEY)
        self.crypto_data_client = CryptoHistoricalDataClient(API_KEY, SECRET_KEY)
        self.visualizer = Visualizer()
        
        # --- Load Configuration ---
        self.timeframe = tc.TIME_FRAME
        self.sma_short = tc.SMA_SHORT_WINDOW
        self.sma_long = tc.SMA_LONG_WINDOW
        self.position_limit = tc.POSITION_LIMIT
        self.order_size_usd = tc.ORDER_SIZE_USD
        
        # --- Initialize Symbol Universe ---
        self.symbols = []
        self.initialize_symbols()

    def initialize_symbols(self):
        """Initializes the list of symbols to trade."""
        logger.info("Initializing symbol list...")
        static_symbols = tc.STATIC_SYMBOLS
        dynamic_symbols = []
        
        if tc.DYNAMIC_SYMBOLS_ENABLED:
            logger.info("Fetching most active stocks...")
            dynamic_symbols = get_most_active_stocks()
        
        # Combine and deduplicate symbols
        self.symbols = list(set(static_symbols + dynamic_symbols))
        logger.info(f"Trading symbols: {self.symbols}")

    def get_bars(self, symbol):
        """Fetches historical bars for a stock or crypto symbol."""
        # We're setting start time to a few days ago to avoid issues with free data delays
        start_time = datetime.now() - timedelta(days=60)
        if '/' in symbol:
            request_params = CryptoBarsRequest(
                symbol_or_symbols=[symbol],
                timeframe=self.timeframe,
                start=start_time
            )
            bars = self.crypto_data_client.get_crypto_bars(request_params)
        else:
            request_params = StockBarsRequest(
                symbol_or_symbols=[symbol],
                timeframe=self.timeframe,
                feed='iex',  # Use IEX for free data
                start=start_time
            )
            logger.info(f"Requesting stock bars for {symbol} with params: {request_params}")
            bars = self.stock_data_client.get_stock_bars(request_params)
            logger.info(f"Received {len(bars.df)} bars for {symbol}")
        return bars.df

    def check_crossover(self, df):
        """Checks for an SMA crossover."""
        if len(df) < self.sma_long:
            return None

        df['sma_short'] = df['close'].rolling(window=self.sma_short).mean()
        df['sma_long'] = df['close'].rolling(window=self.sma_long).mean()

        sma_short_prev = df['sma_short'].iloc[-2]
        sma_long_prev = df['sma_long'].iloc[-2]
        sma_short_curr = df['sma_short'].iloc[-1]
        sma_long_curr = df['sma_long'].iloc[-1]

        if pd.isna(sma_short_prev) or pd.isna(sma_long_prev):
            return None

        if sma_short_prev < sma_long_prev and sma_short_curr > sma_long_curr:
            return 'buy'
        elif sma_short_prev > sma_long_prev and sma_short_curr < sma_long_curr:
            return 'sell'
        return None

    def run(self):
        """Main trading logic loop."""
        logger.info("Running SMA Crossover strategy...")
        
        try:
            positions = self.client.get_all_positions()
            existing_positions_symbols = [p.symbol for p in positions]
            
            for symbol in self.symbols:
                try:
                    asset = self.client.get_asset(symbol)
                    if not asset.tradable:
                        logger.warning(f"Symbol {symbol} is not tradable, skipping.")
                        continue
                except Exception as e:
                    logger.warning(f"Could not get asset for {symbol}, skipping: {e}")
                    continue

                logger.info(f"Analyzing {symbol}...")
                bars_df = self.get_bars(symbol)
                if bars_df.empty:
                    logger.warning(f"No data for {symbol}, skipping.")
                    continue
                
                logger.warning(f"Found bar data for {symbol}")
                signal = self.check_crossover(bars_df)
                
                if signal:
                    self.visualizer.plot_crossover(bars_df, symbol, signal, self.sma_short, self.sma_long)
                
                if signal == 'buy':
                    if len(positions) >= self.position_limit or symbol in existing_positions_symbols:
                        continue
                    try:
                        market_order_data = MarketOrderRequest(
                            symbol=symbol, notional=self.order_size_usd, side=OrderSide.BUY, time_in_force=TimeInForce.DAY
                        )
                        self.client.submit_order(order_data=market_order_data)
                        logger.info(f"Market buy order for {symbol} submitted.")
                    except Exception as e:
                        logger.error(f"Failed to submit buy order for {symbol}: {e}")

                elif signal == 'sell':
                    if symbol in existing_positions_symbols:
                        try:
                            self.client.close_position(symbol)
                            logger.info(f"Position for {symbol} closed.")
                        except Exception as e:
                            logger.error(f"Failed to close position for {symbol}: {e}")
        except Exception as e:
            logger.error(f"Error running strategy: {e}")
