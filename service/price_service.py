import httpx
import time

from sqlalchemy.sql.functions import current_time

from config.config import COINGECKO_URL

COINGECKO_API = COINGECKO_URL

cached_price = None
last_price_fetch_time = 0
cache_during_seconds = 60

async def get_eth_price():

    global cached_price, last_price_fetch_time
    current_time = time.time()

    if (current_time - last_price_fetch_time) < cache_during_seconds and cached_price is not None:
        print("-> Беру данные из кеша")
        return cached_price


    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(COINGECKO_API)
            response.raise_for_status()
            data = response.json() # Расшифровка json ответа в словарь
            price = data.get("ethereum", {}).get("usd")

            if price:
                cached_price = float(price)
                last_price_fetch_time = current_time
                return cached_price
        return None

    except Exception as e:
        print(f"Ошибка при получении цены ETH {e}")
        return None








