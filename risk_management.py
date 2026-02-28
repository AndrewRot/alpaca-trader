from alpaca.trading.requests import TrailingStopOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from logger import get_logger

logger = get_logger(__name__)

class RiskManager:
    def __init__(self, trading_client):
        self.client = trading_client
        self.daily_drawdown_limit = -0.05  # 5% drop
        self.trailing_stop_pct = 0.02  # 2% trail
        self.initial_portfolio_value = None

    def track_daily_drawdown(self):
        """Monitors the account for a significant daily loss."""
        account = self.client.get_account()
        current_value = float(account.portfolio_value)

        if self.initial_portfolio_value is None:
            # Set the initial value at the start of the trading day (or bot start)
            self.initial_portfolio_value = float(account.last_equity)
            logger.info(f"Initial portfolio value set to: ${self.initial_portfolio_value}")
            return True # Continue trading

        portfolio_change_pct = (current_value - self.initial_portfolio_value) / self.initial_portfolio_value

        if portfolio_change_pct <= self.daily_drawdown_limit:
            logger.critical("Daily drawdown limit reached! Halting all trading activities.")
            logger.critical(f"Initial Value: ${self.initial_portfolio_value}, Current Value: ${current_value}, Loss: {portfolio_change_pct:.2%}")
            # In a real-world scenario, you might want to close all positions and notify someone.
            self.client.close_all_positions(cancel_orders=True)
            logger.info("All positions have been liquidated and orders canceled.")
            return False # Stop trading
        
        return True # Continue trading

    def manage_trailing_stops(self):
        """Creates or updates trailing stop orders for all open positions."""
        open_positions = self.client.get_all_positions()
        existing_orders = self.client.get_orders()
        
        for position in open_positions:
            # Check if there is already a trailing stop for this position
            has_trailing_stop = any(
                o.side == OrderSide.SELL and 
                o.symbol == position.symbol and 
                o.type == 'trailing_stop' 
                for o in existing_orders
            )
            
            if not has_trailing_stop:
                logger.info(f"No trailing stop found for {position.symbol}. Creating one.")
                try:
                    trailing_stop_order_data = TrailingStopOrderRequest(
                        symbol=position.symbol,
                        qty=position.qty,
                        side=OrderSide.SELL,
                        time_in_force=TimeInForce.GTC,
                        trail_percent=self.trailing_stop_pct * 100  # SDK expects percentage points
                    )
                    self.client.submit_order(order_data=trailing_stop_order_data)
                    logger.info(f"Trailing stop order for {position.symbol} submitted with a {self.trailing_stop_pct:.2%} trail.")
                except Exception as e:
                    logger.error(f"Failed to submit trailing stop for {position.symbol}: {e}")
    
    def run(self):
        """Main risk management loop."""
        logger.info("Running risk management checks...")
        
        # 1. Check for major drawdown
        if not self.track_daily_drawdown():
            return False # Signal to stop the bot
            
        # 2. Manage trailing stops for all positions
        self.manage_trailing_stops()
        
        return True # All good, continue trading