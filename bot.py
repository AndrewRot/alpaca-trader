import time
import sys
from alpaca.trading.client import TradingClient
from config import API_KEY, SECRET_KEY, PAPER_TRADING
from logger import get_logger
from strategy import Strategy
from risk_management import RiskManager

logger = get_logger(__name__)

def main():
    logger.info("Starting trading bot...")

    trading_client = TradingClient(API_KEY, SECRET_KEY, paper=PAPER_TRADING)

    try:
        account = trading_client.get_account()
        if account.trading_blocked:
            logger.error('Account is currently restricted from trading.')
            return
        logger.info(f'${account.cash} is available as buying power.')
    except Exception as e:
        logger.error(f"Failed to connect to Alpaca: {e}")
        return

    trading_strategy = Strategy(trading_client)
    risk_manager = RiskManager(trading_client)

    try:
        while True:
            try:
                logger.info("Heartbeat...")
                
                # Run risk management first
                if not risk_manager.run():
                    logger.critical("Risk management checks failed. Stopping bot.")
                    break # Exit the main loop
                
                # If risk management is fine, run the trading strategy
                trading_strategy.run()
                
            except Exception as e:
                logger.error(f"An error occurred in the main loop: {e}")
                logger.info("Retrying in 30 seconds...")
                time.sleep(30)
                continue

            time.sleep(15)
            
    except KeyboardInterrupt:
        logger.info("Bot shutting down...")
        try:
            trading_client.cancel_orders()
            logger.info("All pending orders have been canceled.")
        except Exception as e:
            logger.error(f"Error canceling orders during shutdown: {e}")
        sys.exit(0)

if __name__ == "__main__":
    main()
