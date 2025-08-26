import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command

# 👇 ВАШ ИМПОРТ - ВСЁ ПРАВИЛЬНО
from config.config import BOT_TOKEN

print(f"Проверяем токен... Заканчивается на: ...{BOT_TOKEN[-6:]}")

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# ✅ СРАЗУ ИСПОЛЬЗУЕМ ИМПОРТИРОВАННЫЙ ТОКЕН
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Этот хэндлер будет срабатывать на команду /start
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    """
    Этот хэндлер будет вызываться, когда пользователь отправляет команду `/start`
    """
    await message.reply("Привет!\nЯ твой бот для мониторинга кошельков Arbitrum.\nПока я только учусь отвечать.")

# Основная функция для запуска бота
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())