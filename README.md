# Simplified Binance Futures Trading Bot

## Overview
This is a Python-based simplified trading bot for Binance Futures Testnet (USDT-M).  
The bot allows users to place **market, limit, and stop-limit orders** on a given trading pair. It supports both **buy and sell orders**, fetches account balance, and logs all API requests, responses, and errors.

---

## Features
- Place **market, limit, and stop-limit orders**.
- Support **BUY** and **SELL** sides.
- Fetch **account balance**.
- Check **order history** for a symbol.
- Logging of all API requests and responses.
- CLI interface with user-friendly prompts.
- Optional: Colored output for successful orders using `colorama`.

---

## Trading Pair
- Example: `BTCUSDT`  
  - **BTC** = Bitcoin  
  - **USDT** = Tether (USD stablecoin)  
  - Trading pair means buying or selling BTC using USDT.

---

## Requirements
- Python 3.10+
- Packages:
  - `requests`
  - `python-dotenv`
  - `colorama` (optional for colored CLI output)

Install dependencies with:
```bash
pip install -r requirements.txt
```

## Setup Instructions
1. Clone or create the project folder
git clone https://github.com/<yourusername>/primetrade-bot.git
cd primetrade-bot

2. Create a .env file

Inside your project folder, create a .env file and add your Binance Testnet API credentials:

BINANCE_API_KEY=your_testnet_api_key_here
BINANCE_API_SECRET=your_testnet_api_secret_here


## How to Run the Bot
1. Check connection to Binance Testnet
python cli.py --ping

2. Place a Market Order

Buy BTCUSDT
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

Sell BTCUSDT
```bash
python cli.py --symbol BTCUSDT --side SELL --type MARKET --quantity 0.001
```
3. Place a Limit Order
python cli.py --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.001 --price 105000

4. Place a Stop-Limit Order
python cli.py --symbol BTCUSDT --side SELL --type STOP --quantity 0.001 --stopPrice 108000 --price 107500


For a SELL STOP-LIMIT:

stopPrice = price that triggers the limit order

price = the actual limit order price (must be lower than stopPrice)

5. Check Account Balance
```bash
python cli.py --balance
```

6. View Order History
```bash
python cli.py --orders BTCUSDT
```

## Logging

All logs are automatically saved in:

logs/bot.log


The log file contains:

Timestamps

API endpoint requests and responses

Errors (if any)
