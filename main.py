import asyncio
import json
import websockets
from pyexpat.errors import messages


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

        print("Жду новые блоки")

        while True:
            message = await websocket.recv()
            data = json.loads(message)
            hex_block_number = data['params']['result']['number']
            block_number = int(hex_block_number, 16)
            print(f"Новый блок: {block_number}")

if __name__ == "__main__":
    asyncio.run(listen_new_blocks())




