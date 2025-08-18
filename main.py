import asyncio

from web3 import AsyncWeb3

async def nuber_block():
    url_polygon = "https://polygon-rpc.com/"

    w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(url_polygon))

    check_connect = await w3.is_connected()

    if (check_connect):
        last_block = await w3.eth.block_number
        print(f"Номер последнего блока: {last_block}")
    else:
        print("Блок не найден")

if __name__ == "__main__":
    asyncio.run(nuber_block())
