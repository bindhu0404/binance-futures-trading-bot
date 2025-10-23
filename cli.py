# cli.py
import argparse
import os
from dotenv import load_dotenv
from basic_bot import BasicBot
from logger_config import get_logger
from colorama import Fore, Style, init  

init(autoreset=True)
logger = get_logger("cli")

def parse_args():
    p = argparse.ArgumentParser(description="Simple Binance Futures Testnet trading CLI")
    p.add_argument("--symbol", required=False, help="Trading pair e.g. BTCUSDT")
    p.add_argument("--side", required=False, choices=["BUY", "SELL"], help="BUY or SELL")
    p.add_argument("--type", required=False, choices=["MARKET", "LIMIT", "STOP"], help="Order type")
    p.add_argument("--quantity", required=False, type=float, help="Quantity to trade")
    p.add_argument("--price", type=float, help="Price for LIMIT or STOP-LIMIT order")
    p.add_argument("--stopPrice", type=float, help="Stop price for STOP-LIMIT")
    p.add_argument("--api_key", help="Binance API key (or set in .env)")
    p.add_argument("--api_secret", help="Binance API secret (or set in .env)")
    p.add_argument("--testnet", action="store_true", default=True, help="Use testnet (default True)")
    p.add_argument("--check-orders", action="store_true", help="Check all orders for the symbol")
    p.add_argument("--balance", action="store_true", help="Check account balance") 
    return p.parse_args()

def prompt_if_missing(args):
    # Only ask for inputs if we're placing an order
    if not args.check_orders and not args.balance:
        if not args.symbol:
            args.symbol = input("Enter symbol (e.g. BTCUSDT): ").strip()
        if not args.side:
            args.side = input("Enter side (BUY/SELL): ").strip().upper()
        if not args.type:
            args.type = input("Enter type (MARKET/LIMIT/STOP): ").strip().upper()
        if args.quantity is None:
            args.quantity = float(input("Enter quantity: ").strip())
        if args.type == "LIMIT" and args.price is None:
            args.price = float(input("Enter price for LIMIT order: ").strip())
        if args.type == "STOP" and args.stopPrice is None:
            args.stopPrice = float(input("Enter stopPrice for STOP order: ").strip())
        if args.type == "STOP" and args.price is None:
            args.price = float(input("Enter limit price for STOP-LIMIT order: ").strip())
    return args

def main():
    args = parse_args()
    load_dotenv()
    api_key = args.api_key or os.getenv("BINANCE_API_KEY")
    api_secret = args.api_secret or os.getenv("BINANCE_API_SECRET")

    if not api_key or not api_secret:
        logger.error("API key and secret are required (pass via args or .env)")
        return

    args = prompt_if_missing(args)
    bot = BasicBot(api_key, api_secret, testnet=args.testnet)

    try:
        bot.ping()
    except Exception as e:
        logger.error("Failed to reach testnet: %s", e)
        return

    if args.balance:
        try:
            res = bot._get("/fapi/v2/balance")
            print(Fore.CYAN + "\n Account Balance:")
            for item in res:
                print(f"{item['asset']}: {item['balance']}")
        except Exception as e:
            logger.exception("Failed to fetch balance: %s", e)
        return

   
    if args.check_orders:
        try:
            orders = bot._get("/fapi/v1/allOrders", {"symbol": args.symbol})
            print(Fore.YELLOW + f"\n Order History for {args.symbol}")
            for o in orders[-5:]:
                print(f"- ID: {o['orderId']}, Side: {o['side']}, Type: {o['type']}, Status: {o['status']}")
        except Exception as e:
            logger.exception("Failed to fetch orders: %s", e)
        return

    
    try:
        if args.type == "MARKET":
            res = bot.place_market_order(args.symbol, args.side, args.quantity)
        elif args.type == "LIMIT":
            res = bot.place_limit_order(args.symbol, args.side, args.quantity, args.price)
        elif args.type == "STOP":
            res = bot.place_stop_limit_order(args.symbol, args.side, args.quantity, args.stopPrice, args.price)
        else:
            raise ValueError("Unknown order type")

        logger.info("Order result: %s", res)
        print(Fore.GREEN + "\nOrder placed successfully!" + Style.RESET_ALL)
        print(Fore.MAGENTA + "\nOrder Details:")
        for k, v in res.items():
            print(f"{k}: {v}")

    except Exception as e:
        logger.exception("Order failed: %s", e)

if __name__ == "__main__":
    main()
