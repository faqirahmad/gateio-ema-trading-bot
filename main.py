import time import hmac import hashlib import requests import base64 import json from datetime import datetime

-------------- تنظیمات ربات ------------------

API_KEY = "اینجا API Key را بگذار" API_SECRET = "اینجا Secret را بگذار"

SYMBOL = "DOGE5L_USDT" INVEST_AMOUNT = 100  # سرمایه هر معامله

EMA_FAST = 9 EMA_SLOW = 21 RSI_PERIOD = 14

TA_INTERVAL = "15m"  # تایم‌فریم

---------------- توابع کمکی ------------------

def sign_request(secret, method, url, query_string, payload): timestamp = str(int(time.time() * 1000)) message = timestamp + method + url + query_string + payload signature = hmac.new(secret.encode(), message.encode(), hashlib.sha512).hexdigest() return timestamp, signature

def get_headers(api_key, api_secret, method, url, query_string="", payload=""): t, sig = sign_request(api_secret, method, url, query_string, payload) return { "KEY": api_key, "Timestamp": t, "SIGN": sig, "Content-Type": "application/json" }

---------------- تحلیل تکنیکال ------------------

def fetch_klines(): url = f"https://api.gateio.ws/api/v4/spot/candlesticks?currency_pair={SYMBOL}&interval={TA_INTERVAL}&limit=100" res = requests.get(url) data = res.json() closes = [float(x[2]) for x in data] return closes[::-1]  # از قدیم به جدید

def calculate_ema(prices, period): ema = [sum(prices[:period]) / period] k = 2 / (period + 1) for price in prices[period:]: ema.append(price * k + ema[-1] * (1 - k)) return ema

def calculate_rsi(prices, period): gains, losses = [], [] for i in range(1, len(prices)): change = prices[i] - prices[i - 1] if change > 0: gains.append(change) losses.append(0) else: gains.append(0) losses.append(-change) avg_gain = sum(gains[:period]) / period avg_loss = sum(losses[:period]) / period rsis = [] for i in range(period, len(prices)): gain = gains[i] loss = losses[i] avg_gain = (avg_gain * (period - 1) + gain) / period avg_loss = (avg_loss * (period - 1) + loss) / period rs = avg_gain / avg_loss if avg_loss != 0 else 0 rsis.append(100 - (100 / (1 + rs))) return rsis

---------------- ارسال سفارش خرید/فروش ------------------

def place_order(side): url = "/api/v4/spot/orders" full_url = "https://api.gateio.ws" + url body = { "currency_pair": SYMBOL, "type": "market", "side": side, "amount": str(INVEST_AMOUNT) } payload = json.dumps(body) headers = get_headers(API_KEY, API_SECRET, "POST", url, "", payload) res = requests.post(full_url, headers=headers, data=payload) print(f"سفارش {side}:", res.json())

---------------- اجرای ربات ------------------

def run_bot(): closes = fetch_klines() if len(closes) < EMA_SLOW + 1: print("داده کافی نیست") return

ema_fast = calculate_ema(closes, EMA_FAST)[-1]
ema_slow = calculate_ema(closes, EMA_SLOW)[-1]
rsi = calculate_rsi(closes, RSI_PERIOD)[-1]

print(f"EMA9: {ema_fast:.4f}, EMA21: {ema_slow:.4f}, RSI: {rsi:.2f}")

if ema_fast > ema_slow and rsi > 50:
    print("📈 شرایط خرید برقرار است")
    place_order("buy")
elif ema_fast < ema_slow:
    print("📉 سیگنال خروج / فروش")
    place_order("sell")
else:
    print("❌ هنوز شرایط مناسب نیست")

---------------- اجرای مداوم ------------------

if name == 'main': while True: try: run_bot() except Exception as e: print("خطا:", e) time.sleep(900)  # هر 15 دقیقه اجرا شود

