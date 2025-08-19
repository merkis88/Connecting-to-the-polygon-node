import asyncio
import json
import websockets
from adodbapi.apibase import identity
from pyexpat.errors import messages
from websockets.cli import print_over_input


async def listen_new_blocks():
    polygon_ws_url = "wss://polygon-mainnet.g.alchemy.com/v2/xKuI3iZT7t5-jCrIcbb3w"

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
                    transaction = block_details.get('transaction', [])
                    tr_count = len(transaction)
                    print(f"Количество транзакций в блоке: {tr_count}")

if __name__ == "__main__":
    asyncio.run(listen_new_blocks())




