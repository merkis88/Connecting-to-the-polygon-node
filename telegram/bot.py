from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from config.config import BOT_TOKEN
from database.engine import get_db_session
from service.utils_wallet import add_wallet

dp = Dispatcher()

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.reply("Привет!\nЯ твой бот для мониторинга кошельков Arbitrum.\nПока я только учусь отвечать.")

@dp.message(Command("watch"))
async def watch_wallet(message: types.Message, command):
    if not command.args:
        await message.answer("Вы не указали адрес.\nПример: /watch 0xe592427a0aece92de3edee1f18e0157c05861564")
        return

    wallet_address = command.args
    user_id = message.from_user.id

    async with get_db_session() as session:
        status = await add_wallet(session, user_id, wallet_address)
    if status == "added":
        await message.answer(f"✅ Добавлен кошелёк: {wallet_address}")
    elif status == "exists":
        await message.answer(f"Кошелёк уже отслеживается: {wallet_address}")
    else:
        await message.answer("❌ Произошла внутренняя ошибка. Попробуйте позже.")
