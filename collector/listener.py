import asyncio
import json
import websockets

from config.config import ALCHEMY_WEBSOCKET_URL
from service.utils_blockchain import save_transactions_from_block, check_transactions_for_watched_wallets
from database.engine import get_db_session
from aiogram import Bot


async def listen_new_blocks(bot: Bot):
    async with websockets.connect(ALCHEMY_WEBSOCKET_URL) as websocket:
        print("✅ Соединение установлено!")

        await websocket.send(json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_subscribe",
            "params": ["newHeads"]
        }))
        await websocket.recv()

        print("\n Ожидаем новые блоки")
        while True:
            message = await websocket.recv()
            data = json.loads(message)

            if data.get("method") == "eth_subscription":
                block_header = data.get('params', {}).get('result', {})
                block_number_hex = block_header.get('number')
                if not block_number_hex:
                    continue

                print(f"\nНовый блок: {int(block_number_hex, 16)}")

                await websocket.send(json.dumps({
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "eth_getBlockByNumber",
                    "params": [block_number_hex, True]
                }))

            elif data.get("id") == 2:
                block_details = data.get('result')
                if block_details:
                    transactions = block_details.get('transactions', [])
                    tx_count = len(transactions)
                    print(f"  -> Получены детали. Транзакций в блоке: {tx_count}")

                    async with get_db_session() as session:
                        await save_transactions_from_block(session, block_details)
                        await check_transactions_for_watched_wallets(session, transactions, bot)
                else:
                    print("  -> Не удалось получить детали блока.")

