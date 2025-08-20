import asyncio
from collector.listener import listen_new_blocks

if __name__ == "__main__":
    print("Запускаем сервис сбора данных...")
    asyncio.run(listen_new_blocks())


