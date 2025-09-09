import asyncio
import datetime
import aiohttp
import sys
import os

from web3 import AsyncWeb3
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from config.config import ARBITRUM_RPC_URL, ARBISCAN_API_KEY, ETHERSCAN_ARBITRUM_API_ENDPOINT
from database.engine import get_db_session
from database.models import LabeledWallet, WalletFeature

w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(ARBITRUM_RPC_URL))


async def feature_collector():
    while True:
        try:
            print("Начинаю сбор данных")
            async with get_db_session() as db_session:
                queue = select(LabeledWallet).options(selectinload(LabeledWallet.features)).filter(LabeledWallet.features == None)
                result = await db_session.execute(queue)
                get_wallets = result.scalars().all()

                if not get_wallets:
                    print("Нет новых кошельков для обработки")
                else:
                    print(f"Вижу кошельки для обработки {len(get_wallets)}\n")

                    async with aiohttp.ClientSession() as http_session:
                        for wallet in get_wallets:
                            try:
                                print(f"Обработка кошелька: {wallet.address}")
                                checksum_address = w3.to_checksum_address(wallet.address)

                                tx_count = await w3.eth.get_transaction_count(checksum_address)
                                balance_wei = await w3.eth.get_balance(checksum_address)
                                balance_eth = w3.from_wei(balance_wei, 'ether')
                                first_tx_ts = await get_first_tx_timestamp(http_session, wallet.address)

                                wallet_age_days = 0
                                if first_tx_ts:
                                    first_tx_dt = datetime.datetime.fromtimestamp(first_tx_ts)
                                    wallet_age_days = (datetime.datetime.now() - first_tx_dt).days

                                new_features = WalletFeature(
                                    wallet_id=wallet.id,
                                    transaction_count=tx_count,
                                    wallet_age_days=wallet_age_days,
                                    balance_eth=balance_eth
                                )

                                db_session.add(new_features)
                                print("Признаки кошелька собраны\n")
                                await asyncio.sleep(0.3)

                            except Exception as n:
                                print(f"Ошибка при обработке кошелька {wallet.address}: {n}")

                        await db_session.commit()
                        print("Признаки добавлены в БД")

            await asyncio.sleep(300)  # Ставим сервис на паузу на 5 минут перед началом нового цикла

        except Exception as f:
            print(f"Произошла критическая ошибка {f}. Ждём 1 минуту")
            await asyncio.sleep(60)


async def get_first_tx_timestamp(session, address):
    params = {
        "module": "account",
        "action": "txlist",
        "address": address,
        "startblock": 0,
        "endblock": 99999999,
        "page": 1,
        "offset": 1,
        "sort": "asc",
        "apikey": ARBISCAN_API_KEY
    }

    try:
        async with session.get(ETHERSCAN_ARBITRUM_API_ENDPOINT, params=params) as response:
            response.raise_for_status()
            data = await response.json()

            if data["status"] == "1" and data["result"]:
                return int(data["result"][0]["timeStamp"])
            return None
    except Exception as e:
        print(f"Ошибка при запросе к API {e}")
        return None


if __name__ == "__main__":
    asyncio.run(feature_collector())