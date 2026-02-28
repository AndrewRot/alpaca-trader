import requests
from config import API_KEY, SECRET_KEY, BASE_URL
from logger import get_logger

logger = get_logger(__name__)

def get_most_active_stocks():
    """
    Fetches the top 20 most active stocks from the Alpaca screener API.
    We use the "most active" as a proxy for volatility.
    """
    try:
        # Note: This uses the v1beta1 screener endpoint.
        # The data API URL is the same for live and paper trading, so we adjust the base URL accordingly.
        screener_base_url = BASE_URL.replace('paper-', '').replace('api.', 'data.')
        url = f"{screener_base_url}/v1beta1/screener/stocks/most-actives?top=20"
        headers = {
            "APCA-API-KEY-ID": API_KEY,
            "APCA-API-SECRET-KEY": SECRET_KEY
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status() # Raise an exception for bad status codes
        
        data = response.json()
        
        if 'most_actives' not in data or not data['most_actives']:
            logger.warning("No most active stocks found in API response.")
            return []
            
        symbols = [stock['symbol'] for stock in data['most_actives']]
        logger.info(f"Fetched top 20 most active stocks: {symbols}")
        return symbols

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching most active stocks: {e}")
        return []
    except Exception as e:
        logger.error(f"An unexpected error occurred in get_most_active_stocks: {e}")
        return []
