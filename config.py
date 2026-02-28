
import os

# Alpaca API credentials
# It's recommended to use environment variables for security
API_KEY = os.getenv("APCA_API_KEY_ID", "")
SECRET_KEY = os.getenv("APCA_API_SECRET_KEY", "")

# Paper trading mode
# Set to True for paper trading, False for live trading
PAPER_TRADING = os.getenv("PAPER_TRADING", "True").lower() in ("true", "1", "t")

# Base URL for the API
# The SDK handles the paper/live URL based on the API key,
# but you can override it here if needed.
BASE_URL = "https://paper-api.alpaca.markets" if PAPER_TRADING else "https://api.alpaca.markets"

