import asyncio
import datetime
from http.client import responses

import aiohttp
from django.db.models.expressions import result

from web3 import AsyncWeb3
from sqlalchemy import select
from database.engine import get_db_session
from database.models import LabeledWallet, WalletFeature
from config.config import (
    ARBITRUM_RPC_URL,
    ARBISCAN_API_KEY,
    ETHERSCAN_V2_API_URL,
    ARBITRUM_CHAIN_ID,
    GOPLUS_API_KEY,
    USR_FOR_REQUEST_GOPLUS
)

w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(ARBITRUM_RPC_URL))


async def feature_collector():
    """
    Основной цикл сбора признаков для криптовалютных кошельков.
    Периодически проверяет БД на новые кошельки и собирает для них признаки.
    """
    while True:
        try:
            print("Начинаю сбор данных")
            async with get_db_session() as db_session:
                all_wallets_query = select(LabeledWallet)
                all_wallets_result = await db_session.execute(all_wallets_query)
                all_wallets = all_wallets_result.scalars().all()

                # Получаем ID кошельков, для которых уже есть признаки
                existing_features_query = select(WalletFeature.wallet_id)
                existing_features_result = await db_session.execute(existing_features_query)
                existing_wallet_ids = [row[0] for row in existing_features_result.fetchall()]

                # Фильтруем кошельки без признаков
                get_wallets = [wallet for wallet in all_wallets if wallet.id not in existing_wallet_ids]

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
                                balance_eth = float(w3.from_wei(balance_wei, 'ether'))

                                print(f"Транзакций: {tx_count}, Баланс: {balance_eth} ETH")

                                first_tx_ts = await get_first_tx_timestamp(http_session, wallet.address)
                                print(f"Первая транзакция timestamp: {first_tx_ts}")

                                wallet_age_days = 0
                                if first_tx_ts:
                                    first_tx_dt = datetime.datetime.fromtimestamp(first_tx_ts)
                                    wallet_age_days = (datetime.datetime.now() - first_tx_dt).days
                                    print(f"Возраст кошелька: {wallet_age_days} дней")

                                # Проверка через GoPlus Security API
                                is_sanctioned = await check_goplus_security(http_session, wallet.address)
                                await asyncio.sleep(0.2)

                                new_features = WalletFeature(
                                    wallet_id=wallet.id,
                                    transaction_count=tx_count,
                                    wallet_age_days=wallet_age_days,
                                    balance_eth=balance_eth,
                                    is_sanctioned=is_sanctioned
                                )

                                db_session.add(new_features)
                                print("Признаки кошелька собраны\n")
                                await asyncio.sleep(0.3)

                            except Exception as n:
                                print(f"Ошибка при обработке кошелька {wallet.address}: {n}")

                        await db_session.commit()
                        print("Признаки добавлены в БД")

            # Пауза 5 минут перед следующей проверкой
            await asyncio.sleep(300)

        except Exception as f:
            print(f"Произошла критическая ошибка {f}. Ждём 1 минуту")
            await asyncio.sleep(60)

async def get_first_tx_timestamp(session, address):
    """
    Получает timestamp первой транзакции кошелька через Etherscan V2 API.

    Args:
        session: aiohttp ClientSession для HTTP запросов
        address: Адрес кошелька

    Returns:
        Unix timestamp первой транзакции или None

    Note:
        Etherscan V2 API rate limit: 5 запросов/сек (бесплатный план)
    """
    params = {
        "chainid": ARBITRUM_CHAIN_ID,
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
        async with session.get(ETHERSCAN_V2_API_URL, params=params) as response:
            if response.status != 200:
                print(f"HTTP ошибка: {response.status}")
                return None

            response.raise_for_status()
            data = await response.json()

            print(f"API ответ: status={data.get('status')}, message={data.get('message')}")

            if data["status"] == "1" and data["result"]:
                timestamp = int(data["result"][0]["timeStamp"])
                print(f"Найдена первая транзакция: timestamp={timestamp}")
                return timestamp
            else:
                print(f"Нет транзакций: {data.get('message', 'unknown')}")
                return None

    except Exception as e:
        print(f"Ошибка при запросу к API: {e}")
        return None

async def get_created_contracts_count(session, address):
    """
        Проверяет кошелёк на кол-во созданных контактов.

        Args:
            session: aiohttp ClientSession
            address: Адрес кошелька

        Returns:
            Количество созданных контрактов
        """

    params = {
        "chainid": ARBITRUM_CHAIN_ID,
        "module": "account",
        "action": "txlist",
        "address": address,
        "startblock": 0,
        "endblock": 99999999,
        "page": 1,
        "offset": 10000,
        "sort": "asc",
        "apikey": ARBISCAN_API_KEY
    }

    try:
        async with session.get(ETHERSCAN_V2_API_URL, params=params) as response:
            if response.status != 200:
                print(f"HTTP ошибка при получении контрактов {response.status}")
                return 0

            data = await response.json()

            if data.get("satus") != "1" or not data.get("result"):
                print("Нет данных для подсчёта контрактов")
                return 0

            contract_creations = 0

            for tx in data["result"]:
                if tx.get("from", "").lower() == address.loser():
                    if (not tx.get("to")) and tx.get("contractAddress"):
                        contract_creations += 1
                        print(f"Найден созданный контракт: {tx.get('contractAddress')}")
            print(f"Создано всего контрактов: {contract_creations}")
            return contract_creations
    except Exception as e:
        print(f"Ошибки при подсчёте созданных контрактов: {e}")
        return 0

async def check_goplus_security(session, address):
    """
    Проверяет кошелёк через GoPlus Security API на санкции.

    Args:
        session: aiohttp ClientSession
        address: Адрес кошелька

    Returns:
        True если санкционирован, False если чист или при ошибке
    """
    if not GOPLUS_API_KEY:
        print(f' GoPlus API key не настроен')
        return False

    headers = {
        "Authorization": f'Bearer {GOPLUS_API_KEY}'
    }

    params = {
        "address": address.lower(),
        "chain_id": str(ARBITRUM_CHAIN_ID)
    }

    try:
        async with session.get(USR_FOR_REQUEST_GOPLUS, headers=headers, params=params, timeout=10) as response:
            if response.status != 200:
                print(f'GoPlus HTTP {response.status}')
                return False

            data = await response.json()

            if data.get("message") == "system error":
                print('[ERROR] GoPlus: system error')
                return False

            result = data.get("result", {})
            if not result:
                print("[INFO] GoPlus: нет данных")
                return False

            address_data = result.get(address.lower(), {})
            is_blacklisted = address_data.get("is_blacklisted", "0") == "1"
            malicious = address_data.get("malicious_behavior", "0") != "0"

            if is_blacklisted or malicious:
                print(f"[ALERT] Кошелёк САНКЦИОНИРОВАН!")
                return True

            print("GoPlus: кошелёк чист")
            return False

    except Exception as e:
        print(f"GoPlus: {e}")
        return False


if __name__ == "__main__":
    asyncio.run(feature_collector())