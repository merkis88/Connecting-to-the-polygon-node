import httpx

from config.config import COINGECKO_URL

COINGECKO_API = COINGECKO_URL

async def get_eth_price():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(COINGECKO_API)
            response.raise_for_status()
            data = response.json() # Расшифровка json ответа в словарь
            price = data.get("ethereum", {}).get("usd")

            if price:
                return float(price)
            return None

    except Exception as e:
        print(f"Ошибка при получении цены ETH {e}")
        return None








