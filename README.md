# Alpaca Trading Bot

This project is a Python-based algorithmic trading bot that uses the [Alpaca API](https://alpaca.markets/) to execute trades. It is designed with a modular structure that separates concerns like configuration, strategy, logging, and risk management, making it easy to extend and maintain.

## Features

- **Modular Architecture**: Core components are separated into distinct modules (`config.py`, `bot.py`, `strategy.py`, `logger.py`, `risk_management.py`).
- **SMA Crossover Strategy**: Implements a Simple Moving Average (SMA) crossover strategy to generate buy and sell signals.
- **Multi-Asset Trading**: Capable of trading both stocks (e.g., SPY) and cryptocurrencies (e.g., BTC/USD).
- **Risk Management**: Includes a daily drawdown limit and a trailing stop loss on all positions to manage risk.
- **Data Visualization**: Automatically generates and saves candlestick charts for each trade, visualizing the price action and SMA indicators.
- **Resilient Background Service**: Designed to run continuously, with error handling and a graceful shutdown mechanism.
- **Paper Trading by Default**: Safely runs in Alpaca's paper trading environment by default.

## Getting Started

### Prerequisites

- Python 3.7+
- An [Alpaca Paper Trading Account](https://app.alpaca.markets/signup)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/alpaca-trader.git
    cd alpaca-trader
    ```

2.  **Create a virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Configuration

This bot uses environment variables for configuration. You will need to set up your Alpaca API keys.

1.  **Find your API Keys**: Log in to your Alpaca account and navigate to the API Keys section.

2.  **Set Environment Variables**: Add your API Key ID and Secret Key to your shell's configuration file (e.g., `.zshrc`, `.bash_profile`).

    ```bash
    echo 'export APCA_API_KEY_ID="YOUR_PAPER_API_KEY"' >> ~/.zshrc
    echo 'export APCA_API_SECRET_KEY="YOUR_PAPER_SECRET_KEY"' >> ~/.zshrc
    ```

3.  **Reload your shell**: 
    ```bash
    source ~/.zshrc
    ```

## Usage

To start the trading bot, simply run `bot.py`:

```bash
python bot.py
```

The bot will start running, and you will see log messages in your console and in the `trading_log.txt` file. Any charts generated will be saved in the `charts/` directory.

To stop the bot, press `Ctrl+C`. The bot will perform a graceful shutdown, canceling any open orders.

## Disclaimer

This project is for educational purposes only. Automated trading carries significant risks, and you should not use this bot for live trading without a thorough understanding of the code and the risks involved.
