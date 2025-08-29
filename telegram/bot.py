from aiogram import Router, F, types
from aiogram.filters.command import Command
from database.engine import get_db_session
from service.utils_wallet import add_wallet
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

router = Router()

class AddWallet(StatesGroup):
    waiting_name = State()
    waiting_address = State()

@router.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.reply("Привет!\nЯ твой бот для мониторинга кошельков Arbitrum.\nПока я только учусь отвечать.")

@router.message(Command("watch"))
async def start_add_wallet(message: types.Message, state: FSMContext):
    await state.set_state(AddWallet.waiting_name)
    await message.answer("💭 Придумайте название для отслеживаемого кошелька: ")

@router.message(AddWallet.waiting_name)
async def process_wallet_name(message, state: FSMContext):
    await state.update_data(wallet_name=message.text)

    await state.set_state(AddWallet.waiting_address)
    await message.answer("🫡 Принял. Теперь введите адрес который хотите отслеживать: ")

@router.message(AddWallet.waiting_address)
async def process_wallet_address(message, state: FSMContext):
    await state.update_data(wallet_address=message.text)

    user_data = await state.get_data()
    wallet_name = user_data['wallet_name']
    wallet_address = user_data['wallet_address']
    user_id = message.from_user.id

    async with get_db_session() as session:
        status = await add_wallet(session, user_id, wallet_address, wallet_name)

        if status == "added":
            await message.answer(f"✅ Добавлен кошелёк: **{wallet_name}** \n{wallet_address}")
        elif status == "exists":
            await message.answer(f"Кошелёк уже отслеживается: {wallet_name} \n{wallet_address}")
        else:
            await message.answer("❌ Произошла внутренняя ошибка. Попробуйте позже.")

        await state.clear()




