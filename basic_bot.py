# basic_bot.py
import time
import hmac
import hashlib
import requests
from urllib.parse import urlencode
from logger_config import get_logger

logger = get_logger("BasicBot")

class BasicBot:
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True, base_url: str = None):
        self.api_key = api_key
        self.api_secret = api_secret.encode("utf-8")
        self.testnet = testnet
        self.base_url = base_url or ("https://testnet.binancefuture.com" if testnet else "https://fapi.binance.com")
        self.session = requests.Session()
        self.session.headers.update({"X-MBX-APIKEY": self.api_key})
        logger.debug("Initialized BasicBot with base_url=%s", self.base_url)

    def _sign(self, params: dict) -> dict:
        params = params.copy()
        params["timestamp"] = int(time.time() * 1000)
        query_string = urlencode(params)
        signature = hmac.new(self.api_secret, query_string.encode("utf-8"), hashlib.sha256).hexdigest()
        params["signature"] = signature
        return params

    def _post(self, path: str, params: dict):
        url = self.base_url.rstrip("/") + path
        signed = self._sign(params)
        logger.debug("POST %s | params=%s", url, {k: signed[k] for k in signed if k != "signature"})
        try:
            resp = self.session.post(url, data=signed, timeout=10)
            logger.info("Response %s | status=%s", url, resp.status_code)
            logger.debug("Response body: %s", resp.text)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.exception("Error posting to %s: %s", url, e)
            raise

    def _get(self, path: str, params: dict = None):
        url = self.base_url.rstrip("/") + path
        params = params or {}
        signed = self._sign(params)
        logger.debug("GET %s | params=%s", url, {k: signed[k] for k in signed if k != "signature"})
        try:
            resp = self.session.get(url, params=signed, timeout=10)
            logger.info("Response %s | status=%s", url, resp.status_code)
            logger.debug("Response body: %s", resp.text)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.exception("Error getting %s: %s", url, e)
            raise

    def validate_symbol(self, symbol: str) -> str:
        if not symbol or not isinstance(symbol, str):
            raise ValueError("Symbol must be a non-empty string, e.g. 'BTCUSDT'")
        return symbol.strip().upper()

    def validate_side(self, side: str) -> str:
        s = side.strip().upper()
        if s not in {"BUY", "SELL"}:
            raise ValueError("side must be BUY or SELL")
        return s

    def validate_order_type(self, order_type: str) -> str:
        t = order_type.strip().upper()
        if t not in {"MARKET", "LIMIT", "STOP"}:
            raise ValueError("order_type must be MARKET, LIMIT, or STOP")
        return t

    def place_market_order(self, symbol: str, side: str, quantity: float, reduceOnly: bool = False):
        symbol = self.validate_symbol(symbol)
        side = self.validate_side(side)
        if quantity <= 0:
            raise ValueError("quantity must be > 0")
        params = {
            "symbol": symbol,
            "side": side,
            "type": "MARKET",
            "quantity": str(quantity),
            "reduceOnly": str(reduceOnly).lower()
        }
        return self._post("/fapi/v1/order", params)

    def place_limit_order(self, symbol: str, side: str, quantity: float, price: float, timeInForce: str = "GTC", reduceOnly: bool = False):
        symbol = self.validate_symbol(symbol)
        side = self.validate_side(side)
        if quantity <= 0 or price <= 0:
            raise ValueError("quantity and price must be > 0")
        params = {
            "symbol": symbol,
            "side": side,
            "type": "LIMIT",
            "quantity": str(quantity),
            "price": str(price),
            "timeInForce": timeInForce,
            "reduceOnly": str(reduceOnly).lower()
        }
        return self._post("/fapi/v1/order", params)

    def place_stop_limit_order(self, symbol: str, side: str, quantity: float, stopPrice: float, price: float, timeInForce: str = "GTC"):
        symbol = self.validate_symbol(symbol)
        side = self.validate_side(side)
        if quantity <= 0 or stopPrice <= 0 or price <= 0:
            raise ValueError("quantity, stopPrice and price must be > 0")
        params = {
            "symbol": symbol,
            "side": side,
            "type": "STOP",
            "quantity": str(quantity),
            "stopPrice": str(stopPrice),
            "price": str(price),
            "timeInForce": timeInForce
        }
        return self._post("/fapi/v1/order", params)

    def ping(self):
        url = self.base_url.rstrip("/") + "/fapi/v1/ping"
        logger.debug("Ping %s", url)
        resp = self.session.get(url, timeout=5)
        logger.info("Ping status %s", resp.status_code)
        resp.raise_for_status()
        return resp.status_code == 200

    def get_server_time(self):
        return self._get("/fapi/v1/time", {})
