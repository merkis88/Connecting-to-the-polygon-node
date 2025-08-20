import asyncio
import json
import websockets

from config.config import ALCHEMY_WEBSOCKET_URL
from database.engine import get_db_session
from  database.service import save_transactions_from_block


async def listen_new_blocks():
    polygon_ws_url = ALCHEMY_WEBSOCKET_URL

    async with websockets.connect(polygon_ws_url) as websocket:
        print("Соединение установленно")

        await websocket.send(json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_subscribe",
            "params": ["newHeads"]
        }))

        await websocket.recv()
        print("Соединение установленно \n")

        print("Жду новые блоки")

        while True:
            message = await websocket.recv()
            data = json.loads(message)


            if data.get('method') == "eth_subscription":
                header_block = data['params']['result']
                block_number_hex = header_block['number']
                header_block_number = int(block_number_hex, 16)
                print(f"Новый блок: {header_block_number}\n")

                await websocket.send(json.dumps({
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "eth_getBlockByNumber",
                    "params": [block_number_hex, True]
                }))

            elif data.get('id') == 2:
                block_details = data.get('result')
                if block_details:
                    transactions = block_details.get('transaction', [])
                    tr_count = len(transactions)
                    print(f"Количество транзакций в блоке: {tr_count}")

                    async with get_db_session() as session:
                        await save_transactions_from_block(session, block_details)
                else:
                    print('Не удалось получить данные блока')





